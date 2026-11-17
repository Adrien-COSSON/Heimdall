# Import libraries
import os
from dotenv import load_dotenv
load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Loading BOT_TOKEN and CHAT_ID for Telegram
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

# Trusted IP (may be empty: every SSH login is then reported as unknown)
trusted_ip = os.getenv('TRUSTED_IP') or None

# Critical variables
# Thresholds (temperatures in Celsius, usage in %)
thresholds = {'critical_temp_CPU': 90,
              'critical_temp_harddrive': 60,
              'max_ram_usage': 95,
              'max_cpu_usage': 95,
              'max_harddrive_usage': 90,
              'gpu_temp': 85,
              'gpu_load': 95,
              'gpu_mem_pct': 95}

# Polling interval in seconds
polling_intervalle = 60

# Alerts: one reminder per hour max while a metric stays above its threshold
alert_reminder_minutes = 60
# Hysteresis: a metric is back to normal only below (threshold - margin)
hysteresis = {"pct": 5, "temp_c": 5}

# Exported data, read by Hermès (latest.json + history.db)
data_dir = os.getenv('HEIMDALL_DATA_DIR', os.path.join(BASE_DIR, 'data'))
history_retention_hours = 24

# Watched systemd units (use the real unit names, see `systemctl list-units --type=service`)
services = ["hermes", "ollama", "ploutos"]

# SSH monitoring
auth_log_path = '/var/log/auth.log'
