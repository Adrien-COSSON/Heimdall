# Import libraries
import logging
import threading
import time
from datetime import datetime

import schedule

import config
from collectors.snapshot import collect_snapshot
from alerting.alerts import AlertManager
from alerting.telegram import send_alert
from alerting import listener
import exporter
import ssh_monitor

log = logging.getLogger('heimdall')


def run_once(alert_manager):
    '''
    One pass: a single measurement used for the alerts, latest.json and history.db.
    '''
    snapshot = collect_snapshot(config.thresholds, config.polling_intervalle, config.services)
    now = datetime.fromisoformat(snapshot['timestamp'])
    for message in alert_manager.evaluate(snapshot, now):
        send_alert(message)
    snapshot['alerts'] = alert_manager.active_alerts()
    exporter.write_latest(snapshot, config.data_dir)
    exporter.append_history(snapshot, config.data_dir, config.history_retention_hours)
    return snapshot


def safe_run(alert_manager):
    '''
    An error in one pass is logged and must never kill the loop.
    '''
    try:
        run_once(alert_manager)
    except Exception:
        log.exception("Polling pass failed")


def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s: %(message)s')
    alert_manager = AlertManager(config.thresholds, config.alert_reminder_minutes, config.hysteresis)

    threading.Thread(target=listener.start, daemon=True, name='telegram-listener').start()
    threading.Thread(target=ssh_monitor.monitor, daemon=True, name='ssh-monitor').start()
    send_alert("🔱 Heimdall is online")

    safe_run(alert_manager)  # first pass right away, so Hermès doesn't wait 60 s
    schedule.every(config.polling_intervalle).seconds.do(safe_run, alert_manager)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    main()
