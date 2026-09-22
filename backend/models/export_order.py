"""
Export Order models - Mô hình Phiếu xuất kho
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database import Base


class ExportOrder(Base):
    """
    Export Order / Phiếu xuất kho
    """
    __tablename__ = "export_orders"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(30), unique=True, nullable=False, index=True,
                  comment="Mã phiếu xuất / Export order code")
    recipient = Column(String(200), nullable=False,
                       comment="Người nhận / Recipient")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    order_date = Column(DateTime, nullable=False,
                        comment="Ngày xuất / Export date")
    status = Column(String(20), default="completed",
                    comment="Trạng thái: pending/completed/cancelled")
    note = Column(Text, comment="Ghi chú / Notes")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    created_by_user = relationship("User", back_populates="export_orders")
    details = relationship("ExportOrderDetail", back_populates="export_order",
                           cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ExportOrder(id={self.id}, code='{self.code}')>"


class ExportOrderDetail(Base):
    """
    Export Order Detail / Chi tiết phiếu xuất kho
    """
    __tablename__ = "export_order_details"

    id = Column(Integer, primary_key=True, index=True)
    export_order_id = Column(Integer, ForeignKey("export_orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False,
                      comment="Số lượng xuất / Export quantity")
    reason = Column(String(255),
                    comment="Lý do xuất / Export reason")

    # Relationships
    export_order = relationship("ExportOrder", back_populates="details")
    product = relationship("Product", back_populates="export_details")

    def __repr__(self):
        return f"<ExportOrderDetail(order={self.export_order_id}, product={self.product_id}, qty={self.quantity})>"
