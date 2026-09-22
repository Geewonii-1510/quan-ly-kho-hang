"""
Suppliers router - API quản lý nhà cung cấp
CRUD for suppliers / CRUD nhà cung cấp
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models.supplier import Supplier
from models.user import User
from schemas.supplier import SupplierCreate, SupplierUpdate, SupplierResponse
from services.auth_service import get_current_user

router = APIRouter(prefix="/api/suppliers", tags=["Suppliers / Nhà cung cấp"])


@router.get("/", response_model=List[SupplierResponse])
def get_suppliers(
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all suppliers / Lấy danh sách nhà cung cấp"""
    query = db.query(Supplier)

    if search:
        query = query.filter(
            (Supplier.name.contains(search)) | (Supplier.code.contains(search))
        )
    if is_active is not None:
        query = query.filter(Supplier.is_active == is_active)

    return query.order_by(Supplier.code).all()


@router.get("/{supplier_id}", response_model=SupplierResponse)
def get_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get supplier by ID / Lấy nhà cung cấp theo ID"""
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Không tìm thấy NCC / Supplier not found")
    return supplier


@router.post("/", response_model=SupplierResponse)
def create_supplier(
    data: SupplierCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create supplier / Tạo nhà cung cấp mới"""
    if db.query(Supplier).filter(Supplier.code == data.code).first():
        raise HTTPException(status_code=400, detail="Mã NCC đã tồn tại / Supplier code exists")

    supplier = Supplier(**data.model_dump())
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return supplier


@router.put("/{supplier_id}", response_model=SupplierResponse)
def update_supplier(
    supplier_id: int,
    data: SupplierUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update supplier / Cập nhật nhà cung cấp"""
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Không tìm thấy NCC / Supplier not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(supplier, key, value)

    db.commit()
    db.refresh(supplier)
    return supplier


@router.delete("/{supplier_id}")
def delete_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Deactivate supplier / Vô hiệu hóa nhà cung cấp"""
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Không tìm thấy NCC / Supplier not found")

    supplier.is_active = False
    db.commit()
    return {"message": "Đã vô hiệu hóa NCC / Supplier deactivated"}
