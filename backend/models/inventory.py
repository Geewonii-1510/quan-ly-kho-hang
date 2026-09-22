"""
Inventory model - Mô hình Tồn kho
"""

from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database import Base


class Inventory(Base):
    """
    Inventory / Tồn kho
    Tracks current stock quantity for each product
    Theo dõi số lượng tồn kho hiện tại cho mỗi sản phẩm
    """
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), unique=True, nullable=False)
    quantity = Column(Integer, default=0, nullable=False,
                      comment="Số lượng tồn kho / Current stock quantity")
    last_updated = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                          onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    product = relationship("Product", back_populates="inventory")

    def __repr__(self):
        return f"<Inventory(product_id={self.product_id}, quantity={self.quantity})>"
