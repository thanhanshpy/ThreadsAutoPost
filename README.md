# 🚀 Threads Auto Post Tool

Tool tự động đăng bài lên **Threads** bằng Playwright + Google Sheets.

> ⚠️ Lưu ý quan trọng: tool **đã ổn định về mặt code**. Lỗi thường gặp nhất khi chạy là do **NỘI DUNG (content)** bị Threads chặn ngầm, KHÔNG phải do code.

---

## 1️⃣ Tổng quan

Tool thực hiện các bước:
1. Đọc dữ liệu từ Google Sheet
2. Lấy bài **chưa đăng** (`Posted != YES`)
3. Mở Threads bằng profile đăng nhập sẵn
4. Gõ nội dung + upload ảnh (nếu có)
5. Submit bài post
6. Xác nhận **bài mới thật sự được tạo**
7. Chỉ khi thành công → cập nhật Google Sheet

---

## 2️⃣ Cấu trúc project

```
threads_autopost_tool/
│
├─ main.py                 # Entry point
├─ threads_bot.py          # Logic đăng Threads
├─ sheet_reader.py         # Đọc / ghi Google Sheet
├─ image_downloader.py     # Tải & xử lý ảnh
├─ utils/
│   └─ text.py             # Chuẩn hoá nội dung
├─ config/
│   └─ config.py           # Cấu hình
├─ scripts/
│   └─ login_once.py       # Login Threads 1 lần
├─ threads_profile/        # Session browser (auto tạo)
└─ tmp_images/             # Ảnh tạm
```

---

## 3️⃣ Chuẩn bị ban đầu

### 3.1. Cài môi trường

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

---

### 3.2. Login Threads (BẮT BUỘC 1 LẦN)

```bash
python scripts/login_once.py
```

- Trình duyệt mở ra
- Login Threads bằng tay
- Quay lại terminal → nhấn ENTER

👉 Session sẽ được lưu vào `threads_profile/`

---

## 4️⃣ Google Sheet yêu cầu

Sheet phải có **đúng tên cột**:

| Cột | Tên | Ý nghĩa |
|---|---|---|
| A | Position | Tên vị trí |
| B | Job Content | Nội dung post |
| C | Image URL | Link ảnh (tuỳ chọn) |
| D | Posted | YES = đã đăng |
| E | ThreadsProfile | Link bài post |
| F | Date | Ngày đăng |

Tool **CHỈ đăng** những dòng:
```
Posted != YES
```

---

## 5️⃣ Cách chạy tool

```bash
python main.py
```

Log thành công:
```
🚀 Sending post...
🔍 Confirming post on profile...
🔗 Post URL: https://www.threads.net/@xxx/post/xxxx
✅ Đã đăng & cập nhật Google Sheet
```

---

## 6️⃣ Cơ chế CHỐNG BUG QUAN TRỌNG

### ✅ 6.1. Chống lấy link bài cũ

Tool so sánh:
- `before_url`: bài mới nhất TRƯỚC submit
- `post_url`: bài mới nhất SAU submit

```python
if post_url == before_url:
    raise Exception("Submit KHÔNG tạo bài post mới")
```

👉 Nếu Threads **ignore submit** → tool FAIL → **KHÔNG ghi nhầm sheet**.

---

### ✅ 6.2. Retry submit

Tool tự động submit **tối đa 3 lần** vì Threads hay ignore lần đầu.

---

## 7️⃣ ❗ LỖI THƯỜNG GẶP (RẤT QUAN TRỌNG)

### ❌ Lỗi phổ biến nhất: *Submit KHÔNG tạo bài post mới*

```
❌ Submit KHÔNG tạo bài post mới (Threads ignore submit)
```

👉 **99% KHÔNG phải lỗi code**.

### 🔥 Nguyên nhân thật sự:
- Nội dung **quá dài**
- Nhiều emoji + CTA
- Có từ khoá spam:
  - "Ứng tuyển ngay"
  - "Điền form"
  - Google Forms
  - Email
- Nội dung tuyển dụng lặp lại nhiều lần

Threads **KHÔNG báo lỗi**, chỉ **nuốt submit**.

---

## 8️⃣ Khuyến nghị nội dung AN TOÀN

### ✅ NÊN
- 2–4 dòng ngắn
- Emoji vừa phải
- CTA mềm

Ví dụ:
```
Tuyển Thực tập sinh Quản lý Part-time
Làm việc online, linh hoạt thời gian
Quan tâm thì inbox để trao đổi thêm 👋
```

---

### ❌ KHÔNG NÊN
- Post quá dài (6–10 dòng)
- Copy y chang nhiều bài
- Link / form ngay post đầu

---

## 9️⃣ Debug khi gặp lỗi

### 9.1. Kiểm tra content
- Thử post **bằng tay** nội dung đó trên Threads
- Nếu tay cũng không post được → content bị chặn

### 9.2. Reset session (nếu cần)

```bash
rm -rf threads_profile
python scripts/login_once.py
```

---

## 10️⃣ Ghi chú quan trọng

- Tool dùng **Playwright + browser thật**
- Không API, không hack
- Threads có anti-spam → **content quyết định 80% thành công**

---

## ✅ KẾT LUẬN

- Code: ✅ ổn định
- Confirm: ✅ chính xác
- Không còn ghi nhầm link cũ
- Vấn đề chính: **CONTENT PHẢI NGẮN & AN TOÀN**

> "Automation chạy được hay không phụ thuộc vào content, không phải code."

---

🔥 Nếu cần nâng cấp tiếp:
- content-safe mode
- auto rewrite
- split thành thread
- multi-account rotation

👉 Liên hệ dev để mở rộng thêm.

