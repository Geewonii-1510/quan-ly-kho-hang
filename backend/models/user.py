"""
User & Role models - Mô hình Người dùng & Vai trò
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database import Base


class Role(Base):
    """
    Role model / Vai trò người dùng
    - admin: Quản trị viên / Administrator
    - warehouse_keeper: Thủ kho / Warehouse Keeper
    - accountant: Kế toán / Accountant
    """
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(200))

    # Relationships
    users = relationship("User", back_populates="role")

    def __repr__(self):
        return f"<Role(id={self.id}, name='{self.name}')>"


class User(Base):
    """
    User model / Người dùng hệ thống
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    role = relationship("Role", back_populates="users")
    import_orders = relationship("ImportOrder", back_populates="created_by_user")
    export_orders = relationship("ExportOrder", back_populates="created_by_user")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"
