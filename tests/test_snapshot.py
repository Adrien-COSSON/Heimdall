from datetime import datetime
from types import SimpleNamespace

import psutil

import collectors.snapshot as snapshot_mod
from collectors import system
from config import thresholds

TOP_KEYS = {'version', 'timestamp', 'host', 'boot_time', 'uptime_s', 'polling_s', 'cpu', 'ram',
            'disk', 'gpu', 'services', 'thresholds', 'alerts'}
CPU_KEYS = {'model', 'cores', 'threads', 'percent', 'load_avg', 'temp_c'}
RAM_KEYS = {'percent', 'used_gb', 'total_gb', 'swap_used_gb', 'swap_total_gb'}
DISK_KEYS = {'mount', 'percent', 'used_gb', 'total_gb', 'nvme_temp_c'}


def _snapshot(monkeypatch, temps):
    monkeypatch.setattr(psutil, 'sensors_temperatures', lambda: temps, raising=False)
    monkeypatch.setattr(snapshot_mod, 'collect_gpu', lambda: None)
    return snapshot_mod.collect_snapshot(thresholds, 60, [])


def test_snapshot_respects_contract(monkeypatch):
    snap = _snapshot(monkeypatch, {})
    assert set(snap) == TOP_KEYS
    assert set(snap['cpu']) == CPU_KEYS
    assert set(snap['ram']) == RAM_KEYS
    assert set(snap['disk']) == DISK_KEYS
    assert snap['version'] == 1
    assert datetime.fromisoformat(snap['timestamp']).tzinfo is not None
    assert snap['thresholds'] == thresholds
    assert snap['alerts'] == [] and snap['services'] == []


def test_missing_sensors_give_null(monkeypatch):
    snap = _snapshot(monkeypatch, {'acpitz': []})  # no k10temp, no nvme
    assert snap['cpu']['temp_c'] is None
    assert snap['disk']['nvme_temp_c'] is None
    assert snap['gpu'] is None


def test_sensors_present(monkeypatch):
    reading = SimpleNamespace(label='Tctl', current=58.04, high=None, critical=None)
    snap = _snapshot(monkeypatch, {'k10temp': [reading], 'nvme': [reading]})
    assert snap['cpu']['temp_c'] == 58.0
    assert snap['disk']['nvme_temp_c'] == 58.0


def test_sensors_function_failure(monkeypatch):
    def boom():
        raise OSError("no sensors")
    monkeypatch.setattr(psutil, 'sensors_temperatures', boom, raising=False)
    assert system.read_temperatures() == {'cpu': None, 'nvme': None}
