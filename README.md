# Heimdall 🔱

Heimdall is a lightweight Python agent designed to run autonomously on a home AI server. It continuously monitors system health — CPU, RAM, disk, NVIDIA GPU and temperatures — and sends Telegram alerts when critical thresholds are exceeded. It also exports its measurements so that other tools (such as [Hermès](https://github.com/Adrien-COSSON)) can display them without measuring anything themselves.

Designed for homelab and personal AI infrastructure setups running Ubuntu Server.

---

## Features

- Monitoring of CPU, RAM, swap, disk usage and load average
- Temperature monitoring for CPU (`k10temp`) and NVMe — missing sensors are tolerated
- NVIDIA GPU monitoring (load, VRAM, temperature, power) — automatically disabled if NVML is unavailable
- State of watched systemd services
- Telegram alerts without spam: one alert on entry, one reminder per hour, one message on return to normal (with hysteresis)
- SSH login monitoring (`/var/log/auth.log`), survives log rotation
- `status` command on Telegram
- Exports `data/latest.json` (last measurement) and `data/history.db` (24 h of history, SQLite)

---

## Requirements

- Python 3.11+
- Ubuntu Server 24.04 (recommended)
- A Telegram account
- NVIDIA driver (optional, for GPU monitoring)

---

## Setup

### 1. Clone the repository
```bash
git clone https://github.com/Adrien-COSSON/Heimdall.git
cd Heimdall
```

### 2. Install dependencies
```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
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
```
BOT_TOKEN=your_token_here
CHAT_ID=your_chat_id_here
TRUSTED_IP=192.168.1.10        # optional: your usual SSH client IP
HEIMDALL_DATA_DIR=             # optional: defaults to <repo>/data
```
> ⚠️ Never commit your `.env` file — it is already listed in `.gitignore`

### 5. Allow SSH monitoring
Reading `/var/log/auth.log` requires the `adm` group:
```bash
sudo usermod -aG adm $USER
```
Without it, Heimdall logs an error and keeps running without SSH monitoring.

### 6. Configure `config.py`
```python
thresholds = {
    "critical_temp_CPU": 90,       # °C
    "critical_temp_harddrive": 60, # °C
    "max_ram_usage": 95,           # %
    "max_cpu_usage": 95,           # %
    "max_harddrive_usage": 90,     # %
    "gpu_temp": 85,                # °C
    "gpu_load": 95,                # %
    "gpu_mem_pct": 95,             # %
}
polling_intervalle = 60                  # seconds
alert_reminder_minutes = 60              # reminder while a metric stays above its threshold
hysteresis = {"pct": 5, "temp_c": 5}     # back to normal only below threshold - margin
services = ["hermes"]                    # systemd units to watch
history_retention_hours = 24
```

---

## Run

### Manually
```bash
.venv/bin/python agent.py
```

### Automatically at boot (systemd)
```bash
sudo nano /etc/systemd/system/heimdall.service
```
```ini
[Unit]
Description=Heimdall Server Monitor
After=network-online.target
Wants=network-online.target

[Service]
WorkingDirectory=/home/adrien/Heimdall
ExecStart=/home/adrien/Heimdall/.venv/bin/python /home/adrien/Heimdall/agent.py
Restart=always
RestartSec=10
User=adrien

[Install]
WantedBy=multi-user.target
```
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now heimdall
journalctl -u heimdall -f    # logs
```

---

## Exported data

Heimdall writes, at every polling pass, in `data/` (ignored by git):

| File | Content |
|---|---|
| `latest.json` | Last measurement, written atomically (`.tmp` then `os.replace`) |
| `history.db` | SQLite, table `metrics`, one row per pass, rows older than 24 h are purged |

`latest.json` (excerpt):
```json
{
  "version": 1,
  "timestamp": "2026-11-17T09:41:07+01:00",
  "cpu":  {"percent": 23.4, "temp_c": 58.0, "load_avg": [1.4, 1.1, 0.9], "...": "..."},
  "ram":  {"percent": 68.1, "used_gb": 10.9, "total_gb": 15.6, "...": "..."},
  "disk": {"percent": 47.2, "used_gb": 440.0, "total_gb": 931.0, "nvme_temp_c": 41.0},
  "gpu":  {"name": "NVIDIA GeForce RTX 3080 Ti", "load_percent": 41, "mem_percent": 76.5, "...": "..."},
  "services": [{"name": "hermes", "active": true, "state": "active", "since": "..."}],
  "thresholds": {"...": "..."},
  "alerts": [{"metric": "disk_usage", "value": 92.0, "threshold": 90, "since": "..."}]
}
```
- A value that cannot be measured is `null`; `gpu` is `null` without NVML.
- Sizes in GB (base 1024), VRAM in MB, temperatures in °C, power in W.
- `alerts` lists the currently active alerts.

`history.db` columns: `ts, cpu_pct, ram_pct, gpu_pct, vram_pct, disk_pct, cpu_temp, gpu_temp`.

---

## Telegram messages

```
🔱 Heimdall is online
⚠️ Disque : 92 % (seuil 90 %)
⏳ Disque toujours à 93 % depuis 2 h
✅ Disque revenu à 84 % après 3 h 10
🚨 INTRUSION !!! From IP: 203.0.113.7
```
Send `status` to the bot to get a full summary.

---

## Tests

```bash
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/python -m pytest
```

---

## Roadmap

- [x] CPU / RAM / Disk usage monitoring
- [x] Temperature monitoring
- [x] Telegram alerts
- [x] Systemd auto-start
- [x] GPU monitoring (NVIDIA)
- [x] SSH login monitoring
- [x] Alert cooldown (anti-spam) with hysteresis
- [x] Export for Hermès (`latest.json`, `history.db`)

---

## Stack

Python · psutil · nvidia-ml-py · SQLite · Telegram Bot API · systemd

---

## License

MIT
