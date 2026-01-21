# threads_bot.py
import time
import random
from pathlib import Path
from playwright.sync_api import sync_playwright
from utils.text import normalize_threads_content
THREADS_PROFILE_DIR = "threads_profile"
THREADS_URL = "https://www.threads.net"

POST_DELAY_RANGE = (3, 6)
AFTER_POST_DELAY = (5, 8)


class ThreadsBot:
    def __init__(self, headless=True):
        self.headless = headless
        self.pw = None
        self.context = None
        self.page = None

    def start(self):
        self.pw = sync_playwright().start()

        self.context = self.pw.chromium.launch_persistent_context(
            THREADS_PROFILE_DIR,
            headless=self.headless,
            viewport={"width": 1280, "height": 900},
        )

        self.page = self.context.new_page()
        self.page.goto(THREADS_URL, wait_until="domcontentloaded")

        print("ℹ Threads browser opened (login check deferred)")

    def close(self):
        if self.context:
            self.context.close()
        if self.pw:
            self.pw.stop()

    def _is_logged_in(self) -> bool:
        try:
            self.page.goto("https://www.threads.net", wait_until="networkidle")
            self.page.wait_for_selector(
                "div[role='button']:has-text(\"What's new\")",
                timeout=20000
            )
            return True
        except:
            return False

    def post(self, text: str, image_path: str | None = None):
        text = normalize_threads_content(text)

        if not text.strip():
            raise ValueError("❌ Nội dung bài post trống")

        self._open_composer()
        self._type_text(text)
        time.sleep(2)

        if image_path:
            self._upload_image(image_path)

        print("🚀 Sending post...")
        self._submit_post()

        print("🔍 Confirming post on profile...")
        post_url = self._confirm_posted(text)
        if not post_url:
            self.page.screenshot(path="debug_post_not_found.png", full_page=True)
            raise Exception("❌ Post KHÔNG xuất hiện trên Threads profile")

        return post_url

    def get_profile_name(self) -> str:
        try:
            el = self.page.wait_for_selector("a[href^='/@']", timeout=5000)
            return el.get_attribute("href").replace("/", "")
        except:
            return ""

    def get_latest_post_url(self) -> str:
        """
        Lấy link bài post mới nhất trên Threads profile
        """
        username = self.get_profile_name()
        if not username:
            return ""

        # vào profile
        self.page.goto(f"https://www.threads.net/{username}", wait_until="networkidle")
        self.page.wait_for_timeout(5000)

        # bài post đầu tiên
        post_link = self.page.locator("a[href*='/post/']").first

        if post_link.count() == 0:
            return ""

        href = post_link.get_attribute("href")

        # chuẩn hoá link
        if href.startswith("/"):
            return f"https://www.threads.net{href}"

        return href

    def _open_composer(self):
        box = self.page.wait_for_selector(
            'div[aria-label="Empty text field. Type to compose a new post."]',
            timeout=20000
        )
        box.click()
        time.sleep(random.uniform(*POST_DELAY_RANGE))

    def _type_text(self, text: str):
        # Sau khi click box, focus đã nằm trong editor
        self.page.keyboard.type(text, delay=20)
        time.sleep(random.uniform(*POST_DELAY_RANGE))

    def _confirm_posted(self, text: str) -> str:
        """
        Confirm post bằng profile
        Trả về URL bài post nếu tìm thấy, ngược lại trả ""
        """
        username = self.get_profile_name()
        if not username:
            return ""

        # vào profile
        self.page.goto(f"https://www.threads.net/{username}", wait_until="networkidle")
        self.page.wait_for_timeout(8000)

        snippet = text[:30].replace("🚀", "").replace("✨", "").strip()

        # tìm bài có snippet
        post = self.page.locator(f"text={snippet}").first
        if post.count() == 0:
            return ""

        # lấy link bài post mới nhất
        link = self.page.locator("a[href*='/post/']").first
        if link.count() == 0:
            return ""

        href = link.get_attribute("href")
        return f"https://www.threads.net{href}" if href.startswith("/") else href

    def _upload_image(self, image_path: str):
        if not image_path:
            return

        file_input = self.page.locator("input[type='file']").first

        # KHÔNG wait visible
        file_input.set_input_files(image_path)

        # đợi Threads load preview
        self.page.wait_for_timeout(5000)

    def _submit_post(self):
        # thử Ctrl+Enter trước
        self.page.keyboard.down("Control")
        self.page.keyboard.press("Enter")
        self.page.keyboard.up("Control")

        time.sleep(1)

        # fallback: Enter thường
        self.page.keyboard.press("Enter")

        # đợi Threads xử lý
        time.sleep(4)