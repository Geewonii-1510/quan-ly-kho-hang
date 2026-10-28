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


class StockCardTransaction(BaseModel):
    """Chi tiết từng giao dịch trong thẻ kho / Stock card transaction item"""
    date: datetime
    document_code: str
    order_type: str  # "import" hoặc "export"
    partner_name: Optional[str] = None  # Nhà cung cấp hoặc Người nhận
    quantity_in: int = 0
    quantity_out: int = 0
    balance: int = 0  # Số tồn lũy kế
    unit_price: Optional[float] = 0.0
    note: Optional[str] = None
    created_by_name: Optional[str] = None


class StockCardResponse(BaseModel):
    """Báo cáo Thẻ kho của một sản phẩm / Stock card report for a product"""
    product_id: int
    product_code: str
    product_name: str
    unit_name: Optional[str] = None
    category_name: Optional[str] = None
    start_date: datetime
    end_date: datetime
    opening_balance: int = 0
    total_import: int = 0
    total_export: int = 0
    closing_balance: int = 0
    transactions: list[StockCardTransaction] = []
