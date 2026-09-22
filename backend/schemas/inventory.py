"""
Inventory schemas - Schema Tồn kho
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class InventoryResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    last_updated: Optional[datetime] = None
    # Joined fields
    product_code: Optional[str] = None
    product_name: Optional[str] = None
    category_name: Optional[str] = None
    unit_name: Optional[str] = None
    min_stock: int = 0
    stock_status: str = "normal"  # normal / low / out_of_stock

    class Config:
        from_attributes = True


class InventoryAlert(BaseModel):
    """Low stock alert / Cảnh báo tồn kho thấp"""
    product_id: int
    product_code: str
    product_name: str
    current_stock: int
    min_stock: int
    shortage: int  # How many units below minimum / Thiếu bao nhiêu
