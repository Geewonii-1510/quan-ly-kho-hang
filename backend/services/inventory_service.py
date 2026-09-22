"""
Inventory service - Dịch vụ quản lý tồn kho
Transaction-safe inventory updates / Cập nhật tồn kho an toàn bằng transaction
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import HTTPException, status
from models.inventory import Inventory
from models.product import Product
from datetime import datetime, timezone


def get_or_create_inventory(db: Session, product_id: int) -> Inventory:
    """
    Get inventory record or create if not exists
    Lấy bản ghi tồn kho hoặc tạo mới nếu chưa có
    """
    inventory = db.query(Inventory).filter(
        Inventory.product_id == product_id
    ).first()

    if not inventory:
        inventory = Inventory(product_id=product_id, quantity=0)
        db.add(inventory)
        db.flush()

    return inventory


def increase_stock(db: Session, product_id: int, quantity: int) -> Inventory:
    """
    Increase stock for a product (used when importing)
    Tăng tồn kho cho sản phẩm (dùng khi nhập kho)

    Uses database transaction to ensure consistency
    Sử dụng transaction để đảm bảo tính nhất quán
    """
    if quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Số lượng phải lớn hơn 0 / Quantity must be greater than 0"
        )

    inventory = get_or_create_inventory(db, product_id)
    inventory.quantity += quantity
    inventory.last_updated = datetime.now(timezone.utc)
    db.flush()
    return inventory


def decrease_stock(db: Session, product_id: int, quantity: int) -> Inventory:
    """
    Decrease stock for a product (used when exporting)
    Giảm tồn kho cho sản phẩm (dùng khi xuất kho)

    Raises error if insufficient stock (prevents negative inventory)
    Báo lỗi nếu tồn kho không đủ (ngăn tồn kho âm)
    """
    if quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Số lượng phải lớn hơn 0 / Quantity must be greater than 0"
        )

    inventory = get_or_create_inventory(db, product_id)

    if inventory.quantity < quantity:
        product = db.query(Product).filter(Product.id == product_id).first()
        product_name = product.name if product else f"ID={product_id}"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Tồn kho không đủ cho '{product_name}': "
                f"hiện có {inventory.quantity}, yêu cầu xuất {quantity} / "
                f"Insufficient stock for '{product_name}': "
                f"current {inventory.quantity}, requested {quantity}"
            )
        )

    inventory.quantity -= quantity
    inventory.last_updated = datetime.now(timezone.utc)
    db.flush()
    return inventory


def get_low_stock_products(db: Session):
    """
    Get products with stock below minimum level
    Lấy danh sách sản phẩm có tồn kho dưới mức tối thiểu
    """
    results = (
        db.query(Product, Inventory)
        .outerjoin(Inventory, Product.id == Inventory.product_id)
        .filter(
            and_(
                Product.is_active == True,
                Product.min_stock > 0
            )
        )
        .all()
    )

    alerts = []
    for product, inventory in results:
        current_stock = inventory.quantity if inventory else 0
        if current_stock < product.min_stock:
            alerts.append({
                "product_id": product.id,
                "product_code": product.code,
                "product_name": product.name,
                "current_stock": current_stock,
                "min_stock": product.min_stock,
                "shortage": product.min_stock - current_stock,
            })

    return sorted(alerts, key=lambda x: x["shortage"], reverse=True)
