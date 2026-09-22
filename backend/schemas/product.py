"""
Product schemas - Schema Sản phẩm
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# ---- Category / Danh mục ----

class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    id: int

    class Config:
        from_attributes = True


# ---- Unit / Đơn vị tính ----

class UnitBase(BaseModel):
    name: str
    abbreviation: str


class UnitCreate(UnitBase):
    pass


class UnitResponse(UnitBase):
    id: int

    class Config:
        from_attributes = True


# ---- Product / Sản phẩm ----

class ProductCreate(BaseModel):
    code: str
    name: str
    category_id: int
    unit_id: int
    min_stock: int = 0
    description: Optional[str] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category_id: Optional[int] = None
    unit_id: Optional[int] = None
    min_stock: Optional[int] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class ProductResponse(BaseModel):
    id: int
    code: str
    name: str
    category_id: int
    unit_id: int
    category: Optional[CategoryResponse] = None
    unit: Optional[UnitResponse] = None
    min_stock: int
    description: Optional[str] = None
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProductWithStock(ProductResponse):
    """Product with current stock info / Sản phẩm kèm thông tin tồn kho"""
    current_stock: int = 0
    stock_status: str = "normal"  # normal / low / out_of_stock
