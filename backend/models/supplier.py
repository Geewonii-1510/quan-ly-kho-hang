"""
Supplier model - Mô hình Nhà cung cấp
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database import Base


class Supplier(Base):
    """
    Supplier / Nhà cung cấp
    """
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    contact_person = Column(String(100), comment="Người liên hệ / Contact person")
    phone = Column(String(20))
    email = Column(String(100))
    address = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    import_orders = relationship("ImportOrder", back_populates="supplier")

    def __repr__(self):
        return f"<Supplier(id={self.id}, code='{self.code}', name='{self.name}')>"
