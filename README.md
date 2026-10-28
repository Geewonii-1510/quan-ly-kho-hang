# WMS - Hệ thống Quản lý Kho hàng tích hợp AI
# AI-integrated Warehouse Management System

## 📋 Giới thiệu / Introduction

Hệ thống quản lý kho hàng toàn diện cho doanh nghiệp nhỏ, tích hợp AI (Google Gemini) để sinh báo cáo, gợi ý nhập hàng và phát hiện bất thường.

A comprehensive warehouse management system for small businesses, integrated with AI (Google Gemini) for report generation, restock suggestions, and anomaly detection.

## 🛠 Công nghệ / Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | Python, FastAPI, SQLAlchemy |
| Frontend | React, Vite, Chart.js |
| Database | MySQL 8.0 |
| AI Engine | Google Gemini API |
| Container | Docker, Docker Compose |

## 🚀 Cách chạy / How to Run

### Cách 1: Docker (Khuyến nghị / Recommended)

```bash
# 1. Thêm Gemini API key / Add Gemini API key
# Lấy key miễn phí tại / Get free key at: https://aistudio.google.com/apikey
export GEMINI_API_KEY=your_api_key_here

# 2. Chạy Docker Compose / Run Docker Compose
docker-compose up -d

# 3. Mở trình duyệt / Open browser
# http://localhost:3000
```

### Cách 2: Chạy thủ công / Manual Setup

**Backend:**
```bash
cd backend
pip install -r requirements.txt

# Sửa file .env - thêm thông tin MySQL và Gemini API key
# Edit .env - add MySQL credentials and Gemini API key

python main.py
# Server chạy tại / Server runs at: http://localhost:8000
# API docs tại / API docs at: http://localhost:8000/docs
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
# App chạy tại / App runs at: http://localhost:5173
```

## 👤 Tài khoản demo / Demo Accounts

| Username | Password | Vai trò / Role |
|----------|----------|----------------|
| admin | 123456 | Quản trị viên / Administrator |
| thuho | 123456 | Thủ kho / Warehouse Keeper |
| ketoan | 123456 | Kế toán / Accountant |

## 📦 Tính năng / Features

### Quản lý cốt lõi / Core WMS
- ✅ Đăng nhập & phân quyền chặt chẽ (JWT & RBAC: Admin, Thủ kho, Kế toán)
- ✅ Quản lý sản phẩm, danh mục, đơn vị tính / Products, categories, units
- ✅ Quản lý nhà cung cấp / Supplier management
- ✅ Phiếu nhập kho (tự động cập nhật tồn bằng transaction)
- ✅ Phiếu xuất kho (kiểm tra tồn trước khi xuất, ngăn chặn tồn kho âm)
- ✅ Tồn kho thời gian thực / Real-time inventory
- ✅ Cảnh báo hàng dưới tồn tối thiểu / Low stock alerts
- ✅ **Thẻ kho & Tra cứu lịch sử nhập xuất theo hàng hóa, thời gian, NCC / Stock Card & Ledger**
- ✅ **Báo cáo nhập xuất tồn & Xuất file CSV (Excel) / Export Reports**
- ✅ Dashboard thống kê trực quan / Statistics dashboard

### AI tích hợp / AI Features (Google Gemini)
- 🤖 Sinh báo cáo nhập xuất tồn tự động theo kỳ / Auto-generate inventory reports
- 🤖 Gợi ý nhập hàng thông minh (dựa trên tồn kho, tồn tối thiểu, tốc độ xuất)
- 🤖 Phát hiện biến động bất thường (xuất đột biến, hàng tồn lâu)
- 🤖 Bảo mật dữ liệu nhạy cảm: Không gửi đơn giá mua trong prompt AI

### Kiểm thử tự động / Automated Testing
```bash
# Chạy toàn bộ 13 test cases (nhập, xuất, tồn âm, thẻ kho, báo cáo AI)
python -m pytest backend/tests -v
```

📖 **Tài liệu SDLC & Minh chứng dùng AI 4 giai đoạn:** Xem tại [`docs/SDLC_MINH_CHUNG_AI_DE_TAI_07.md`](docs/SDLC_MINH_CHUNG_AI_DE_TAI_07.md)

## 📁 Cấu trúc dự án / Project Structure

```
HT Qly kho hang/
├── backend/
│   ├── main.py              # FastAPI entry point
│   ├── config.py            # Configuration
│   ├── database.py          # SQLAlchemy setup
│   ├── seed_data.py         # Sample data
│   ├── models/              # ORM models
│   ├── schemas/             # Pydantic schemas
│   ├── routers/             # API endpoints
│   ├── services/            # Business logic
│   ├── ai/                  # AI module (Gemini)
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/             # API client
│   │   ├── contexts/        # Auth context
│   │   ├── components/      # Reusable components
│   │   └── pages/           # Page components
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
└── README.md
```
