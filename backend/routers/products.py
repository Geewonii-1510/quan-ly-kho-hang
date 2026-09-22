"""
Products router - API quản lý sản phẩm
CRUD for products, categories, units / CRUD sản phẩm, danh mục, đơn vị tính
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from database import get_db
from models.product import Product, Category, Unit
from models.inventory import Inventory
from models.user import User
from schemas.product import (
    ProductCreate, ProductUpdate, ProductResponse, ProductWithStock,
    CategoryCreate, CategoryResponse,
    UnitCreate, UnitResponse,
)
from services.auth_service import get_current_user

router = APIRouter(prefix="/api/products", tags=["Products / Sản phẩm"])


# ---- Categories / Danh mục ----

@router.get("/categories", response_model=List[CategoryResponse])
def get_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all categories / Lấy danh sách danh mục"""
    return db.query(Category).all()


@router.post("/categories", response_model=CategoryResponse)
def create_category(
    data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create category / Tạo danh mục mới"""
    if db.query(Category).filter(Category.name == data.name).first():
        raise HTTPException(status_code=400, detail="Danh mục đã tồn tại / Category exists")
    category = Category(**data.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


# ---- Units / Đơn vị tính ----

@router.get("/units", response_model=List[UnitResponse])
def get_units(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all units / Lấy danh sách đơn vị tính"""
    return db.query(Unit).all()


@router.post("/units", response_model=UnitResponse)
def create_unit(
    data: UnitCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create unit / Tạo đơn vị tính mới"""
    if db.query(Unit).filter(Unit.name == data.name).first():
        raise HTTPException(status_code=400, detail="Đơn vị tính đã tồn tại / Unit exists")
    unit = Unit(**data.model_dump())
    db.add(unit)
    db.commit()
    db.refresh(unit)
    return unit


# ---- Products / Sản phẩm ----

@router.get("/", response_model=List[ProductWithStock])
def get_products(
    search: Optional[str] = Query(None, description="Search by name or code"),
    category_id: Optional[int] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all products with stock info
    Lấy danh sách sản phẩm kèm thông tin tồn kho
    """
    query = db.query(Product).options(
        joinedload(Product.category),
        joinedload(Product.unit),
        joinedload(Product.inventory),
    )

    if search:
        query = query.filter(
            (Product.name.contains(search)) | (Product.code.contains(search))
        )
    if category_id:
        query = query.filter(Product.category_id == category_id)
    if is_active is not None:
        query = query.filter(Product.is_active == is_active)

    products = query.order_by(Product.code).all()

    result = []
    for p in products:
        current_stock = p.inventory.quantity if p.inventory else 0
        if current_stock <= 0:
            stock_status = "out_of_stock"
        elif current_stock < p.min_stock:
            stock_status = "low"
        else:
            stock_status = "normal"

        result.append(ProductWithStock(
            id=p.id, code=p.code, name=p.name,
            category_id=p.category_id, unit_id=p.unit_id,
            category=p.category, unit=p.unit,
            min_stock=p.min_stock, description=p.description,
            is_active=p.is_active, created_at=p.created_at,
            current_stock=current_stock,
            stock_status=stock_status,
        ))

    return result


@router.get("/{product_id}", response_model=ProductWithStock)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get product by ID / Lấy sản phẩm theo ID"""
    p = db.query(Product).options(
        joinedload(Product.category),
        joinedload(Product.unit),
        joinedload(Product.inventory),
    ).filter(Product.id == product_id).first()

    if not p:
        raise HTTPException(status_code=404, detail="Không tìm thấy sản phẩm / Product not found")

    current_stock = p.inventory.quantity if p.inventory else 0
    stock_status = "out_of_stock" if current_stock <= 0 else ("low" if current_stock < p.min_stock else "normal")

    return ProductWithStock(
        id=p.id, code=p.code, name=p.name,
        category_id=p.category_id, unit_id=p.unit_id,
        category=p.category, unit=p.unit,
        min_stock=p.min_stock, description=p.description,
        is_active=p.is_active, created_at=p.created_at,
        current_stock=current_stock, stock_status=stock_status,
    )


@router.post("/", response_model=ProductResponse)
def create_product(
    data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create product / Tạo sản phẩm mới"""
    if db.query(Product).filter(Product.code == data.code).first():
        raise HTTPException(status_code=400, detail="Mã sản phẩm đã tồn tại / Product code exists")

    product = Product(**data.model_dump())
    db.add(product)
    db.flush()

    # Create inventory record / Tạo bản ghi tồn kho
    inventory = Inventory(product_id=product.id, quantity=0)
    db.add(inventory)

    db.commit()
    db.refresh(product)
    return product


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update product / Cập nhật sản phẩm"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Không tìm thấy sản phẩm / Product not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(product, key, value)

    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Deactivate product / Vô hiệu hóa sản phẩm"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Không tìm thấy sản phẩm / Product not found")

    product.is_active = False
    db.commit()
    return {"message": "Đã vô hiệu hóa sản phẩm / Product deactivated"}
