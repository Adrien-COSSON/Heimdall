# Heimdall 🔱

Heimdall is a lightweight Python agent designed to run autonomously on a home AI server. It continuously monitors system health — CPU, RAM, disk usage and temperatures — and sends real-time Telegram alerts when critical thresholds are exceeded. Built to launch automatically at boot via systemd, Heimdall runs silently in the background and only speaks up when something demands attention.

Designed for homelab and personal AI infrastructure setups running Ubuntu Server.

---

## Features

- Real-time monitoring of CPU, RAM and disk usage
- Temperature monitoring for CPU and storage devices
- Instant Telegram alerts when critical thresholds are exceeded
- Startup notification when Heimdall comes online
- GPU monitoring (NVIDIA) — coming soon
- SSH security analysis — coming soon
- Lightweight — no database, no log files, minimal memory footprint

---

## Requirements

- Python 3.11+
- Ubuntu Server 24.04 (recommended)
- A Telegram account

---

## Setup

### 1. Clone the repository
```bash
git clone https://github.com/AdrienCosson/Heimdall.git
cd Heimdall
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Create your Telegram bot
- Open Telegram and search for `@BotFather`
- Send `/newbot` and follow the instructions
- Copy the `BOT_TOKEN` provided by BotFather
- Send a message to your new bot, then open:
```
https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates
```
- Find your `CHAT_ID` in the JSON response under `"chat":{"id": XXXXXXXXX}`

### 4. Create your `.env` file
```bash
touch .env
```
```
BOT_TOKEN=your_token_here
CHAT_ID=your_chat_id_here
```
> ⚠️ Never commit your `.env` file — it is already listed in `.gitignore`

### 5. Configure your thresholds

Edit `config.py` to set your own alert thresholds :
```python
thresholds = {
    "critical_temp_CPU": 90,       # °C
    "critical_temp_harddrive": 60, # °C
    "max_ram_usage": 95,           # %
    "max_cpu_usage": 95,           # %
    "max_harddrive_usage": 90      # %
}

polling_intervalle = 60            # seconds
```

---

## Run

### Manually
```bash
python agent.py
```

### Automatically at boot (systemd)
```bash
sudo nano /etc/systemd/system/heimdall.service
```
```ini
[Unit]
Description=Heimdall Server Monitor
After=network.target

[Service]
ExecStart=/usr/bin/python3 /path/to/agent.py
Restart=always
RestartSec=10
User=your_user

[Install]
WantedBy=multi-user.target
```
```bash
sudo systemctl enable heimdall
sudo systemctl start heimdall
```

---

## Telegram Alerts Examples

```
🔱 Heimdall is online

⚠️ CPU usage critical : 97% for a threshold of 95%

⚠️ RAM usage critical : 96% for a threshold of 95%

⚠️ Hard Drive usage critical : 92% for a threshold of 90%
```

---

## Roadmap

- [x] CPU / RAM / Disk usage monitoring
- [x] Temperature monitoring
- [x] Telegram alerts
- [x] Systemd auto-start
- [ ] GPU monitoring (NVIDIA)
- [ ] SSH security analysis
- [ ] Alert cooldown (anti-spam)

---

## Stack

Python · psutil · pynvml · Telegram Bot API · systemd

---

## License

MIT