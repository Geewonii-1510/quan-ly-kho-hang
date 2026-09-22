"""
Application configuration - Cấu hình ứng dụng
Loads settings from .env file / Đọc cấu hình từ file .env
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App / Ứng dụng
    APP_NAME: str = "WMS - Warehouse Management System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Database / Cơ sở dữ liệu MySQL
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "wms_user"
    DB_PASSWORD: str = "wms_password"
    DB_NAME: str = "wms_db"

    @property
    def DATABASE_URL(self) -> str:
        if self.DB_HOST and self.DB_HOST not in ("localhost", "127.0.0.1"):
            return (
                f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@"
                f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"
            )
        return "sqlite:///./wms_db.sqlite"

    # JWT Authentication / Xác thực JWT
    SECRET_KEY: str = "wms-secret-key-change-in-production-2024"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 hours / 8 giờ

    # AI - Google Gemini
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-3.6-flash"

    # CORS
    CORS_ORIGINS: str = (
        "http://localhost:5173,http://localhost:3000,"
        "http://127.0.0.1:5173,http://127.0.0.1:3000"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
