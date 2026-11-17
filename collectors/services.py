# Import libraries
import subprocess
from datetime import datetime


def _systemctl(*args):
    try:
        result = subprocess.run(['systemctl', *args], capture_output=True, text=True, timeout=5)
        return result.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ''


def _parse_since(raw):
    '''
    `--timestamp=unix` gives "@1731770880"; empty or "n/a" if the unit never started.
    '''
    if not raw.startswith('@'):
        return None
    try:
        return datetime.fromtimestamp(int(raw[1:])).astimezone().isoformat(timespec='seconds')
    except ValueError:
        return None


def collect_services(names):
    '''
    State of each watched systemd unit:
    [{"name", "active", "state", "since"}]
    '''
    services = []
    for name in names:
        state = _systemctl('is-active', name) or 'unknown'
        since = None
        if state == 'active':
            since = _parse_since(_systemctl('show', '-p', 'ActiveEnterTimestamp', '--value',
                                            '--timestamp=unix', name))
        services.append({'name': name, 'active': state == 'active', 'state': state, 'since': since})
    return services
