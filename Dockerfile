FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY data/ ./data/

WORKDIR /app/src

EXPOSE 8000

ENV QDRANT_HOST=host.docker.internal
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]