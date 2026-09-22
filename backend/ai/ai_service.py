"""
AI Service - Dịch vụ AI
Google Gemini integration for warehouse analysis
Tích hợp Google Gemini cho phân tích kho hàng
"""

import google.generativeai as genai
from config import settings
from ai.prompts import (
    SYSTEM_PROMPT,
    INVENTORY_REPORT_PROMPT,
    RESTOCK_SUGGESTION_PROMPT,
    ANOMALY_DETECTION_PROMPT,
)
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


class AIService:
    """
    AI Service using Google Gemini / Dịch vụ AI sử dụng Google Gemini
    """

    def __init__(self):
        self.model = None
        self._current_model_name = None
        self._initialized = False

    def _ensure_initialized(self):
        """Initialize Gemini model lazily / Khởi tạo model Gemini khi cần"""
        if self._initialized and self.model and self._current_model_name == settings.GEMINI_MODEL:
            return

        if not settings.GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY chưa được cấu hình. "
                "Vui lòng thêm API key vào file .env / "
                "GEMINI_API_KEY not configured. "
                "Please add API key to .env file"
            )

        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(
            model_name=settings.GEMINI_MODEL,
            system_instruction=SYSTEM_PROMPT,
        )
        self._current_model_name = settings.GEMINI_MODEL
        self._initialized = True

    async def generate_report(self, inventory_data: str) -> dict:
        """
        Generate inventory report using AI
        Sinh báo cáo nhập xuất tồn bằng AI
        """
        self._ensure_initialized()

        prompt = INVENTORY_REPORT_PROMPT.format(inventory_data=inventory_data)

        try:
            response = self.model.generate_content(prompt)
            return {
                "report_type": "inventory_report",
                "content": response.text,
                "generated_at": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as e:
            logger.error(f"AI report generation failed: {e}")
            return {
                "report_type": "inventory_report",
                "content": f"Lỗi khi sinh báo cáo / Error generating report: {str(e)}",
                "generated_at": datetime.now(timezone.utc).isoformat(),
            }

    async def suggest_restock(self, inventory_data: str) -> dict:
        """
        Get AI restock suggestions
        Lấy gợi ý nhập hàng từ AI
        """
        self._ensure_initialized()

        prompt = RESTOCK_SUGGESTION_PROMPT.format(inventory_data=inventory_data)

        try:
            response = self.model.generate_content(prompt)
            return {
                "report_type": "restock_suggestion",
                "content": response.text,
                "generated_at": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as e:
            logger.error(f"AI restock suggestion failed: {e}")
            return {
                "report_type": "restock_suggestion",
                "content": f"Lỗi khi sinh gợi ý / Error generating suggestion: {str(e)}",
                "generated_at": datetime.now(timezone.utc).isoformat(),
            }

    async def detect_anomalies(self, inventory_data: str) -> dict:
        """
        Detect anomalies using AI
        Phát hiện bất thường bằng AI
        """
        self._ensure_initialized()

        prompt = ANOMALY_DETECTION_PROMPT.format(inventory_data=inventory_data)

        try:
            response = self.model.generate_content(prompt)
            return {
                "report_type": "anomaly_detection",
                "content": response.text,
                "generated_at": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as e:
            logger.error(f"AI anomaly detection failed: {e}")
            return {
                "report_type": "anomaly_detection",
                "content": f"Lỗi khi phân tích / Error analyzing: {str(e)}",
                "generated_at": datetime.now(timezone.utc).isoformat(),
            }

    async def chat(self, user_message: str, inventory_data: str, history: list = None) -> dict:
        """
        Free-form chat with AI using warehouse data as context
        Chat tự do với AI sử dụng dữ liệu kho làm ngữ cảnh
        """
        self._ensure_initialized()

        # Xây dựng prompt ngữ cảnh với dữ liệu kho thực tế
        context_prompt = (
            f"Dưới đây là dữ liệu hiện tại của kho hàng:\n\n"
            f"{inventory_data}\n\n"
            f"Hãy trả lời câu hỏi sau của người dùng dựa trên dữ liệu kho ở trên:\n"
            f"{user_message}"
        )

        try:
            # Chuyển đổi lịch sử chat sang định dạng Gemini
            gemini_history = []
            if history:
                for h in history:
                    gemini_history.append({
                        "role": h.get("role", "user"),
                        "parts": [h.get("content", "")],
                    })

            # Khởi tạo session chat với lịch sử (multi-turn)
            chat_session = self.model.start_chat(history=gemini_history)
            response = chat_session.send_message(context_prompt)

            return {
                "reply": response.text,
                "generated_at": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as e:
            logger.error(f"AI chat failed: {e}")
            return {
                "reply": f"Lỗi khi xử lý chat / Chat error: {str(e)}",
                "generated_at": datetime.now(timezone.utc).isoformat(),
            }


# Singleton instance / Instance duy nhất
ai_service = AIService()
