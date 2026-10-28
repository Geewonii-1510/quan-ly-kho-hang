"""
Import Orders router - API phiếu nhập kho
Create import orders with transaction-safe inventory updates
Tạo phiếu nhập kho với cập nhật tồn kho an toàn bằng transaction
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime, timezone
from database import get_db
from models.user import User
from models.product import Product
from models.supplier import Supplier
from models.import_order import ImportOrder, ImportOrderDetail
from schemas.import_order import ImportOrderCreate, ImportOrderResponse
from services.auth_service import get_current_user, require_role
from services.inventory_service import increase_stock

router = APIRouter(prefix="/api/import-orders", tags=["Import Orders / Phiếu nhập kho"])


def _generate_import_code(db: Session) -> str:
    """Generate next import order code / Sinh mã phiếu nhập tiếp theo"""
    last = db.query(ImportOrder).order_by(ImportOrder.id.desc()).first()
    next_num = (last.id + 1) if last else 1
    return f"PN{next_num:06d}"


@router.get("/", response_model=List[ImportOrderResponse])
def get_import_orders(
    status_filter: Optional[str] = Query(None, alias="status"),
    supplier_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all import orders / Lấy danh sách phiếu nhập kho"""
    query = db.query(ImportOrder).options(
        joinedload(ImportOrder.supplier),
        joinedload(ImportOrder.created_by_user),
        joinedload(ImportOrder.details).joinedload(ImportOrderDetail.product),
    )

    if status_filter:
        query = query.filter(ImportOrder.status == status_filter)
    if supplier_id:
        query = query.filter(ImportOrder.supplier_id == supplier_id)

    orders = query.order_by(ImportOrder.created_at.desc()).all()

    result = []
    for order in orders:
        details = []
        for d in order.details:
            details.append({
                "id": d.id,
                "import_order_id": d.import_order_id,
                "product_id": d.product_id,
                "quantity": d.quantity,
                "unit_price": d.unit_price,
                "product_code": d.product.code if d.product else None,
                "product_name": d.product.name if d.product else None,
            })

        result.append(ImportOrderResponse(
            id=order.id,
            code=order.code,
            supplier_id=order.supplier_id,
            supplier_name=order.supplier.name if order.supplier else None,
            created_by=order.created_by,
            created_by_name=order.created_by_user.full_name if order.created_by_user else None,
            order_date=order.order_date,
            status=order.status,
            note=order.note,
            total_amount=order.total_amount or 0,
            created_at=order.created_at,
            details=details,
        ))

    return result


@router.get("/{order_id}", response_model=ImportOrderResponse)
def get_import_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get import order by ID / Lấy phiếu nhập theo ID"""
    order = db.query(ImportOrder).options(
        joinedload(ImportOrder.supplier),
        joinedload(ImportOrder.created_by_user),
        joinedload(ImportOrder.details).joinedload(ImportOrderDetail.product),
    ).filter(ImportOrder.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Không tìm thấy phiếu nhập / Import order not found")

    details = []
    for d in order.details:
        details.append({
            "id": d.id,
            "import_order_id": d.import_order_id,
            "product_id": d.product_id,
            "quantity": d.quantity,
            "unit_price": d.unit_price,
            "product_code": d.product.code if d.product else None,
            "product_name": d.product.name if d.product else None,
        })

    return ImportOrderResponse(
        id=order.id, code=order.code,
        supplier_id=order.supplier_id,
        supplier_name=order.supplier.name if order.supplier else None,
        created_by=order.created_by,
        created_by_name=order.created_by_user.full_name if order.created_by_user else None,
        order_date=order.order_date, status=order.status,
        note=order.note, total_amount=order.total_amount or 0,
        created_at=order.created_at, details=details,
    )


@router.post("/", response_model=ImportOrderResponse, status_code=status.HTTP_201_CREATED)
def create_import_order(
    data: ImportOrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "warehouse_keeper"))
):
    """
    Create import order and update inventory (transaction-safe)
    Tạo phiếu nhập kho và cập nhật tồn kho (an toàn transaction)
    """
    # Validate supplier / Kiểm tra nhà cung cấp
    supplier = db.query(Supplier).filter(Supplier.id == data.supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=400, detail="Nhà cung cấp không tồn tại / Supplier not found")

    if not data.details or len(data.details) == 0:
        raise HTTPException(status_code=400, detail="Phiếu nhập phải có ít nhất 1 sản phẩm / Must have at least 1 product")

    try:
        # Create order / Tạo phiếu nhập
        order_dt = data.order_date or datetime.now(timezone.utc)
        order = ImportOrder(
            code=_generate_import_code(db),
            supplier_id=data.supplier_id,
            created_by=current_user.id,
            order_date=order_dt,
            status="completed",
            note=data.note,
        )
        db.add(order)
        db.flush()

        total_amount = 0

        # Create details and update inventory / Tạo chi tiết và cập nhật tồn kho
        for detail_data in data.details:
            # Validate product / Kiểm tra sản phẩm
            product = db.query(Product).filter(Product.id == detail_data.product_id).first()
            if not product:
                raise HTTPException(
                    status_code=400,
                    detail=f"Sản phẩm ID={detail_data.product_id} không tồn tại / Product not found"
                )

            detail = ImportOrderDetail(
                import_order_id=order.id,
                product_id=detail_data.product_id,
                quantity=detail_data.quantity,
                unit_price=detail_data.unit_price,
            )
            db.add(detail)

            # Update inventory (transaction) / Cập nhật tồn kho (transaction)
            increase_stock(db, detail_data.product_id, detail_data.quantity)

            total_amount += detail_data.quantity * detail_data.unit_price

        order.total_amount = total_amount
        db.commit()
        db.refresh(order)

        return ImportOrderResponse(
            id=order.id, code=order.code,
            supplier_id=order.supplier_id,
            supplier_name=supplier.name,
            created_by=order.created_by,
            created_by_name=current_user.full_name,
            order_date=order.order_date,
            status=order.status,
            note=order.note,
            total_amount=order.total_amount,
            created_at=order.created_at,
            details=[],
        )

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi tạo phiếu nhập / Error creating import order: {str(e)}"
        )
