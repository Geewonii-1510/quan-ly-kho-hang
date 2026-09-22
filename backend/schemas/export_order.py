"""
Export Order schemas - Schema Phiếu xuất kho
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ExportOrderDetailCreate(BaseModel):
    product_id: int
    quantity: int
    reason: Optional[str] = None


class ExportOrderDetailResponse(BaseModel):
    id: int
    export_order_id: int
    product_id: int
    quantity: int
    reason: Optional[str] = None
    product_code: Optional[str] = None
    product_name: Optional[str] = None

    class Config:
        from_attributes = True


class ExportOrderCreate(BaseModel):
    recipient: str
    order_date: datetime
    note: Optional[str] = None
    details: List[ExportOrderDetailCreate]


class ExportOrderResponse(BaseModel):
    id: int
    code: str
    recipient: str
    created_by: int
    created_by_name: Optional[str] = None
    order_date: datetime
    status: str
    note: Optional[str] = None
    created_at: Optional[datetime] = None
    details: List[ExportOrderDetailResponse] = []

    class Config:
        from_attributes = True
