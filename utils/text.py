import regex as re

def normalize_threads_content(text: str) -> str:
    if not text:
        return ""

    t = text.strip()

    # Chuẩn hoá khoảng trắng
    t = re.sub(r"\s{2,}", " ", t)

    # 🔥 Tách dòng TRƯỚC BẤT KỲ EMOJI NÀO
    # \p{Extended_Pictographic} = toàn bộ emoji Unicode
    t = re.sub(r"\s*(\p{Extended_Pictographic})", r"\n\1", t)

    # Tách câu hỏi thành 1 dòng riêng
    t = re.sub(r"(\?)\s+", r"\1\n", t)

    # Dọn dòng trống dư
    t = re.sub(r"\n{2,}", "\n", t)

    return t.strip()
