"""
WMS Backend - Main application entry point
Ứng dụng Backend chính của Hệ thống Quản lý Kho hàng
"""

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from database import init_db, SessionLocal
from seed_data import seed_database

# Import all routers / Import tất cả routers
from routers import auth, users, products, suppliers, inventory
from routers import import_orders, export_orders, reports, ai

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Hệ thống Quản lý Kho hàng tích hợp AI / "
        "AI-integrated Warehouse Management System"
    ),
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS configuration / Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers / Đăng ký các router
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(products.router)
app.include_router(suppliers.router)
app.include_router(inventory.router)
app.include_router(import_orders.router)
app.include_router(export_orders.router)
app.include_router(reports.router)
app.include_router(ai.router)


@app.on_event("startup")
def startup_event():
    """
    Application startup / Khởi động ứng dụng
    - Create tables / Tạo bảng
    - Seed data / Thêm dữ liệu mẫu
    """
    print("🚀 Khởi động WMS Backend... / Starting WMS Backend...")
    init_db()
    print("✅ Database tables created / Đã tạo bảng database")

    # Seed sample data / Thêm dữ liệu mẫu
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()


@app.get("/", tags=["Root"])
def root():
    """Health check / Kiểm tra trạng thái"""
    return {
        "message": "WMS Backend is running / WMS Backend đang hoạt động",
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }


@app.get("/api/health", tags=["Root"])
def health_check():
    """API health check / Kiểm tra API"""
    return {"status": "ok", "message": "API hoạt động bình thường / API is healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
