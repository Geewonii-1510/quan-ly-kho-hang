"""
Report schemas - Schema Báo cáo
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class DashboardStats(BaseModel):
    """Dashboard statistics / Thống kê Dashboard"""
    total_products: int = 0
    total_suppliers: int = 0
    total_import_today: int = 0
    total_export_today: int = 0
    low_stock_count: int = 0
    total_inventory_value: float = 0


class InventorySummaryItem(BaseModel):
    """Inventory summary per product / Tổng hợp tồn kho theo sản phẩm"""
    product_id: int
    product_code: str
    product_name: str
    category_name: str
    opening_stock: int = 0
    total_imported: int = 0
    total_exported: int = 0
    closing_stock: int = 0
    min_stock: int = 0


class InventoryReport(BaseModel):
    """Full inventory report / Báo cáo nhập xuất tồn"""
    period_start: datetime
    period_end: datetime
    items: List[InventorySummaryItem] = []
    total_imported: int = 0
    total_exported: int = 0


class ChartData(BaseModel):
    """Chart data for frontend / Dữ liệu biểu đồ"""
    labels: List[str] = []
    import_data: List[int] = []
    export_data: List[int] = []


class AIReportRequest(BaseModel):
    """Request to AI for report / Yêu cầu AI sinh báo cáo"""
    report_type: str  # "inventory_report" | "restock_suggestion" | "anomaly_detection"
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None


class AIReportResponse(BaseModel):
    """AI generated report / Báo cáo AI sinh"""
    report_type: str
    content: str
    generated_at: datetime


class ChatMessage(BaseModel):
    """Chat message / Tin nhắn chat"""
    role: str  # "user" hoặc "model"
    content: str


class AIChatRequest(BaseModel):
    """Request to AI chat / Yêu cầu chat với AI"""
    message: str
    history: Optional[List[ChatMessage]] = []


class AIChatResponse(BaseModel):
    """AI chat response / Phản hồi chat từ AI"""
    reply: str
    generated_at: datetime
