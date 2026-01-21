import os
import re
import requests
from PIL import Image

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def convert_google_drive(url: str) -> str:
    match = re.search(r"/d/([^/]+)/", url)
    if match:
        return f"https://drive.google.com/uc?export=download&id={match.group(1)}"

    match = re.search(r"id=([^&]+)", url)
    if match:
        return f"https://drive.google.com/uc?export=download&id={match.group(1)}"

    return url


def get_filename_from_response(response, default="image.jpg"):
    cd = response.headers.get("Content-Disposition", "")
    if "filename=" in cd:
        fname = cd.split("filename=")[-1].strip('"')
        return fname
    return default

def make_square(image_path, min_size=1080, fill_color=(0, 0, 0)):
    img = Image.open(image_path)
    w, h = img.size

    size = max(min_size, w, h)
    new_img = Image.new("RGB", (size, size), fill_color)

    new_img.paste(img, ((size - w) // 2, (size - h) // 2))
    new_img.save(image_path)
    
def download_image(url, folder="tmp_images"):
    folder_path = os.path.join(BASE_DIR, folder)
    os.makedirs(folder_path, exist_ok=True)

    url = convert_google_drive(url)
    print("🖼 Image download URL:", url)

    response = requests.get(url, allow_redirects=True, timeout=20)
    if response.status_code != 200:
        raise Exception(f"Image download failed: {response.status_code}")

    # 👉 LẤY TÊN FILE GỐC
    filename = get_filename_from_response(response)
    filename = filename.replace("/", "_")  # an toàn path

    full_path = os.path.join(folder_path, filename)

    content = response.content
    if not (content.startswith(b"\xff\xd8") or content.startswith(b"\x89PNG")):
        raise Exception("Downloaded file is not a valid image")

    with open(full_path, "wb") as f:
        f.write(content)

    make_square(full_path)
    return full_path
