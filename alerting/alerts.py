# Import libraries
from dataclasses import dataclass
from datetime import timedelta

# key, label, path in the snapshot, threshold key, kind (for units and hysteresis)
METRICS = [
    ('cpu_usage', 'CPU', ('cpu', 'percent'), 'max_cpu_usage', 'pct'),
    ('cpu_temp', 'Température CPU', ('cpu', 'temp_c'), 'critical_temp_CPU', 'temp_c'),
    ('ram_usage', 'RAM', ('ram', 'percent'), 'max_ram_usage', 'pct'),
    ('disk_usage', 'Disque', ('disk', 'percent'), 'max_harddrive_usage', 'pct'),
    ('nvme_temp', 'Température NVMe', ('disk', 'nvme_temp_c'), 'critical_temp_harddrive', 'temp_c'),
    ('gpu_temp', 'Température GPU', ('gpu', 'temp_c'), 'gpu_temp', 'temp_c'),
    ('gpu_load', 'Charge GPU', ('gpu', 'load_percent'), 'gpu_load', 'pct'),
    ('gpu_mem', 'Mémoire GPU', ('gpu', 'mem_percent'), 'gpu_mem_pct', 'pct'),
]
UNITS = {'pct': ' %', 'temp_c': ' °C'}


@dataclass
class AlertState:
    active: bool = False
    since: object = None       # datetime
    last_sent: object = None   # datetime
    value: float = None
    threshold: float = None


def _get(snapshot, path):
    node = snapshot
    for key in path:
        if not isinstance(node, dict):
            return None
        node = node.get(key)
    return node


def format_value(value, kind):
    return f"{round(value, 1):g}".replace('.', ',') + UNITS[kind]


def format_duration(delta):
    minutes = int(delta.total_seconds() // 60)
    hours, minutes = divmod(minutes, 60)
    if hours == 0:
        return f"{minutes} min"
    return f"{hours} h" if minutes == 0 else f"{hours} h {minutes:02d}"


class AlertManager:
    '''
    Per metric: one alert when crossing the threshold, one reminder per
    `reminder_minutes` max while it stays active, one message on return to normal.
    Return to normal is validated only below (threshold - hysteresis margin).
    State is kept in memory: a restart of Heimdall re-sends the active alerts once.
    '''

    def __init__(self, thresholds, reminder_minutes=60, hysteresis=None):
        self.thresholds = thresholds
        self.reminder = timedelta(minutes=reminder_minutes)
        self.hysteresis = hysteresis or {'pct': 5, 'temp_c': 5}
        self.states = {key: AlertState() for key, *_ in METRICS}

    def evaluate(self, snapshot, now):
        '''
        Updates the states with a snapshot, returns the Telegram messages to send.
        '''
        messages = []
        for key, label, path, threshold_key, kind in METRICS:
            value = _get(snapshot, path)
            threshold = self.thresholds.get(threshold_key)
            if value is None or threshold is None:
                continue  # sensor missing: state unchanged
            state = self.states[key]
            state.value, state.threshold = value, threshold
            if not state.active:
                if value > threshold:
                    state.active, state.since, state.last_sent = True, now, now
                    messages.append(f"⚠️ {label} : {format_value(value, kind)} "
                                    f"(seuil {format_value(threshold, kind)})")
            elif value < threshold - self.hysteresis[kind]:
                messages.append(f"✅ {label} revenu à {format_value(value, kind)} "
                                f"après {format_duration(now - state.since)}")
                state.active, state.since, state.last_sent = False, None, None
            elif now - state.last_sent >= self.reminder:
                state.last_sent = now
                messages.append(f"⏳ {label} toujours à {format_value(value, kind)} "
                                f"depuis {format_duration(now - state.since)}")
        return messages

    def active_alerts(self):
        '''
        Currently active alerts, for the "alerts" field of latest.json.
        '''
        return [{'metric': key,
                 'value': state.value,
                 'threshold': state.threshold,
                 'since': state.since.isoformat(timespec='seconds')}
                for key, state in self.states.items() if state.active]
