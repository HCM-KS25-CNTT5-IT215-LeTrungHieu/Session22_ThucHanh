# TrustBank Digital API

Ứng dụng ngân hàng số TrustBank Digital được viết bằng FastAPI và SQLAlchemy.
Hệ thống cung cấp chức năng xác thực qua JWT với cơ chế phân quyền (Customer / Admin), giao dịch chuyển tiền an toàn trong Transaction, và xử lý lỗi đồng nhất.

## 1. Yêu cầu hệ thống
- Python 3.10+
- `uv` (Khuyến nghị, dùng để quản lý môi trường và package)

## 2. Cài đặt và Chạy

### Cài đặt môi trường

Sử dụng `uv` để cài đặt dependencies tự động dựa trên `pyproject.toml`:
```bash
uv sync
```
Hoặc dùng pip (nếu không dùng uv):
```bash
pip install -r requirements.txt
```

### Thiết lập File cấu hình
Tạo file `.env` từ `.env.example`:
```bash
cp .env.example .env
```
Cấu hình thông tin trong file `.env` (ví dụ `JWT_SECRET`).

### Chạy Server
Sử dụng `fastapi run` hoặc chạy trực tiếp thông qua uv:
```bash
uv run fastapi run app/main.py --port 8000
```
Swagger UI (Tài liệu API) sẽ khả dụng tại: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## 3. Chạy Kiểm thử (Test Suite)
Dự án đi kèm bộ test (pytest) bao phủ toàn bộ luồng đăng ký, đăng nhập, JWT Role-based, và chuyển tiền có bắt lỗi giao dịch.
```bash
PYTHONPATH=. uv run pytest tests/
```

## 4. Kiến trúc
Dự án được viết theo cấu trúc Layered Architecture (Phân lớp), tinh gọn và không boilerplate thừa:
- `app/routes/`: Khai báo các API endpoints.
- `app/service/`: Xử lý logic nghiệp vụ, giao dịch (transaction) với DB.
- `app/core/`: Chứa config, file database, security (hash/JWT), dependencies (xác thực token), và hệ thống xử lý Exception (Centralized Exception).
- `app/models/`: Định nghĩa các table database.
- `app/schema/`: Khai báo các Pydantic model để serialize/validate dữ liệu vào ra.
