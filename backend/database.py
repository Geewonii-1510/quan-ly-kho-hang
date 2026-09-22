"""
Database configuration - Cấu hình cơ sở dữ liệu
SQLAlchemy engine & session for MySQL
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings

if "sqlite" in settings.DATABASE_URL:
    engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        echo=settings.DEBUG,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    Dependency to get DB session / Dependency để lấy DB session
    Used in FastAPI route handlers / Dùng trong các route handler
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Create all tables / Tạo tất cả các bảng
    Called on application startup / Gọi khi khởi động ứng dụng
    """
    from models import (  # noqa: F401
        user, product, supplier, inventory,
        import_order, export_order
    )
    Base.metadata.create_all(bind=engine)
