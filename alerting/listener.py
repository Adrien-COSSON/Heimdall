# Import libraries
import logging
import time

import requests

import config
import exporter
from alerting.telegram import send_alert
from collectors.system import get_top_processes

log = logging.getLogger(__name__)


def _fmt(value, unit=''):
    return 'n/a' if value is None else f"{value}{unit}"


def format_status():
    '''
    Formats the last snapshot written by the agent (latest.json) into a Telegram-ready
    status message, plus the current top processes. No second measurement.
    '''
    snap = exporter.read_latest(config.data_dir)
    if snap is None:
        return "📊 Heimdall — pas encore de mesure, réessaie dans une minute."
    cpu, ram, disk, gpu = snap['cpu'], snap['ram'], snap['disk'], snap.get('gpu')
    if gpu:
        gpu_line = (f"🎮 GPU: {gpu['name']} | {_fmt(gpu['temp_c'], '°C')} | {gpu['load_percent']}% | "
                    f"{gpu['mem_used_mb']}MB / {gpu['mem_total_mb']}MB ({gpu['mem_percent']}%)")
    else:
        gpu_line = "🎮 GPU: indisponible"
    alerts = snap.get('alerts') or []
    alerts_line = ", ".join(a['metric'] for a in alerts) if alerts else "aucune"
    processes_lines = "\n".join(f"{i+1}. {p.info['name']} — {p.info['cpu_percent']}%"
                                for i, p in enumerate(get_top_processes()))
    return f"""📊 Heimdall — Status ({snap['timestamp'][11:16]})
🖥️ CPU: {cpu['percent']}% | {_fmt(cpu['temp_c'], '°C')}
💾 Disk: {disk['percent']}% ({disk['used_gb']} / {disk['total_gb']} Go)
💿 NVMe: {_fmt(disk['nvme_temp_c'], '°C')}
🧠 RAM: {ram['percent']}% ({ram['used_gb']} / {ram['total_gb']} Go)
{gpu_line}
🚨 Alertes actives: {alerts_line}

⚙️ Processus:
{processes_lines}"""


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
                f"https://api.telegram.org/bot{config.BOT_TOKEN}/getUpdates",
                params={"timeout": 30, "offset": offset}, timeout=35)
            data = response.json()
            for update in data["result"]:
                offset = update["update_id"] + 1
                message = update.get("message", {})
                chat_id = message.get("chat", {}).get("id")
                text = message.get("text", "").strip().lower()
                if str(chat_id) == config.CHAT_ID:
                    handle_message(text)
        except Exception:
            log.exception("Telegram listener error")
            time.sleep(5)
