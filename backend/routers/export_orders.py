"""
Export Orders router - API phiếu xuất kho
Create export orders with stock validation
Tạo phiếu xuất kho với kiểm tra tồn kho
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime
from database import get_db
from models.user import User
from models.product import Product
from models.export_order import ExportOrder, ExportOrderDetail
from schemas.export_order import ExportOrderCreate, ExportOrderResponse
from services.auth_service import get_current_user
from services.inventory_service import decrease_stock

router = APIRouter(prefix="/api/export-orders", tags=["Export Orders / Phiếu xuất kho"])


def _generate_export_code(db: Session) -> str:
    """Generate next export order code / Sinh mã phiếu xuất tiếp theo"""
    last = db.query(ExportOrder).order_by(ExportOrder.id.desc()).first()
    next_num = (last.id + 1) if last else 1
    return f"PX{next_num:06d}"


@router.get("/", response_model=List[ExportOrderResponse])
def get_export_orders(
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all export orders / Lấy danh sách phiếu xuất kho"""
    query = db.query(ExportOrder).options(
        joinedload(ExportOrder.created_by_user),
        joinedload(ExportOrder.details).joinedload(ExportOrderDetail.product),
    )

    if status_filter:
        query = query.filter(ExportOrder.status == status_filter)

    orders = query.order_by(ExportOrder.created_at.desc()).all()

    result = []
    for order in orders:
        details = []
        for d in order.details:
            details.append({
                "id": d.id,
                "export_order_id": d.export_order_id,
                "product_id": d.product_id,
                "quantity": d.quantity,
                "reason": d.reason,
                "product_code": d.product.code if d.product else None,
                "product_name": d.product.name if d.product else None,
            })

        result.append(ExportOrderResponse(
            id=order.id, code=order.code,
            recipient=order.recipient,
            created_by=order.created_by,
            created_by_name=order.created_by_user.full_name if order.created_by_user else None,
            order_date=order.order_date,
            status=order.status, note=order.note,
            created_at=order.created_at, details=details,
        ))

    return result


@router.get("/{order_id}", response_model=ExportOrderResponse)
def get_export_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get export order by ID / Lấy phiếu xuất theo ID"""
    order = db.query(ExportOrder).options(
        joinedload(ExportOrder.created_by_user),
        joinedload(ExportOrder.details).joinedload(ExportOrderDetail.product),
    ).filter(ExportOrder.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Không tìm thấy phiếu xuất / Export order not found")

    details = []
    for d in order.details:
        details.append({
            "id": d.id,
            "export_order_id": d.export_order_id,
            "product_id": d.product_id,
            "quantity": d.quantity,
            "reason": d.reason,
            "product_code": d.product.code if d.product else None,
            "product_name": d.product.name if d.product else None,
        })

    return ExportOrderResponse(
        id=order.id, code=order.code,
        recipient=order.recipient,
        created_by=order.created_by,
        created_by_name=order.created_by_user.full_name if order.created_by_user else None,
        order_date=order.order_date,
        status=order.status, note=order.note,
        created_at=order.created_at, details=details,
    )


@router.post("/", response_model=ExportOrderResponse, status_code=status.HTTP_201_CREATED)
def create_export_order(
    data: ExportOrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create export order and decrease inventory (transaction-safe)
    Tạo phiếu xuất kho và giảm tồn kho (an toàn transaction)
    Raises error if insufficient stock / Báo lỗi nếu tồn kho không đủ
    """
    if not data.details or len(data.details) == 0:
        raise HTTPException(status_code=400, detail="Phiếu xuất phải có ít nhất 1 sản phẩm / Must have at least 1 product")

    try:
        # Create order / Tạo phiếu xuất
        order = ExportOrder(
            code=_generate_export_code(db),
            recipient=data.recipient,
            created_by=current_user.id,
            order_date=data.order_date,
            status="completed",
            note=data.note,
        )
        db.add(order)
        db.flush()

        # Create details and update inventory / Tạo chi tiết và cập nhật tồn kho
        for detail_data in data.details:
            product = db.query(Product).filter(Product.id == detail_data.product_id).first()
            if not product:
                raise HTTPException(
                    status_code=400,
                    detail=f"Sản phẩm ID={detail_data.product_id} không tồn tại / Product not found"
                )

            # Check and decrease stock (will raise if insufficient)
            # Kiểm tra và giảm tồn kho (sẽ báo lỗi nếu không đủ)
            decrease_stock(db, detail_data.product_id, detail_data.quantity)

            detail = ExportOrderDetail(
                export_order_id=order.id,
                product_id=detail_data.product_id,
                quantity=detail_data.quantity,
                reason=detail_data.reason,
            )
            db.add(detail)

        db.commit()
        db.refresh(order)

        return ExportOrderResponse(
            id=order.id, code=order.code,
            recipient=order.recipient,
            created_by=order.created_by,
            created_by_name=current_user.full_name,
            order_date=order.order_date,
            status=order.status, note=order.note,
            created_at=order.created_at, details=[],
        )

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi tạo phiếu xuất / Error creating export order: {str(e)}"
        )
