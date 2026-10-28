"""
Pytest configuration & fixtures
Thiết lập database in-memory và client kiểm thử cho FastAPI
"""

import pytest
import sys
import os

# Thêm thư mục backend vào sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from main import app
from models.user import Role, User
from models.product import Category, Unit, Product
from models.supplier import Supplier
from models.inventory import Inventory
from services.auth_service import hash_password, create_access_token

# Sử dụng SQLite in-memory với StaticPool cho test đa luồng
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Thiết lập môi trường test"""
    os.environ["SECRET_KEY"] = "test-secret-key-for-unit-tests"


@pytest.fixture(scope="function")
def db_session():
    """Tạo mới toàn bộ bảng cho mỗi test case để đảm bảo tính độc lập"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()

    # Tạo dữ liệu cơ sở
    # 1. Roles
    admin_role = Role(id=1, name="admin", description="Admin")
    wh_role = Role(id=2, name="warehouse_keeper", description="Thủ kho")
    acc_role = Role(id=3, name="accountant", description="Kế toán")
    session.add_all([admin_role, wh_role, acc_role])
    session.flush()

    # 2. Users
    admin_user = User(
        id=1, username="admin_test", email="admin@test.vn",
        full_name="Quản Trị Viên Test", hashed_password=hash_password("123456"),
        role_id=1, is_active=True
    )
    wh_user = User(
        id=2, username="thuho_test", email="thuho@test.vn",
        full_name="Thủ Kho Test", hashed_password=hash_password("123456"),
        role_id=2, is_active=True
    )
    acc_user = User(
        id=3, username="ketoan_test", email="ketoan@test.vn",
        full_name="Kế Toán Test", hashed_password=hash_password("123456"),
        role_id=3, is_active=True
    )
    session.add_all([admin_user, wh_user, acc_user])
    session.flush()

    # 3. Category & Unit
    cat = Category(id=1, name="Phụ kiện", description="Mô tả phụ kiện")
    unit = Unit(id=1, name="Cái", abbreviation="cái")
    session.add_all([cat, unit])
    session.flush()

    # 4. Supplier
    supplier = Supplier(
        id=1, code="NCC_TEST", name="Công ty Cung Cấp Mẫu",
        contact_person="Nguyễn Văn A", phone="0901234567"
    )
    session.add(supplier)
    session.flush()

    # 5. Product với tồn kho ban đầu = 10, tồn tối thiểu = 5
    product = Product(
        id=1, code="HH001", name="Bàn phím cơ Test",
        category_id=1, unit_id=1, min_stock=5, is_active=True
    )
    session.add(product)
    session.flush()

    inv = Inventory(id=1, product_id=1, quantity=10)
    session.add(inv)
    session.commit()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """TestClient FastAPI với dependency override get_db"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def admin_headers(db_session):
    """Header xác thực quyền Admin"""
    token = create_access_token({"sub": "1"})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def warehouse_headers(db_session):
    """Header xác thực quyền Thủ kho (warehouse_keeper)"""
    token = create_access_token({"sub": "2"})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def accountant_headers(db_session):
    """Header xác thực quyền Kế toán (accountant)"""
    token = create_access_token({"sub": "3"})
    return {"Authorization": f"Bearer {token}"}
