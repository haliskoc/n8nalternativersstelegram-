FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY rss_telegram_bot.py .

ENV PYTHONUNBUFFERED=1

CMD ["python", "rss_telegram_bot.py"]
