"""
Unit & Integration Test: Tra cứu Thẻ kho & Lịch sử biến động
Kiểm thử: Tra cứu theo hàng hóa, thời gian, nhà cung cấp, tính lũy kế tồn kho
"""

import pytest
from datetime import datetime, timezone, timedelta


def test_stock_card_full_lifecycle(client, warehouse_headers):
    """
    Test case 1: Tạo 1 chu trình nhập - xuất và kiểm tra thẻ kho
    1. Nhập thêm 20 cái
    2. Xuất đi 8 cái
    3. Tra cứu thẻ kho sản phẩm HH001
    Kỳ vọng: Thẻ kho ghi nhận đầy đủ 2 giao dịch, số dư đầu kỳ, tổng nhập, tổng xuất và tồn cuối kỳ khớp 100%
    """
    # 1. Nhập 20
    import_payload = {
        "supplier_id": 1,
        "note": "Nhập đợt A",
        "details": [{"product_id": 1, "quantity": 20, "unit_price": 400000.0}]
    }
    res_import = client.post("/api/import-orders/", json=import_payload, headers=warehouse_headers)
    assert res_import.status_code == 201

    # 2. Xuất 8
    export_payload = {
        "recipient": "Khách A",
        "note": "Giao đợt 1",
        "details": [{"product_id": 1, "quantity": 8, "reason": "Bán lẻ"}]
    }
    res_export = client.post("/api/export-orders/", json=export_payload, headers=warehouse_headers)
    assert res_export.status_code == 201

    # 3. Tra cứu thẻ kho
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    res_card = client.get(
        f"/api/inventory/stock-card?product_id=1&start_date={today}&end_date={today}",
        headers=warehouse_headers
    )
    assert res_card.status_code == 200
    card_data = res_card.json()

    assert card_data["product_code"] == "HH001"
    assert card_data["total_import"] == 20
    assert card_data["total_export"] == 8
    # Ban đầu là 10, nhập 20 = 30, xuất 8 = 22
    assert card_data["closing_balance"] == 22
    assert len(card_data["transactions"]) == 2

    # Giao dịch 1 là nhập 20, tồn lũy kế = 30
    assert card_data["transactions"][0]["order_type"] == "import"
    assert card_data["transactions"][0]["quantity_in"] == 20
    assert card_data["transactions"][0]["balance"] == 30

    # Giao dịch 2 là xuất 8, tồn lũy kế = 22
    assert card_data["transactions"][1]["order_type"] == "export"
    assert card_data["transactions"][1]["quantity_out"] == 8
    assert card_data["transactions"][1]["balance"] == 22


def test_stock_card_filter_by_supplier(client, warehouse_headers):
    """
    Test case 2: Lọc thẻ kho theo nhà cung cấp cụ thể
    """
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    res = client.get(
        f"/api/inventory/stock-card?product_id=1&supplier_id=1&start_date={today}&end_date={today}",
        headers=warehouse_headers
    )
    assert res.status_code == 200
    data = res.json()
    assert data["product_id"] == 1
