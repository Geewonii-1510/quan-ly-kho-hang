"""
Unit & Integration Test: Nghiệp vụ Xuất kho và Ràng buộc chống Tồn kho âm
Kiểm thử: Ràng buộc tính nhất quán, rollback transaction khi không đủ hàng, ngăn chặn tồn âm
"""

import pytest
from models.inventory import Inventory
from models.product import Product


def test_create_export_order_success(client, warehouse_headers, db_session):
    """
    Test case 1: Xuất kho hợp lệ khi tồn kho đủ
    Tồn kho ban đầu: 10
    Xuất: 4
    Kỳ vọng: HTTP 201, tồn kho giảm còn 6
    """
    payload = {
        "recipient": "Công ty TNHH Khách Hàng A",
        "note": "Xuất bán theo đơn đặt hàng #001",
        "details": [
            {
                "product_id": 1,
                "quantity": 4,
                "reason": "Bán hàng"
            }
        ]
    }

    response = client.post("/api/export-orders/", json=payload, headers=warehouse_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["code"].startswith("PX")

    # Kiểm tra tồn kho sau khi xuất: 10 - 4 = 6
    inv = db_session.query(Inventory).filter(Inventory.product_id == 1).first()
    assert inv.quantity == 6


def test_negative_stock_prevention(client, warehouse_headers, db_session):
    """
    Test case 2: Cố tình xuất vượt quá số lượng tồn kho (Chặn tồn kho âm)
    Tồn kho hiện tại: 10
    Yêu cầu xuất: 25
    Kỳ vọng: HTTP 400 Bad Request, thông báo tồn kho không đủ, tồn kho giữ nguyên = 10
    """
    payload = {
        "recipient": "Khách hàng B",
        "note": "Cố tình xuất quá số lượng tồn",
        "details": [
            {
                "product_id": 1,
                "quantity": 25,  # Vượt quá tồn kho 10
                "reason": "Bán số lượng lớn"
            }
        ]
    }

    response = client.post("/api/export-orders/", json=payload, headers=warehouse_headers)
    assert response.status_code == 400
    detail = response.json()["detail"].lower()
    assert "tồn kho không đủ" in detail or "insufficient stock" in detail

    # Đảm bảo số lượng tồn kho KHÔNG bị âm và không bị thay đổi
    inv = db_session.query(Inventory).filter(Inventory.product_id == 1).first()
    assert inv.quantity == 10


def test_transaction_atomic_rollback(client, warehouse_headers, db_session):
    """
    Test case 3: Tính nguyên tử (Atomicity) của Transaction
    Tạo sản phẩm thứ 2 có tồn kho = 2.
    Đơn hàng xuất gồm 2 sản phẩm:
    - Sản phẩm 1: xuất 2 (hợp lệ vì tồn 10)
    - Sản phẩm 2: xuất 5 (không hợp lệ vì tồn chỉ có 2)
    Kỳ vọng: Báo lỗi 400 và ROLLBACK toàn bộ. Sản phẩm 1 KHÔNG bị trừ số lượng.
    """
    prod2 = Product(
        id=2, code="HH002", name="Chuột quang Test",
        category_id=1, unit_id=1, min_stock=2, is_active=True
    )
    db_session.add(prod2)
    db_session.flush()

    inv2 = Inventory(id=2, product_id=2, quantity=2)
    db_session.add(inv2)
    db_session.commit()

    payload = {
        "recipient": "Khách hàng C",
        "note": "Đơn hàng có 1 sản phẩm bị thiếu",
        "details": [
            {"product_id": 1, "quantity": 2, "reason": "Bán"},
            {"product_id": 2, "quantity": 5, "reason": "Bán thiếu hàng"}  # Thiếu hàng
        ]
    }

    response = client.post("/api/export-orders/", json=payload, headers=warehouse_headers)
    assert response.status_code == 400

    # Kiểm tra cả 2 sản phẩm đều được giữ nguyên số lượng tồn (Rollback thành công)
    inv1 = db_session.query(Inventory).filter(Inventory.product_id == 1).first()
    inv2_check = db_session.query(Inventory).filter(Inventory.product_id == 2).first()
    assert inv1.quantity == 10
    assert inv2_check.quantity == 2


def test_accountant_cannot_create_export_order(client, accountant_headers):
    """
    Test case 4: Kế toán cố tình tạo phiếu xuất
    Kỳ vọng: HTTP 403 Forbidden
    """
    payload = {
        "recipient": "Khách hàng D",
        "details": [{"product_id": 1, "quantity": 1, "reason": "Bán"}]
    }
    response = client.post("/api/export-orders/", json=payload, headers=accountant_headers)
    assert response.status_code == 403
