import requests
import os
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

def send_alert(message):
    try:
        response = requests.post(
            url=f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": CHAT_ID, "text": message}
        )
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"Telegram error: {e}")