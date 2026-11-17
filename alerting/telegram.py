import logging

import requests

from config import BOT_TOKEN, CHAT_ID

log = logging.getLogger(__name__)


def send_alert(message):
    try:
        response = requests.post(
            url=f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": CHAT_ID, "text": message},
            timeout=10)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        log.error("Telegram error: %s", e)
