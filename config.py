# Import libraries
import os
from dotenv import load_dotenv
load_dotenv()

# Loading BOT_TOKEN and CHAT_ID for Telegram
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

# Critical variables
# Thresholds (temperatures in Celsius, usage in %, polling in seconds)
critical_temp_CPU = 90
critical_temp_harddrive = 60
max_ram_usage = 95
max_cpu_usage = 95
max_harddrive_usage = 90
polling_intervalle = 60
