FROM python:3.14-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir - t requirements.txt
COPY src/ ./src/
COPY migrations/ ./migrations/
COPY alembic.ini .
COPY frontend/ ./frontend/
EXPOSE 8000
CMD ["python", "-c", "from src.main import app_start; app_start()"]