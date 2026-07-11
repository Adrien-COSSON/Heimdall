# Heimdall
Heimdall is a lightweight Python agent designed to run autonomously on a home AI server. It continuously monitors system health — CPU, RAM, disk usage and temperatures — and sends real-time Telegram alerts when critical thresholds are exceeded.
Built to launch automatically at boot via systemd, Heimdall runs silently in the background and only speaks up when something demands attention. GPU monitoring (NVIDIA) is supported as an optional module, activated automatically when hardware is detected.
Designed for homelab and personal AI infrastructure setups running Ubuntu Server.
