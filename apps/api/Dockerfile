FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /workspace

COPY apps/api /workspace/apps/api
COPY packages/contracts /workspace/packages/contracts

RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir /workspace/apps/api

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "/workspace/apps/api"]
