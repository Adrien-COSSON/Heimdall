# Import libraries
import json
import os
import sqlite3
from datetime import datetime, timedelta

LATEST_FILE = 'latest.json'
HISTORY_FILE = 'history.db'

SCHEMA = '''
CREATE TABLE IF NOT EXISTS metrics (
    ts        TEXT PRIMARY KEY,
    cpu_pct   REAL,
    ram_pct   REAL,
    gpu_pct   REAL,
    vram_pct  REAL,
    disk_pct  REAL,
    cpu_temp  REAL,
    gpu_temp  REAL
)
'''


def write_latest(snapshot, data_dir):
    '''
    Atomic write: Hermès can never read a half-written file.
    '''
    os.makedirs(data_dir, exist_ok=True)
    path = os.path.join(data_dir, LATEST_FILE)
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)
    return path


def read_latest(data_dir):
    '''
    Last snapshot written, or None if absent or unreadable.
    '''
    try:
        with open(os.path.join(data_dir, LATEST_FILE), encoding='utf-8') as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def _row(snapshot):
    gpu = snapshot.get('gpu') or {}
    return (snapshot['timestamp'],
            snapshot['cpu']['percent'],
            snapshot['ram']['percent'],
            gpu.get('load_percent'),
            gpu.get('mem_percent'),
            snapshot['disk']['percent'],
            snapshot['cpu']['temp_c'],
            gpu.get('temp_c'))


def append_history(snapshot, data_dir, retention_hours=24):
    '''
    Inserts one row per pass and purges rows older than retention_hours.
    Default journal mode (no WAL): Hermès opens the base read-only.
    '''
    os.makedirs(data_dir, exist_ok=True)
    now = datetime.fromisoformat(snapshot['timestamp'])
    # Text comparison of local ISO timestamps: at most one hour off on DST change day
    cutoff = (now - timedelta(hours=retention_hours)).isoformat(timespec='seconds')
    conn = sqlite3.connect(os.path.join(data_dir, HISTORY_FILE))
    try:
        with conn:
            conn.execute(SCHEMA)
            conn.execute('INSERT OR REPLACE INTO metrics VALUES (?, ?, ?, ?, ?, ?, ?, ?)', _row(snapshot))
            conn.execute('DELETE FROM metrics WHERE ts < ?', (cutoff,))
    finally:
        conn.close()
