import requests
from django.conf import settings

def send_telegram_message(text: str):
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": settings.TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
    }

    try:
        requests.post(url, data=payload, timeout=5)
    except Exception:
        pass