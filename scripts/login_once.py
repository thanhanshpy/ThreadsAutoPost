# scripts/login_once.py
import os
import sys
from playwright.sync_api import sync_playwright

# ===== ADD ROOT PROJECT TO PYTHON PATH =====
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

from threads_bot import THREADS_PROFILE_DIR

if __name__ == "__main__":
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            THREADS_PROFILE_DIR,
            headless=False,   # 👈 BẮT BUỘC false để login
            viewport={"width": 1280, "height": 900},
        )

        page = ctx.new_page()
        page.goto("https://www.threads.net/login", wait_until="domcontentloaded")

        print("✅ Login Threads in the opened browser.")
        print("👉 Login xong thì quay lại terminal và nhấn ENTER.")
        input()

        ctx.close()
        print("✅ Saved session to threads_profile/")
