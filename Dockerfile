FROM python:3.13-slim
LABEL authors="Illia Avdiienko"

WORKDIR /app
COPY . .

RUN pip install --no-cache -r requirements.txt

EXPOSE 8000

CMD uvicorn main:app --host 0.0.0.0 --port 8000
