FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONPATH=/app/src PORT=8000
WORKDIR /app
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY config ./config
COPY src ./src
EXPOSE 8000
CMD ["sh","-c","uvicorn node47_espn.api:app --host 0.0.0.0 --port $PORT"]
