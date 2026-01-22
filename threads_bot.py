# threads_bot.py

import time
import random
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError
from utils.text import normalize_threads_content

THREADS_PROFILE_DIR = "threads_profile"
THREADS_URL = "https://www.threads.net"

POST_DELAY_RANGE = (3, 6)
AFTER_POST_DELAY = (5, 8)

MAX_RETRIES = 2


class ThreadsBot:
    def __init__(self, headless=True):
        self.headless = headless
        self.pw = None
        self.context = None
        self.page = None

    # =========================
    # START / STOP
    # =========================
    def start(self):
        self.pw = sync_playwright().start()

        self.context = self.pw.chromium.launch_persistent_context(
            THREADS_PROFILE_DIR,
            headless=self.headless,
            viewport={"width": 1280, "height": 900},
        )

        # ⏱ global timeouts (VERY IMPORTANT for CI)
        self.context.set_default_timeout(60000)
        self.context.set_default_navigation_timeout(60000)

        self.page = self.context.new_page()
        self.page.goto(THREADS_URL, wait_until="domcontentloaded")

        # 🚨 FAIL FAST: login wall / blocked UI
        self._assert_logged_in()

        print("✅ Threads browser ready")



    def close(self):
        if self.context:
            self.context.close()
        if self.pw:
            self.pw.stop()

    # =========================
    # POST ENTRYPOINT
    # =========================
    def post(self, text: str, image_path: str | None = None):
        text = normalize_threads_content(text)
        if not text.strip():
            raise ValueError("❌ Post content is empty")

        last_error = None

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                print(f"✍️ Posting attempt {attempt}/{MAX_RETRIES}")

                self._open_composer()
                self._type_text(text)

                if image_path:
                    self._upload_image(image_path)

                self._submit_post()

                time.sleep(random.uniform(*AFTER_POST_DELAY))

                post_url = self._confirm_posted(text)
                if not post_url:
                    raise Exception("Post not found on profile")

                print("✅ Post confirmed")
                return post_url

            except Exception as e:
                last_error = e
                print(f"⚠ Attempt {attempt} failed: {e}")

                self.page.screenshot(
                    path=f"debug_post_attempt_{attempt}.png",
                    full_page=True,
                )

                if attempt < MAX_RETRIES:
                    print("🔄 Retrying…")
                    self.page.reload(wait_until="domcontentloaded")
                    time.sleep(5)

        raise Exception(f"❌ All post attempts failed: {last_error}")

    # =========================
    # INTERNAL HELPERS
    # =========================
    def _assert_logged_in(self):
        """
        Fail fast if Threads shows login wall / blocked UI
        """
        time.sleep(3)

        if self.page.locator("text=Log in").count() > 0:
            self.page.screenshot(path="debug_not_logged_in.png", full_page=True)
            raise Exception("❌ Threads is not logged in (login wall detected)")

        if self.page.locator("text=Something went wrong").count() > 0:
            self.page.screenshot(path="debug_blocked.png", full_page=True)
            raise Exception("❌ Threads UI blocked")

    def _open_composer(self):
        try:
            # Force open compose page (most reliable)
            self.page.goto("https://www.threads.com/", wait_until="domcontentloaded")
            time.sleep(3)
            
            # Step 2: wait for the editor
            editor = self.page.wait_for_selector(
                #"div[contenteditable='true']",
                #timeout=60000
                "div[role='button']:has-text(\"What's new\")",
                timeout=60000
            )
            editor.click()
            time.sleep(random.uniform(*POST_DELAY_RANGE))
            
        except Exception:
            self.page.screenshot(
                path="debug_composer_failed.png",
                full_page=True
            )
            raise Exception("❌ Composer not available")

    def _type_text(self, text: str):
        self.page.keyboard.type(text, delay=20)
        time.sleep(random.uniform(*POST_DELAY_RANGE))

    def _upload_image(self, image_path: str):
        file_input = self.page.locator("input[type='file']").first
        file_input.set_input_files(image_path)
        time.sleep(5)  # wait for preview

    def _submit_post(self):
        # Ctrl+Enter
        self.page.keyboard.down("Control")
        self.page.keyboard.press("Enter")
        self.page.keyboard.up("Control")

        time.sleep(2)

        # fallback Enter
        self.page.keyboard.press("Enter")
        time.sleep(4)

    def _confirm_posted(self, text: str) -> str:
        username = self.get_profile_name()
        if not username:
            return ""

        self.page.goto(
            f"https://www.threads.net/{username}",
            wait_until="networkidle"
        )
        time.sleep(6)

        post_link = self.page.locator("a[href*='/post/']").first
        if post_link.count() == 0:
            return ""

        href = post_link.get_attribute("href")
        return f"https://www.threads.net{href}" if href.startswith("/") else href

    def get_profile_name(self) -> str:
        try:
            el = self.page.wait_for_selector(
                "a[href^='/@']",
                timeout=10000
            )
            return el.get_attribute("href").replace("/", "")
        except:
            return ""
