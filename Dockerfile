# Stage 1: Build
FROM python:3.11-slim AS builder
RUN apt-get update && apt-get install -y ffmpeg
WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH=/root/.local/bin:$PATH

WORKDIR /app

COPY --from=builder /root/.local /root/.local
COPY . .

# Default command runs the API server with Gunicorn
CMD ["gunicorn", "-c", "app.main:app"]