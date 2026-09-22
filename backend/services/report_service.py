"""
Report service - Dịch vụ báo cáo
Aggregates warehouse data for reports and AI analysis
Tổng hợp dữ liệu kho cho báo cáo và phân tích AI
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, case
from datetime import datetime, timedelta, timezone, date
from models.product import Product, Category
from models.inventory import Inventory
from models.import_order import ImportOrder, ImportOrderDetail
from models.export_order import ExportOrder, ExportOrderDetail
from models.supplier import Supplier
from models.user import User


def get_dashboard_stats(db: Session) -> dict:
    """
    Get dashboard statistics / Lấy thống kê cho Dashboard
    """
    today_start = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    total_products = db.query(func.count(Product.id)).filter(
        Product.is_active == True
    ).scalar() or 0

    total_suppliers = db.query(func.count(Supplier.id)).filter(
        Supplier.is_active == True
    ).scalar() or 0

    # Import orders today / Phiếu nhập hôm nay
    total_import_today = db.query(func.count(ImportOrder.id)).filter(
        and_(
            ImportOrder.order_date >= today_start,
            ImportOrder.status == "completed"
        )
    ).scalar() or 0

    # Export orders today / Phiếu xuất hôm nay
    total_export_today = db.query(func.count(ExportOrder.id)).filter(
        and_(
            ExportOrder.order_date >= today_start,
            ExportOrder.status == "completed"
        )
    ).scalar() or 0

    # Low stock count / Số sản phẩm tồn kho thấp
    low_stock_subquery = (
        db.query(Product.id)
        .outerjoin(Inventory, Product.id == Inventory.product_id)
        .filter(
            and_(
                Product.is_active == True,
                Product.min_stock > 0,
                func.coalesce(Inventory.quantity, 0) < Product.min_stock
            )
        )
    )
    low_stock_count = low_stock_subquery.count()

    return {
        "total_products": total_products,
        "total_suppliers": total_suppliers,
        "total_import_today": total_import_today,
        "total_export_today": total_export_today,
        "low_stock_count": low_stock_count,
        "total_inventory_value": 0,
    }


def get_chart_data(db: Session, days: int = 7) -> dict:
    """
    Get import/export chart data for last N days
    Lấy dữ liệu biểu đồ nhập/xuất N ngày gần nhất
    """
    labels = []
    import_data = []
    export_data = []

    today = datetime.now(timezone.utc).date()

    for i in range(days - 1, -1, -1):
        target_date = today - timedelta(days=i)
        day_start = datetime.combine(target_date, datetime.min.time()).replace(tzinfo=timezone.utc)
        day_end = day_start + timedelta(days=1)

        labels.append(target_date.strftime("%d/%m"))

        # Count import orders for this day
        imp_count = db.query(func.count(ImportOrder.id)).filter(
            and_(
                ImportOrder.order_date >= day_start,
                ImportOrder.order_date < day_end,
                ImportOrder.status == "completed"
            )
        ).scalar() or 0
        import_data.append(imp_count)

        # Count export orders for this day
        exp_count = db.query(func.count(ExportOrder.id)).filter(
            and_(
                ExportOrder.order_date >= day_start,
                ExportOrder.order_date < day_end,
                ExportOrder.status == "completed"
            )
        ).scalar() or 0
        export_data.append(exp_count)

    return {
        "labels": labels,
        "import_data": import_data,
        "export_data": export_data,
    }


def get_inventory_summary(db: Session, start_date: datetime, end_date: datetime) -> list:
    """
    Get inventory summary report (nhập-xuất-tồn) for a period
    Lấy báo cáo tổng hợp nhập xuất tồn cho một kỳ
    """
    products = db.query(Product).filter(Product.is_active == True).all()
    summary = []

    for product in products:
        # Total imported in period / Tổng nhập trong kỳ
        total_imported = (
            db.query(func.coalesce(func.sum(ImportOrderDetail.quantity), 0))
            .join(ImportOrder, ImportOrderDetail.import_order_id == ImportOrder.id)
            .filter(
                and_(
                    ImportOrderDetail.product_id == product.id,
                    ImportOrder.order_date >= start_date,
                    ImportOrder.order_date <= end_date,
                    ImportOrder.status == "completed"
                )
            )
            .scalar()
        ) or 0

        # Total exported in period / Tổng xuất trong kỳ
        total_exported = (
            db.query(func.coalesce(func.sum(ExportOrderDetail.quantity), 0))
            .join(ExportOrder, ExportOrderDetail.export_order_id == ExportOrder.id)
            .filter(
                and_(
                    ExportOrderDetail.product_id == product.id,
                    ExportOrder.order_date >= start_date,
                    ExportOrder.order_date <= end_date,
                    ExportOrder.status == "completed"
                )
            )
            .scalar()
        ) or 0

        # Current stock / Tồn kho hiện tại
        inventory = db.query(Inventory).filter(
            Inventory.product_id == product.id
        ).first()
        closing_stock = inventory.quantity if inventory else 0

        # Opening stock = closing - imported + exported
        opening_stock = closing_stock - total_imported + total_exported

        category = db.query(Category).filter(
            Category.id == product.category_id
        ).first()

        summary.append({
            "product_id": product.id,
            "product_code": product.code,
            "product_name": product.name,
            "category_name": category.name if category else "",
            "opening_stock": opening_stock,
            "total_imported": total_imported,
            "total_exported": total_exported,
            "closing_stock": closing_stock,
            "min_stock": product.min_stock,
        })

    return summary


def get_inventory_data_for_ai(db: Session, start_date: datetime = None, end_date: datetime = None) -> str:
    """
    Prepare inventory data as text for AI analysis
    Chuẩn bị dữ liệu tồn kho dạng text cho AI phân tích
    """
    if not end_date:
        end_date = datetime.now(timezone.utc)
    if not start_date:
        start_date = end_date - timedelta(days=30)

    summary = get_inventory_summary(db, start_date, end_date)

    lines = []
    lines.append(f"Kỳ báo cáo / Report period: {start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}")
    lines.append("")
    lines.append("Mã SP | Tên SP | Danh mục | Tồn đầu kỳ | Nhập | Xuất | Tồn cuối kỳ | Tồn tối thiểu")
    lines.append("-" * 100)

    for item in summary:
        lines.append(
            f"{item['product_code']} | {item['product_name']} | {item['category_name']} | "
            f"{item['opening_stock']} | {item['total_imported']} | {item['total_exported']} | "
            f"{item['closing_stock']} | {item['min_stock']}"
        )

    # Add low stock alerts
    low_stock = [i for i in summary if i['closing_stock'] < i['min_stock'] and i['min_stock'] > 0]
    if low_stock:
        lines.append("")
        lines.append("⚠️ SẢN PHẨM DƯỚI TỒN TỐI THIỂU / PRODUCTS BELOW MINIMUM STOCK:")
        for item in low_stock:
            lines.append(
                f"  - {item['product_code']} {item['product_name']}: "
                f"tồn {item['closing_stock']}, tối thiểu {item['min_stock']}, "
                f"thiếu {item['min_stock'] - item['closing_stock']}"
            )

    # Add high export products
    high_export = sorted(summary, key=lambda x: x['total_exported'], reverse=True)[:5]
    if high_export and high_export[0]['total_exported'] > 0:
        lines.append("")
        lines.append("📊 TOP 5 SẢN PHẨM XUẤT NHIỀU NHẤT / TOP 5 MOST EXPORTED:")
        for item in high_export:
            if item['total_exported'] > 0:
                lines.append(
                    f"  - {item['product_code']} {item['product_name']}: "
                    f"xuất {item['total_exported']}"
                )

    return "\n".join(lines)
