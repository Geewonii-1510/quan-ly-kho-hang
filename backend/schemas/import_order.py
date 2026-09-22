"""
Import Order schemas - Schema Phiếu nhập kho
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ImportOrderDetailCreate(BaseModel):
    product_id: int
    quantity: int
    unit_price: float = 0


class ImportOrderDetailResponse(BaseModel):
    id: int
    import_order_id: int
    product_id: int
    quantity: int
    unit_price: float
    product_code: Optional[str] = None
    product_name: Optional[str] = None

    class Config:
        from_attributes = True


class ImportOrderCreate(BaseModel):
    supplier_id: int
    order_date: datetime
    note: Optional[str] = None
    details: List[ImportOrderDetailCreate]


class ImportOrderResponse(BaseModel):
    id: int
    code: str
    supplier_id: int
    supplier_name: Optional[str] = None
    created_by: int
    created_by_name: Optional[str] = None
    order_date: datetime
    status: str
    note: Optional[str] = None
    total_amount: float = 0
    created_at: Optional[datetime] = None
    details: List[ImportOrderDetailResponse] = []

    class Config:
        from_attributes = True
