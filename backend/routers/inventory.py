"""
Inventory router - API tồn kho
View inventory and alerts / Xem tồn kho và cảnh báo
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from database import get_db
from models.product import Product, Category
from models.inventory import Inventory
from models.user import User
from schemas.inventory import InventoryResponse, InventoryAlert
from services.auth_service import get_current_user
from services.inventory_service import get_low_stock_products

router = APIRouter(prefix="/api/inventory", tags=["Inventory / Tồn kho"])


@router.get("/", response_model=List[InventoryResponse])
def get_inventory(
    search: Optional[str] = Query(None),
    category_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all inventory records / Lấy danh sách tồn kho
    """
    query = (
        db.query(Product, Inventory)
        .outerjoin(Inventory, Product.id == Inventory.product_id)
        .filter(Product.is_active == True)
    )

    if search:
        query = query.filter(
            (Product.name.contains(search)) | (Product.code.contains(search))
        )
    if category_id:
        query = query.filter(Product.category_id == category_id)

    results = query.order_by(Product.code).all()

    inventory_list = []
    for product, inventory in results:
        qty = inventory.quantity if inventory else 0
        if qty <= 0:
            stock_status = "out_of_stock"
        elif qty < product.min_stock:
            stock_status = "low"
        else:
            stock_status = "normal"

        category = db.query(Category).filter(Category.id == product.category_id).first()

        inventory_list.append(InventoryResponse(
            id=inventory.id if inventory else 0,
            product_id=product.id,
            quantity=qty,
            last_updated=inventory.last_updated if inventory else None,
            product_code=product.code,
            product_name=product.name,
            category_name=category.name if category else "",
            unit_name=product.unit.name if product.unit else "",
            min_stock=product.min_stock,
            stock_status=stock_status,
        ))

    return inventory_list


@router.get("/alerts", response_model=List[InventoryAlert])
def get_inventory_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get low stock alerts / Lấy cảnh báo tồn kho thấp
    """
    return get_low_stock_products(db)
