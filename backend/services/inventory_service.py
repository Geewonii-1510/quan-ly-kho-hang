"""
Inventory service - Dịch vụ quản lý tồn kho
Transaction-safe inventory updates / Cập nhật tồn kho an toàn bằng transaction
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, func
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


def get_stock_card(
    db: Session,
    product_id: int,
    start_date: datetime,
    end_date: datetime,
    supplier_id: int = None,
):
    """
    Get stock card / ledger for a specific product
    Tra cứu thẻ kho / lịch sử nhập xuất của một hàng hóa theo thời gian và nhà cung cấp
    """
    from models.product import Product, Category, Unit
    from models.import_order import ImportOrder, ImportOrderDetail
    from models.export_order import ExportOrder, ExportOrderDetail
    from models.supplier import Supplier
    from models.user import User

    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy sản phẩm / Product not found"
        )

    # 1. Tồn kho hiện tại
    inv = db.query(Inventory).filter(Inventory.product_id == product_id).first()
    current_stock = inv.quantity if inv else 0

    # 2. Tổng nhập và xuất sau thời điểm end_date (nếu end_date ở quá khứ)
    future_imports = (
        db.query(func.coalesce(func.sum(ImportOrderDetail.quantity), 0))
        .join(ImportOrder, ImportOrderDetail.import_order_id == ImportOrder.id)
        .filter(
            ImportOrderDetail.product_id == product_id,
            ImportOrder.status == "completed",
            ImportOrder.order_date > end_date,
        )
        .scalar() or 0
    )

    future_exports = (
        db.query(func.coalesce(func.sum(ExportOrderDetail.quantity), 0))
        .join(ExportOrder, ExportOrderDetail.export_order_id == ExportOrder.id)
        .filter(
            ExportOrderDetail.product_id == product_id,
            ExportOrder.status == "completed",
            ExportOrder.order_date > end_date,
        )
        .scalar() or 0
    )

    stock_at_end = current_stock - future_imports + future_exports

    # 3. Lấy tất cả giao dịch nhập trong kỳ
    import_query = (
        db.query(
            ImportOrderDetail.quantity,
            ImportOrderDetail.unit_price,
            ImportOrder.code.label("doc_code"),
            ImportOrder.order_date.label("trans_date"),
            ImportOrder.note,
            Supplier.name.label("partner_name"),
            Supplier.id.label("supplier_id"),
            User.full_name.label("creator_name"),
        )
        .join(ImportOrder, ImportOrderDetail.import_order_id == ImportOrder.id)
        .outerjoin(Supplier, ImportOrder.supplier_id == Supplier.id)
        .outerjoin(User, ImportOrder.created_by == User.id)
        .filter(
            ImportOrderDetail.product_id == product_id,
            ImportOrder.status == "completed",
            ImportOrder.order_date >= start_date,
            ImportOrder.order_date <= end_date,
        )
    )
    if supplier_id:
        import_query = import_query.filter(ImportOrder.supplier_id == supplier_id)

    import_rows = import_query.all()

    # 4. Lấy tất cả giao dịch xuất trong kỳ (nếu lọc theo supplier_id thì xuất không có supplier)
    export_rows = []
    if not supplier_id:
        export_query = (
            db.query(
                ExportOrderDetail.quantity,
                ExportOrderDetail.reason,
                ExportOrder.code.label("doc_code"),
                ExportOrder.order_date.label("trans_date"),
                ExportOrder.note,
                ExportOrder.recipient.label("partner_name"),
                User.full_name.label("creator_name"),
            )
            .join(ExportOrder, ExportOrderDetail.export_order_id == ExportOrder.id)
            .outerjoin(User, ExportOrder.created_by == User.id)
            .filter(
                ExportOrderDetail.product_id == product_id,
                ExportOrder.status == "completed",
                ExportOrder.order_date >= start_date,
                ExportOrder.order_date <= end_date,
            )
        )
        export_rows = export_query.all()

    # Tổng nhập / xuất trong kỳ
    period_import_qty = sum(r.quantity for r in import_rows)
    period_export_qty = sum(r.quantity for r in export_rows)

    # Tồn đầu kỳ = Tồn cuối kỳ - Nhập trong kỳ + Xuất trong kỳ
    opening_balance = stock_at_end - period_import_qty + period_export_qty

    # 5. Gộp và sắp xếp theo ngày tăng dần để tính tồn lũy kế
    all_events = []
    for r in import_rows:
        all_events.append({
            "date": r.trans_date,
            "document_code": r.doc_code,
            "order_type": "import",
            "partner_name": r.partner_name or "N/A",
            "quantity_in": r.quantity,
            "quantity_out": 0,
            "unit_price": float(r.unit_price or 0),
            "note": r.note,
            "created_by_name": r.creator_name,
        })

    for r in export_rows:
        all_events.append({
            "date": r.trans_date,
            "document_code": r.doc_code,
            "order_type": "export",
            "partner_name": r.partner_name or "Khách hàng / Xuất nội bộ",
            "quantity_in": 0,
            "quantity_out": r.quantity,
            "unit_price": 0.0,
            "note": r.note or r.reason,
            "created_by_name": r.creator_name,
        })

    # Sort theo ngày tăng dần
    all_events.sort(key=lambda x: x["date"])

    running_stock = opening_balance
    transactions = []
    for ev in all_events:
        running_stock = running_stock + ev["quantity_in"] - ev["quantity_out"]
        ev["balance"] = running_stock
        transactions.append(ev)

    category = db.query(Category).filter(Category.id == product.category_id).first()
    unit = db.query(Unit).filter(Unit.id == product.unit_id).first()

    return {
        "product_id": product.id,
        "product_code": product.code,
        "product_name": product.name,
        "unit_name": unit.name if unit else "",
        "category_name": category.name if category else "",
        "start_date": start_date,
        "end_date": end_date,
        "opening_balance": opening_balance,
        "total_import": period_import_qty,
        "total_export": period_export_qty,
        "closing_balance": running_stock,
        "transactions": transactions,
    }
