from datetime import datetime, timedelta

from alerting.alerts import AlertManager, format_duration
from config import thresholds

T0 = datetime(2026, 11, 17, 8, 0).astimezone()


def snap(disk=50.0, cpu_temp=50.0):
    return {'cpu': {'percent': 10.0, 'temp_c': cpu_temp},
            'ram': {'percent': 40.0},
            'disk': {'percent': disk, 'nvme_temp_c': None},
            'gpu': None}


def at(minutes):
    return T0 + timedelta(minutes=minutes)


def test_entry_sends_one_alert():
    am = AlertManager(thresholds)
    assert am.evaluate(snap(disk=50), at(0)) == []
    assert am.evaluate(snap(disk=92), at(1)) == ["⚠️ Disque : 92 % (seuil 90 %)"]
    alerts = am.active_alerts()
    assert alerts == [{'metric': 'disk_usage', 'value': 92, 'threshold': 90, 'since': at(1).isoformat()}]


def test_no_repeat_before_reminder_then_reminder():
    am = AlertManager(thresholds, reminder_minutes=60)
    am.evaluate(snap(disk=92), at(0))
    for m in range(1, 60):
        assert am.evaluate(snap(disk=93), at(m)) == []
    assert am.evaluate(snap(disk=93), at(60)) == ["⏳ Disque toujours à 93 % depuis 1 h"]
    assert am.evaluate(snap(disk=93), at(61)) == []
    assert am.evaluate(snap(disk=93), at(120)) == ["⏳ Disque toujours à 93 % depuis 2 h"]


def test_return_only_below_margin():
    am = AlertManager(thresholds, hysteresis={'pct': 5, 'temp_c': 5})
    am.evaluate(snap(disk=92), at(0))
    # Oscillating around the threshold, inside the margin: nothing sent, still active
    for m, value in enumerate([89, 91, 86, 88.5, 85], start=1):
        assert am.evaluate(snap(disk=value), at(m)) == []
    assert am.active_alerts()
    assert am.evaluate(snap(disk=84), at(190)) == ["✅ Disque revenu à 84 % après 3 h 10"]
    assert am.active_alerts() == []
    # New crossing -> new alert
    assert am.evaluate(snap(disk=91), at(191)) == ["⚠️ Disque : 91 % (seuil 90 %)"]


def test_temperature_and_missing_sensor():
    am = AlertManager(thresholds)
    assert am.evaluate(snap(cpu_temp=91.5), at(0)) == ["⚠️ Température CPU : 91,5 °C (seuil 90 °C)"]
    assert am.evaluate(snap(cpu_temp=None), at(1)) == []   # sensor lost: state kept
    assert am.evaluate(snap(cpu_temp=86), at(2)) == []      # inside 5 °C margin
    assert am.evaluate(snap(cpu_temp=84), at(3)) == ["✅ Température CPU revenu à 84 °C après 3 min"]


def test_format_duration():
    assert format_duration(timedelta(minutes=45)) == "45 min"
    assert format_duration(timedelta(hours=2)) == "2 h"
    assert format_duration(timedelta(hours=3, minutes=5)) == "3 h 05"
