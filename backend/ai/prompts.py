"""
AI Prompt Templates - Mẫu prompt cho AI
Designed to prevent hallucination - only analyze provided data
Thiết kế để tránh bịa số liệu - chỉ phân tích dữ liệu được cung cấp
"""

SYSTEM_PROMPT = """Bạn là trợ lý quản lý kho thông minh (AI Warehouse Assistant).
Quy tắc bắt buộc:
1. CHỈ phân tích dựa trên số liệu được cung cấp. KHÔNG tự tạo hoặc bịa số liệu mới.
2. Trả lời bằng song ngữ Việt-Anh (Tiếng Việt trước, English after).
3. Sử dụng format markdown để dễ đọc.
4. Đưa ra nhận xét cụ thể dựa trên con số thực tế.
5. Nếu dữ liệu không đủ để phân tích, hãy nói rõ thay vì đoán.

You are a smart warehouse management assistant (AI Warehouse Assistant).
Mandatory rules:
1. ONLY analyze based on provided data. DO NOT create or fabricate new data.
2. Respond in bilingual Vietnamese-English (Vietnamese first, English after).
3. Use markdown format for readability.
4. Provide specific observations based on actual numbers.
5. If data is insufficient for analysis, state so clearly instead of guessing."""


INVENTORY_REPORT_PROMPT = """Dữ liệu nhập xuất tồn kho / Inventory data:

{inventory_data}

Hãy sinh báo cáo nhập xuất tồn ngắn gọn gồm:
1. **Tổng quan tình trạng kho** (Overview): Tóm tắt số lượng sản phẩm, tình trạng chung
2. **Sản phẩm cần chú ý** (Products needing attention): Hàng tồn thấp, hàng xuất nhiều
3. **Nhận xét & Đề xuất** (Comments & Suggestions): Đánh giá hoạt động kho trong kỳ

Please generate a concise inventory report including:
1. **Warehouse Overview**: Summary of product quantities, general status
2. **Products Needing Attention**: Low stock items, high export items
3. **Comments & Suggestions**: Assessment of warehouse operations during the period"""


RESTOCK_SUGGESTION_PROMPT = """Dữ liệu tồn kho hiện tại / Current inventory data:

{inventory_data}

Dựa trên dữ liệu trên, hãy gợi ý nhập hàng:
1. **Danh sách cần nhập gấp** (Urgent restock): Sản phẩm dưới tồn tối thiểu
2. **Số lượng gợi ý nhập** (Suggested quantities): Dựa trên tốc độ xuất và tồn tối thiểu
3. **Ưu tiên nhập hàng** (Priority order): Sắp xếp theo mức độ cấp bách

Based on the data above, suggest restocking:
1. **Urgent Restock List**: Products below minimum stock
2. **Suggested Quantities**: Based on export rate and minimum stock levels
3. **Priority Order**: Sorted by urgency"""


ANOMALY_DETECTION_PROMPT = """Dữ liệu kho hàng / Warehouse data:

{inventory_data}

Hãy phân tích và phát hiện các biến động bất thường:
1. **Xuất tăng đột biến** (Sudden export spikes): Sản phẩm có lượng xuất cao bất thường
2. **Hàng tồn lâu** (Slow-moving items): Sản phẩm có tồn kho cao nhưng ít xuất
3. **Mất cân đối nhập-xuất** (Import-export imbalance): Nhập nhiều nhưng ít xuất hoặc ngược lại
4. **Tổng kết rủi ro** (Risk summary): Đánh giá mức độ rủi ro tổng thể

Analyze and detect unusual variations:
1. **Sudden Export Spikes**: Products with abnormally high export volumes
2. **Slow-moving Items**: Products with high stock but low exports
3. **Import-Export Imbalance**: High imports with low exports or vice versa
4. **Risk Summary**: Overall risk assessment"""
