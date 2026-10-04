FROM python:3.14-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ ./src/
COPY migrations/ ./migrations/
COPY alembic.ini .
COPY frontend/ ./frontend/
EXPOSE 8000
CMD ["python", "-c", "from src.main import start_server; app_start()"]