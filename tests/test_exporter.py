import json
import os
import sqlite3
import threading
from datetime import datetime, timedelta

import exporter

TZ = datetime.now().astimezone().tzinfo


def make_snapshot(ts, gpu=True):
    return {'version': 1,
            'timestamp': ts.isoformat(timespec='seconds'),
            'cpu': {'percent': 23.4, 'temp_c': 58.0},
            'ram': {'percent': 68.1},
            'disk': {'percent': 47.2},
            'gpu': {'load_percent': 41, 'mem_percent': 76.5, 'temp_c': 64} if gpu else None,
            'alerts': []}


def test_write_latest_atomic(tmp_path):
    snap = make_snapshot(datetime.now(TZ))
    path = exporter.write_latest(snap, str(tmp_path))
    assert json.load(open(path)) == snap
    assert not os.path.exists(path + '.tmp')
    assert exporter.read_latest(str(tmp_path)) == snap


def test_latest_always_valid_json_while_writing(tmp_path):
    '''A reader polling the file during many writes never sees a partial JSON.'''
    data_dir = str(tmp_path)
    exporter.write_latest(make_snapshot(datetime.now(TZ)), data_dir)
    stop = threading.Event()
    errors = []

    def reader():
        while not stop.is_set():
            try:
                with open(os.path.join(data_dir, 'latest.json')) as f:
                    json.load(f)
            except ValueError as e:
                errors.append(e)

    t = threading.Thread(target=reader)
    t.start()
    big = make_snapshot(datetime.now(TZ))
    big['services'] = [{'name': f's{i}', 'active': True, 'state': 'active', 'since': None} for i in range(500)]
    for _ in range(200):
        exporter.write_latest(big, data_dir)
    stop.set()
    t.join()
    assert errors == []


def test_read_latest_missing(tmp_path):
    assert exporter.read_latest(str(tmp_path)) is None


def test_history_insert_and_purge(tmp_path):
    data_dir = str(tmp_path)
    now = datetime.now(TZ).replace(microsecond=0)
    exporter.append_history(make_snapshot(now - timedelta(hours=25)), data_dir)
    exporter.append_history(make_snapshot(now - timedelta(hours=23)), data_dir)
    exporter.append_history(make_snapshot(now, gpu=False), data_dir)

    conn = sqlite3.connect(os.path.join(data_dir, 'history.db'))
    rows = conn.execute('SELECT ts, cpu_pct, gpu_pct FROM metrics ORDER BY ts').fetchall()
    mode = conn.execute('PRAGMA journal_mode').fetchone()[0]
    conn.close()
    assert [r[0] for r in rows] == [(now - timedelta(hours=23)).isoformat(), now.isoformat()]
    assert rows[1][1] == 23.4 and rows[1][2] is None  # gpu null -> NULL column
    assert mode == 'delete'  # default journal, no WAL
