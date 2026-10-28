"""
AI router - API trợ lý AI
Endpoints for AI-powered warehouse analysis
Các endpoint cho phân tích kho hàng bằng AI
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from database import get_db
from models.user import User
from schemas.report import AIReportRequest, AIReportResponse, AIChatRequest, AIChatResponse
from services.auth_service import get_current_user
from services.report_service import get_inventory_data_for_ai
from ai.ai_service import ai_service

router = APIRouter(prefix="/api/ai", tags=["AI Assistant / Trợ lý AI"])


@router.post("/report", response_model=AIReportResponse)
async def generate_ai_report(
    request: AIReportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate AI-powered report / Sinh báo cáo bằng AI

    report_type options:
    - inventory_report: Báo cáo nhập xuất tồn / Inventory report
    - restock_suggestion: Gợi ý nhập hàng / Restock suggestions
    - anomaly_detection: Phát hiện bất thường / Anomaly detection
    """
    # Prepare data / Chuẩn bị dữ liệu
    inventory_data = get_inventory_data_for_ai(
        db,
        start_date=request.period_start,
        end_date=request.period_end,
    )

    if not inventory_data or inventory_data.strip() == "":
        raise HTTPException(
            status_code=400,
            detail="Không có dữ liệu kho để phân tích / No warehouse data to analyze"
        )

    # Call AI based on report type / Gọi AI theo loại báo cáo
    try:
        if request.report_type == "inventory_report":
            result = await ai_service.generate_report(inventory_data)
        elif request.report_type == "restock_suggestion":
            result = await ai_service.suggest_restock(inventory_data)
        elif request.report_type == "anomaly_detection":
            result = await ai_service.detect_anomalies(inventory_data)
        else:
            raise HTTPException(
                status_code=400,
                detail="Loại báo cáo không hợp lệ / Invalid report type"
            )

        return AIReportResponse(**result)

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi AI / AI Error: {str(e)}"
        )


@router.post("/chat", response_model=AIChatResponse)
async def ai_chat(
    request: AIChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Free-form AI chat with warehouse context
    Chat tự do với AI sử dụng ngữ cảnh dữ liệu kho

    Gửi câu hỏi bất kỳ về kho hàng, AI sẽ trả lời dựa trên dữ liệu thực tế.
    Send any question about the warehouse, AI will respond based on actual data.
    """
    if not request.message or not request.message.strip():
        raise HTTPException(
            status_code=400,
            detail="Tin nhắn không được để trống / Message cannot be empty"
        )

    # Lấy dữ liệu kho mới nhất làm ngữ cảnh / Get latest inventory data as context
    inventory_data = get_inventory_data_for_ai(db)

    if not inventory_data or inventory_data.strip() == "":
        raise HTTPException(
            status_code=400,
            detail="Không có dữ liệu kho để phân tích / No warehouse data to analyze"
        )

    try:
        # Chuyển lịch sử chat thành dạng dict cho ai_service
        history_dicts = [
            {"role": msg.role, "content": msg.content}
            for msg in (request.history or [])
        ]

        result = await ai_service.chat(
            user_message=request.message,
            inventory_data=inventory_data,
            history=history_dicts,
        )

        return AIChatResponse(**result)

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi AI Chat / AI Chat Error: {str(e)}"
        )
