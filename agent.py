# Import libraries
import schedule
import time
from config import polling_intervalle, thresholds
from collectors.system import get_metrics
from alerting.telegram import send_alert

def check_and_alert():
    current_status = get_metrics()
    if current_status['cpu_percent'] > thresholds['max_cpu_usage']:
        send_alert(f"⚠️ CPU usage critical : {current_status['cpu_percent']}% for a threshold of {thresholds['max_cpu_usage']}")
    if current_status['ram_memory_percent'] > thresholds['max_ram_usage']:
        send_alert(f"⚠️ RAM usage critical : {current_status['ram_memory_percent']}% for a threshold of {thresholds['max_ram_usage']}")
    if current_status['disk_usage_percent'] > thresholds['max_harddrive_usage']:
        send_alert(f"⚠️ Hard Drive usage critical : {current_status['disk_usage_percent']}% for a threshold of {thresholds['max_harddrive_usage']}")
    # TODO: sensor_temp — à implémenter après test sur Ubuntu Server

send_alert("🔱 Heimdall is online")

schedule.every(polling_intervalle).seconds.do(check_and_alert)

while True:
    schedule.run_pending()
    time.sleep(1)