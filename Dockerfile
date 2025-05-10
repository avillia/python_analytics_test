FROM python:3.13-slim
LABEL authors="Illia Avdiienko"

WORKDIR /app
COPY . .

ENV PYTHONUNBUFFERED=1

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000
