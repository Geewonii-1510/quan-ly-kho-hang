"""
Import Order models - Mô hình Phiếu nhập kho
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database import Base


class ImportOrder(Base):
    """
    Import Order / Phiếu nhập kho
    """
    __tablename__ = "import_orders"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(30), unique=True, nullable=False, index=True,
                  comment="Mã phiếu nhập / Import order code")
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    order_date = Column(DateTime, nullable=False,
                        comment="Ngày nhập / Import date")
    status = Column(String(20), default="completed",
                    comment="Trạng thái: pending/completed/cancelled")
    note = Column(Text, comment="Ghi chú / Notes")
    total_amount = Column(Float, default=0,
                          comment="Tổng tiền / Total amount")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    supplier = relationship("Supplier", back_populates="import_orders")
    created_by_user = relationship("User", back_populates="import_orders")
    details = relationship("ImportOrderDetail", back_populates="import_order",
                           cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ImportOrder(id={self.id}, code='{self.code}')>"


class ImportOrderDetail(Base):
    """
    Import Order Detail / Chi tiết phiếu nhập kho
    """
    __tablename__ = "import_order_details"

    id = Column(Integer, primary_key=True, index=True)
    import_order_id = Column(Integer, ForeignKey("import_orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False,
                      comment="Số lượng nhập / Import quantity")
    unit_price = Column(Float, default=0,
                        comment="Đơn giá / Unit price")

    # Relationships
    import_order = relationship("ImportOrder", back_populates="details")
    product = relationship("Product", back_populates="import_details")

    @property
    def line_total(self):
        """Thành tiền / Line total"""
        return self.quantity * self.unit_price

    def __repr__(self):
        return f"<ImportOrderDetail(order={self.import_order_id}, product={self.product_id}, qty={self.quantity})>"
