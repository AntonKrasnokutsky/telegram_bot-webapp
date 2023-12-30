FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip3 install -r requirements.txt --no-cache-dir
COPY . .
CMD ["gunicorn", "--workers=3", "--max-requests=3", "coffee_bot_beckend.wsgi:application", "--bind", "0:8000" ]
