# Backend Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies / Cài đặt thư viện
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code / Sao chép mã nguồn
COPY . .

# Expose port / Mở cổng
EXPOSE 8000

# Start server / Khởi động server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
