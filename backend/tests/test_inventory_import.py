"""
Unit & Integration Test: Nghiệp vụ Nhập kho
Kiểm thử: Tạo phiếu nhập, tự động tăng tồn kho bằng transaction, phân quyền người dùng
"""

import pytest
from models.inventory import Inventory
from models.import_order import ImportOrder


def test_create_import_order_success(client, warehouse_headers, db_session):
    """
    Test case 1: Thủ kho lập phiếu nhập hợp lệ
    Kỳ vọng: HTTP 201, tạo phiếu thành công, tồn kho tăng tương ứng
    """
    payload = {
        "supplier_id": 1,
        "note": "Nhập hàng bổ sung đợt 1",
        "details": [
            {
                "product_id": 1,
                "quantity": 15,
                "unit_price": 500000.0
            }
        ]
    }

    response = client.post("/api/import-orders/", json=payload, headers=warehouse_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["code"].startswith("PN")
    assert data["total_amount"] == 15 * 500000.0

    # Kiểm tra tồn kho trong database: ban đầu 10 + nhập 15 = 25
    inv = db_session.query(Inventory).filter(Inventory.product_id == 1).first()
    assert inv.quantity == 25


def test_create_import_order_invalid_product(client, warehouse_headers):
    """
    Test case 2: Nhập sản phẩm không tồn tại
    Kỳ vọng: HTTP 400 Bad Request
    """
    payload = {
        "supplier_id": 1,
        "note": "Nhập hàng lỗi",
        "details": [
            {
                "product_id": 9999,
                "quantity": 10,
                "unit_price": 100000.0
            }
        ]
    }

    response = client.post("/api/import-orders/", json=payload, headers=warehouse_headers)
    assert response.status_code == 400
    assert "không tồn tại" in response.json()["detail"].lower()


def test_accountant_cannot_create_import_order(client, accountant_headers):
    """
    Test case 3: Kế toán cố tình lập phiếu nhập kho
    Kỳ vọng: HTTP 403 Forbidden (chỉ Quản trị viên và Thủ kho mới có quyền lập phiếu)
    """
    payload = {
        "supplier_id": 1,
        "note": "Kế toán lập phiếu trái thẩm quyền",
        "details": [
            {
                "product_id": 1,
                "quantity": 5,
                "unit_price": 200000.0
            }
        ]
    }

    response = client.post("/api/import-orders/", json=payload, headers=accountant_headers)
    assert response.status_code == 403
