"""
Unit & Integration Test: Báo cáo AI & Tổng hợp Dữ liệu cho LLM
Kiểm thử: Dữ liệu rỗng, Xuất tăng bất thường, Cảnh báo tồn tối thiểu, Bảo mật dữ liệu nhạy cảm (không gửi giá mua)
"""

import pytest
from datetime import datetime, timezone, timedelta
from services.report_service import get_inventory_data_for_ai
from models.product import Product
from models.inventory import Inventory
from models.export_order import ExportOrder, ExportOrderDetail


def test_ai_data_security_no_sensitive_price_leaked(db_session):
    """
    Test case 1: Bảo mật dữ liệu nhạy cảm (Mục 5 đề tài)
    'Không gửi thông tin giá mua nhạy cảm nếu báo cáo AI không cần phân tích chi phí'
    Kỳ vọng: Chuỗi dữ liệu gửi cho AI KHÔNG chứa đơn giá mua, giá vốn hay chi phí
    """
    now = datetime.now(timezone.utc)
    data_text = get_inventory_data_for_ai(db_session, start_date=now - timedelta(days=30), end_date=now)

    assert "Mã SP" in data_text
    assert "Tồn cuối kỳ" in data_text
    # Kiểm tra không chứa các từ khóa về giá tiền nhạy cảm
    assert "unit_price" not in data_text.lower()
    assert "giá mua" not in data_text.lower()
    assert "đơn giá" not in data_text.lower()


def test_ai_data_empty_inventory(db_session):
    """
    Test case 2: Xử lý dữ liệu rỗng (Bài KT3)
    Khi kho hàng chưa có sản phẩm nào hoạt động
    Kỳ vọng: Hàm tổng hợp không bị crash, vẫn sinh ra tiêu đề báo cáo hợp lệ
    """
    # Deactivate sản phẩm mẫu
    prod = db_session.query(Product).first()
    if prod:
        prod.is_active = False
        db_session.commit()

    now = datetime.now(timezone.utc)
    data_text = get_inventory_data_for_ai(db_session, start_date=now - timedelta(days=30), end_date=now)

    assert "Kỳ báo cáo" in data_text
    assert "Mã SP | Tên SP" in data_text


def test_ai_data_spike_exports_and_low_stock(db_session):
    """
    Test case 3: Phát hiện xuất tăng bất thường & Dưới tồn tối thiểu (Bài KT3)
    Tạo sản phẩm có tồn ban đầu 20, tồn tối thiểu 10.
    Tạo phiếu xuất số lượng lớn = 15 (xuất tăng mạnh).
    Số tồn còn lại = 5 (< 10 tồn tối thiểu).
    Kỳ vọng:
    - Báo cáo sinh mục: SẢN PHẨM DƯỚI TỒN TỐI THIỂU
    - Báo cáo sinh mục: TOP 5 SẢN PHẨM XUẤT NHIỀU NHẤT
    """
    # Đảm bảo sản phẩm 1 active
    prod = db_session.query(Product).filter(Product.id == 1).first()
    prod.is_active = True
    prod.min_stock = 10

    inv = db_session.query(Inventory).filter(Inventory.product_id == 1).first()
    inv.quantity = 20
    db_session.commit()

    # Tạo phiếu xuất 15
    now = datetime.now(timezone.utc)
    exp_order = ExportOrder(
        code="PX_TEST_SPIKE",
        recipient="Khách Hàng Mua Sỉ",
        created_by=1,
        order_date=now,
        status="completed"
    )
    db_session.add(exp_order)
    db_session.flush()

    exp_detail = ExportOrderDetail(
        export_order_id=exp_order.id,
        product_id=1,
        quantity=15,
        reason="Xuất bán đột biến"
    )
    db_session.add(exp_detail)
    inv.quantity -= 15  # Tồn kho còn 5 < min_stock 10
    db_session.commit()

    data_text = get_inventory_data_for_ai(db_session, start_date=now - timedelta(days=7), end_date=now + timedelta(days=1))

    # Kiểm tra có cảnh báo tồn tối thiểu
    assert "SẢN PHẨM DƯỚI TỒN TỐI THIỂU" in data_text
    assert "thiếu 5" in data_text

    # Kiểm tra có thống kê top xuất nhiều nhất
    assert "TOP 5 SẢN PHẨM XUẤT NHIỀU NHẤT" in data_text
    assert "xuất 15" in data_text


def test_ai_report_endpoint_validation(client, warehouse_headers):
    """
    Test case 4: Kiểm tra validate loại báo cáo tại endpoint /api/ai/report
    """
    invalid_payload = {
        "report_type": "invalid_type",
        "period_start": "2026-01-01",
        "period_end": "2026-01-31"
    }
    response = client.post("/api/ai/report", json=invalid_payload, headers=warehouse_headers)
    assert response.status_code == 400
    assert "Loại báo cáo không hợp lệ" in response.json()["detail"]
