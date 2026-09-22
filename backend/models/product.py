"""
Product, Category, Unit models - Mô hình Sản phẩm, Danh mục, Đơn vị tính
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database import Base


class Category(Base):
    """
    Product category / Danh mục sản phẩm
    """
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(255))

    # Relationships
    products = relationship("Product", back_populates="category")

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}')>"


class Unit(Base):
    """
    Unit of measurement / Đơn vị tính
    """
    __tablename__ = "units"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    abbreviation = Column(String(10), nullable=False)

    # Relationships
    products = relationship("Product", back_populates="unit")

    def __repr__(self):
        return f"<Unit(id={self.id}, name='{self.name}')>"


class Product(Base):
    """
    Product / Sản phẩm - Hàng hóa
    """
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    unit_id = Column(Integer, ForeignKey("units.id"), nullable=False)
    min_stock = Column(Integer, default=0, comment="Tồn tối thiểu / Minimum stock level")
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    category = relationship("Category", back_populates="products")
    unit = relationship("Unit", back_populates="products")
    inventory = relationship("Inventory", back_populates="product", uselist=False)
    import_details = relationship("ImportOrderDetail", back_populates="product")
    export_details = relationship("ExportOrderDetail", back_populates="product")

    def __repr__(self):
        return f"<Product(id={self.id}, code='{self.code}', name='{self.name}')>"
