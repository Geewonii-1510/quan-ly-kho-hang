"""
Seed data - Dữ liệu mẫu
Populates database with sample data for demo
Thêm dữ liệu mẫu vào database để demo
"""

from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from models.user import Role, User
from models.product import Category, Unit, Product
from models.supplier import Supplier
from models.inventory import Inventory
from models.import_order import ImportOrder, ImportOrderDetail
from models.export_order import ExportOrder, ExportOrderDetail
from services.auth_service import hash_password
import random


def seed_database(db: Session):
    """
    Seed database with sample data / Thêm dữ liệu mẫu vào database
    Only runs if roles table is empty / Chỉ chạy khi bảng roles rỗng
    """
    # Check if already seeded / Kiểm tra đã có dữ liệu chưa
    if db.query(Role).count() > 0:
        print("✅ Dữ liệu đã tồn tại, bỏ qua seed / Data exists, skipping seed")
        return

    print("🌱 Đang thêm dữ liệu mẫu... / Seeding database...")

    # ---- Roles / Vai trò ----
    roles = [
        Role(id=1, name="admin", description="Quản trị viên / Administrator"),
        Role(id=2, name="warehouse_keeper", description="Thủ kho / Warehouse Keeper"),
        Role(id=3, name="accountant", description="Kế toán / Accountant"),
    ]
    db.add_all(roles)
    db.flush()

    # ---- Users / Người dùng ----
    users = [
        User(id=1, username="admin", email="admin@wms.vn", full_name="Quản trị viên",
             hashed_password=hash_password("123456"), role_id=1),
        User(id=2, username="thuho", email="thuho@wms.vn", full_name="Nguyễn Văn Kho",
             hashed_password=hash_password("123456"), role_id=2),
        User(id=3, username="ketoan", email="ketoan@wms.vn", full_name="Trần Thị Toán",
             hashed_password=hash_password("123456"), role_id=3),
    ]
    db.add_all(users)
    db.flush()

    # ---- Categories / Danh mục ----
    categories = [
        Category(id=1, name="Thiết bị IT / IT Equipment", description="Máy tính, laptop, màn hình"),
        Category(id=2, name="Văn phòng phẩm / Office Supplies", description="Giấy, bút, kẹp"),
        Category(id=3, name="Linh kiện điện tử / Electronic Components", description="RAM, SSD, CPU"),
        Category(id=4, name="Phụ kiện / Accessories", description="Chuột, bàn phím, tai nghe"),
        Category(id=5, name="Thiết bị mạng / Network Devices", description="Router, switch, cáp mạng"),
    ]
    db.add_all(categories)
    db.flush()

    # ---- Units / Đơn vị tính ----
    units = [
        Unit(id=1, name="Cái / Piece", abbreviation="cái"),
        Unit(id=2, name="Hộp / Box", abbreviation="hộp"),
        Unit(id=3, name="Bộ / Set", abbreviation="bộ"),
        Unit(id=4, name="Cuộn / Roll", abbreviation="cuộn"),
        Unit(id=5, name="Ram / Ream", abbreviation="ram"),
    ]
    db.add_all(units)
    db.flush()

    # ---- Products / Sản phẩm ----
    products_data = [
        # IT Equipment
        {"code": "HH001", "name": "Bàn phím cơ / Mechanical Keyboard", "cat": 4, "unit": 1, "min": 10},
        {"code": "HH002", "name": "Chuột không dây / Wireless Mouse", "cat": 4, "unit": 1, "min": 15},
        {"code": "HH003", "name": "Màn hình 24 inch / 24\" Monitor", "cat": 1, "unit": 1, "min": 5},
        {"code": "HH004", "name": "Laptop văn phòng / Office Laptop", "cat": 1, "unit": 1, "min": 3},
        # Components
        {"code": "HH005", "name": "RAM DDR4 8GB", "cat": 3, "unit": 1, "min": 20},
        {"code": "HH006", "name": "SSD 256GB", "cat": 3, "unit": 1, "min": 15},
        {"code": "HH007", "name": "SSD 512GB", "cat": 3, "unit": 1, "min": 10},
        {"code": "HH008", "name": "CPU Intel i5 / Intel i5 CPU", "cat": 3, "unit": 1, "min": 5},
        # Accessories
        {"code": "HH009", "name": "Tai nghe Bluetooth / Bluetooth Headset", "cat": 4, "unit": 1, "min": 10},
        {"code": "HH010", "name": "Webcam HD", "cat": 4, "unit": 1, "min": 8},
        {"code": "HH011", "name": "Cáp HDMI 1.5m / HDMI Cable 1.5m", "cat": 4, "unit": 1, "min": 20},
        {"code": "HH012", "name": "Bộ sạc USB-C / USB-C Charger", "cat": 4, "unit": 1, "min": 15},
        # Office
        {"code": "HH013", "name": "Giấy A4 / A4 Paper", "cat": 2, "unit": 5, "min": 50},
        {"code": "HH014", "name": "Bút bi xanh / Blue Pen", "cat": 2, "unit": 2, "min": 30},
        {"code": "HH015", "name": "Kẹp giấy / Paper Clips", "cat": 2, "unit": 2, "min": 20},
        # Network
        {"code": "HH016", "name": "Router WiFi 6 / WiFi 6 Router", "cat": 5, "unit": 1, "min": 5},
        {"code": "HH017", "name": "Switch 8 cổng / 8-Port Switch", "cat": 5, "unit": 1, "min": 5},
        {"code": "HH018", "name": "Cáp mạng Cat6 / Cat6 Cable", "cat": 5, "unit": 4, "min": 10},
    ]

    products = []
    for p in products_data:
        prod = Product(
            code=p["code"], name=p["name"],
            category_id=p["cat"], unit_id=p["unit"],
            min_stock=p["min"],
        )
        products.append(prod)
        db.add(prod)
    db.flush()

    # ---- Suppliers / Nhà cung cấp ----
    suppliers = [
        Supplier(id=1, code="NCC001", name="Công ty TNHH Phong Vũ / Phong Vu Co., Ltd.",
                 contact_person="Nguyễn Minh", phone="028-7300-6100",
                 email="sales@phongvu.vn", address="123 Nguyễn Thị Minh Khai, Q.1, TP.HCM"),
        Supplier(id=2, code="NCC002", name="Công ty CP An Phát / An Phat Corp.",
                 contact_person="Trần Hùng", phone="024-3825-6789",
                 email="info@anphat.vn", address="456 Trần Đại Nghĩa, Hai Bà Trưng, Hà Nội"),
        Supplier(id=3, code="NCC003", name="Công ty TNHH Thế Giới Di Động / MWG Co., Ltd.",
                 contact_person="Lê Thảo", phone="1800-1060",
                 email="b2b@mwg.vn", address="789 Lê Văn Lương, Q.7, TP.HCM"),
        Supplier(id=4, code="NCC004", name="Công ty CP Văn phòng phẩm Hồng Hà / Hong Ha Office",
                 contact_person="Phạm Lan", phone="024-3633-1122",
                 email="sales@hongha.vn", address="321 Phạm Văn Đồng, Cầu Giấy, Hà Nội"),
        Supplier(id=5, code="NCC005", name="Công ty TNHH Mạng Máy Tính / Network Computer Co., Ltd.",
                 contact_person="Hoàng Nam", phone="028-3920-5500",
                 email="order@netcomp.vn", address="654 Điện Biên Phủ, Bình Thạnh, TP.HCM"),
    ]
    db.add_all(suppliers)
    db.flush()

    # ---- Initial inventory / Tồn kho ban đầu ----
    initial_stocks = [50, 40, 12, 8, 5, 18, 7, 6, 25, 15, 35, 22, 80, 45, 30, 10, 8, 12]
    inventories = []
    for i, prod in enumerate(products):
        inv = Inventory(product_id=prod.id, quantity=initial_stocks[i])
        inventories.append(inv)
        db.add(inv)
    db.flush()

    # ---- Sample Import Orders / Phiếu nhập mẫu ----
    now = datetime.now(timezone.utc)
    import_orders_data = [
        {"days_ago": 60, "supplier_id": 1, "items": [(0, 30, 350000), (1, 25, 250000), (2, 10, 4500000)]},
        {"days_ago": 45, "supplier_id": 2, "items": [(4, 50, 800000), (5, 30, 600000), (6, 20, 1100000)]},
        {"days_ago": 30, "supplier_id": 3, "items": [(8, 20, 450000), (9, 15, 650000)]},
        {"days_ago": 20, "supplier_id": 4, "items": [(12, 100, 65000), (13, 50, 5000), (14, 40, 15000)]},
        {"days_ago": 15, "supplier_id": 5, "items": [(15, 10, 1200000), (16, 8, 800000), (17, 15, 45000)]},
        {"days_ago": 7, "supplier_id": 1, "items": [(0, 20, 350000), (3, 5, 12000000)]},
        {"days_ago": 5, "supplier_id": 2, "items": [(4, 30, 800000), (7, 10, 4500000)]},
        {"days_ago": 3, "supplier_id": 3, "items": [(1, 15, 250000), (10, 20, 80000)]},
        {"days_ago": 1, "supplier_id": 1, "items": [(5, 25, 600000), (11, 30, 200000)]},
    ]

    for idx, io_data in enumerate(import_orders_data):
        order = ImportOrder(
            code=f"PN{idx + 1:06d}",
            supplier_id=io_data["supplier_id"],
            created_by=2,  # thuho
            order_date=now - timedelta(days=io_data["days_ago"]),
            status="completed",
            note=f"Phiếu nhập mẫu #{idx + 1} / Sample import #{idx + 1}",
        )
        db.add(order)
        db.flush()

        total = 0
        for prod_idx, qty, price in io_data["items"]:
            detail = ImportOrderDetail(
                import_order_id=order.id,
                product_id=products[prod_idx].id,
                quantity=qty,
                unit_price=price,
            )
            db.add(detail)
            total += qty * price

        order.total_amount = total

    # ---- Sample Export Orders / Phiếu xuất mẫu ----
    export_orders_data = [
        {"days_ago": 55, "recipient": "Phòng IT - Chi nhánh HCM / IT Dept - HCM Branch",
         "items": [(0, 10, "Cấp phát thiết bị"), (1, 8, "Cấp phát thiết bị")]},
        {"days_ago": 40, "recipient": "Phòng Kỹ thuật / Engineering Dept",
         "items": [(4, 15, "Nâng cấp máy"), (5, 10, "Nâng cấp máy")]},
        {"days_ago": 25, "recipient": "Phòng Hành chính / Admin Dept",
         "items": [(12, 30, "Bổ sung VP phẩm"), (13, 20, "Bổ sung VP phẩm")]},
        {"days_ago": 18, "recipient": "Khách hàng ABC / Customer ABC",
         "items": [(2, 5, "Bán hàng"), (8, 8, "Bán hàng")]},
        {"days_ago": 10, "recipient": "Phòng IT - Chi nhánh HN / IT Dept - HN Branch",
         "items": [(0, 25, "Cấp phát đợt 2"), (1, 15, "Cấp phát đợt 2"), (3, 3, "Cấp phát laptop")]},
        {"days_ago": 6, "recipient": "Phòng Kỹ thuật / Engineering Dept",
         "items": [(7, 8, "Lắp ráp máy mới"), (6, 5, "Lắp ráp máy mới")]},
        {"days_ago": 2, "recipient": "Phòng Hành chính / Admin Dept",
         "items": [(14, 15, "Bổ sung VP phẩm"), (12, 20, "Bổ sung VP phẩm")]},
    ]

    for idx, eo_data in enumerate(export_orders_data):
        order = ExportOrder(
            code=f"PX{idx + 1:06d}",
            recipient=eo_data["recipient"],
            created_by=2,
            order_date=now - timedelta(days=eo_data["days_ago"]),
            status="completed",
            note=f"Phiếu xuất mẫu #{idx + 1} / Sample export #{idx + 1}",
        )
        db.add(order)
        db.flush()

        for prod_idx, qty, reason in eo_data["items"]:
            detail = ExportOrderDetail(
                export_order_id=order.id,
                product_id=products[prod_idx].id,
                quantity=qty,
                reason=reason,
            )
            db.add(detail)

    db.commit()
    print("✅ Đã thêm dữ liệu mẫu thành công! / Seed data created successfully!")
    print("   📋 3 users: admin/thuho/ketoan (password: 123456)")
    print("   📦 18 sản phẩm / products")
    print("   🏢 5 nhà cung cấp / suppliers")
    print("   📥 9 phiếu nhập / import orders")
    print("   📤 7 phiếu xuất / export orders")
