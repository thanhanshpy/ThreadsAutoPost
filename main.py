# main.py
import os
import sys
import traceback

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(ROOT_DIR)

from threads_bot import ThreadsBot
from sheet_reader import get_unposted_rows, mark_posted
from image_downloader import download_image
from utils.text import normalize_threads_content
from config.config import (
    COL_POSITION,
    COL_CONTENT,
    COL_IMAGE,
    MAX_POSTS_PER_RUN,
)


def run():
    print("🚀 START THREADS AUTO POST")

    bot = ThreadsBot(headless=True)

    try:
        bot.start()

        rows = get_unposted_rows(limit=MAX_POSTS_PER_RUN)

        if not rows:
            print("🎉 Không có bài nào cần đăng.")
            return

        print(f"📄 Tìm thấy {len(rows)} bài chưa đăng")

        for item in rows:
            row_index = item["row_index"]
            data = item["data"]

            position = data.get(COL_POSITION, "").strip()
            content = data.get(COL_CONTENT, "").strip()
            image_url = data.get(COL_IMAGE, "").strip()

            print("=" * 60)
            print(f"📌 POSITION: {position}")
            print(f"📍 ROW INDEX: {row_index}")

            if not content:
                print("⚠ Job Content trống → SKIP")
                continue

            image_path = None

            if image_url:
                # Có Image URL → BẮT BUỘC tải ảnh
                try:
                    image_path = download_image(image_url)
                except Exception as e:
                    raise Exception(f"❌ Có Image URL nhưng tải ảnh thất bại: {e}")

            post_url = bot.post(text=content, image_path=image_path)

            print(f"🔗 Post URL: {post_url}")
            mark_posted(row_index=row_index, threads_profile=post_url)

            # 🔁 XOÁ ẢNH LOCAL SAU KHI POST THÀNH CÔNG
            if image_path and os.path.exists(image_path):
                try:
                    os.remove(image_path)
                    print(f"🗑 Deleted local image: {image_path}")
                except Exception as e:
                    print(f"⚠ Không xoá được ảnh local: {e}")

            print("✅ Đã đăng & cập nhật Google Sheet")

        print("🎯 HOÀN TẤT CHẠY TOOL")

    except Exception as e:
        print("❌ TOOL FAILED")
        print(str(e))
        traceback.print_exc()

    finally:
        bot.close()
        print("🛑 ThreadsBot closed")


if __name__ == "__main__":
    run()
