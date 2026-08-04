# Import libraries
from alerting.telegram import send_alert
from collectors.system import get_metrics, get_top_processes
from collectors.gpu import collect_gpu
import requests
import time
import os
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

def format_status():
    '''
    Collects all system metrics and formats them into a Telegram-ready status message.
    Returns a formatted string with CPU, RAM, disk, temperatures, GPU, and top processes.
    '''
    system_metrics = get_metrics()
    top_processes = get_top_processes()
    processes_lines = "\n".join([f"{i+1}. {p.info['name']} — {p.info['cpu_percent']}%" for i, p in enumerate(top_processes)])
    try:
        gpu_metrics = collect_gpu()
    except Exception:
        gpu_metrics = None
    if gpu_metrics:
        gpu_line = f"🎮 GPU: {gpu_metrics['gpu_name']} | {gpu_metrics['gpu_temp']}°C | {gpu_metrics['gpu_load']}% | {gpu_metrics['gpu_mem_used']}MB / {gpu_metrics['gpu_mem_total']}MB ({gpu_metrics['gpu_mem_pct']}%)"
    else:
        gpu_line = "🎮 GPU: indisponible"
    message = f"""📊 Heimdall — Status
🖥️ CPU: {system_metrics['cpu_percent']}% | {system_metrics['cpu_temp']}°C
💾 Disk: {system_metrics['disk_usage_percent']}%
💿 NVMe: {system_metrics['nvme_temp']}°C
🧠 RAM: {system_metrics['ram_memory_percent']}%
{gpu_line}

⚙️ Processus:
{processes_lines}"""
    return message


def handle_message(text):
    '''
    Dispatches incoming Telegram commands to the appropriate handler.
    Calls format_status() for 'status', otherwise notifies the user of an unknown command.
    '''
    if text == "status":
        send_alert(format_status())
    else:
        send_alert("❓ Unknown command. Send status to have a complet review of the server.")

def start():
    '''
    Starts the Telegram long polling loop.
    Listens for incoming messages, verifies the chat_id, and dispatches commands to handle_message().
    Resumes automatically after 5 seconds on network error.
    '''
    offset = 0
    while True:
        try:
            response = requests.get(
                f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates",
                params={"timeout": 30, "offset": offset}, timeout=35)
            data = response.json()
            for update in data["result"]:
                offset = update["update_id"] + 1
                message = update.get("message", {})
                chat_id = message.get("chat", {}).get("id")
                text = message.get("text", "").strip().lower()
                if str(chat_id) == CHAT_ID:
                    handle_message(text)
        except Exception:
            time.sleep(5)
    