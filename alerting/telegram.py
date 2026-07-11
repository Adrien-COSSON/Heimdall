# Import library
import requests
import os
from dotenv import load_dotenv
load_dotenv()

# Loading BOT_TOKEN and CHAT_ID for Telegram
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

def send_alert(message):
    return requests.post(url=f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": message})
