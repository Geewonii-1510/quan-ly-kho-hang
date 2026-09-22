"""
Reports router - API báo cáo thống kê
Dashboard stats, charts, inventory summary
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from database import get_db
from models.user import User
from schemas.report import DashboardStats, ChartData, InventoryReport
from services.auth_service import get_current_user
from services.report_service import get_dashboard_stats, get_chart_data, get_inventory_summary

router = APIRouter(prefix="/api/reports", tags=["Reports / Báo cáo"])


@router.get("/dashboard", response_model=DashboardStats)
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get dashboard statistics / Lấy thống kê Dashboard"""
    return get_dashboard_stats(db)


@router.get("/chart")
def get_chart(
    days: int = Query(default=7, ge=1, le=90),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get import/export chart data / Lấy dữ liệu biểu đồ nhập/xuất"""
    return get_chart_data(db, days)


@router.get("/inventory-summary")
def get_report_inventory_summary(
    start_date: str = Query(None, description="Start date YYYY-MM-DD"),
    end_date: str = Query(None, description="End date YYYY-MM-DD"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get inventory summary report (nhập-xuất-tồn)
    Báo cáo tổng hợp nhập xuất tồn
    """
    now = datetime.now(timezone.utc)

    if end_date:
        end_dt = datetime.strptime(end_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    else:
        end_dt = now

    if start_date:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    else:
        start_dt = end_dt - timedelta(days=30)

    summary = get_inventory_summary(db, start_dt, end_dt)

    total_imported = sum(i["total_imported"] for i in summary)
    total_exported = sum(i["total_exported"] for i in summary)

    return {
        "period_start": start_dt.isoformat(),
        "period_end": end_dt.isoformat(),
        "items": summary,
        "total_imported": total_imported,
        "total_exported": total_exported,
    }
