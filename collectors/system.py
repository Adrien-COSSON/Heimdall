# Import libraries
import os
import socket
from datetime import datetime

import psutil

GB = 1024 ** 3


def _gb(n_bytes):
    return round(n_bytes / GB, 1)


def _first_temp(temps, sensor):
    '''
    Returns the first reading of a sensor in °C, or None if the sensor is missing
    (e.g. after a kernel update renaming it).
    '''
    readings = temps.get(sensor)
    if not readings:
        return None
    return round(readings[0].current, 1)


def read_temperatures():
    '''
    Returns {'cpu': °C or None, 'nvme': °C or None}. Never raises.
    '''
    try:
        temps = psutil.sensors_temperatures() or {}
    except (AttributeError, OSError):
        temps = {}
    return {'cpu': _first_temp(temps, 'k10temp'),
            'nvme': _first_temp(temps, 'nvme')}


def cpu_model():
    '''
    Reads the CPU model name in /proc/cpuinfo, None if unavailable.
    '''
    try:
        with open('/proc/cpuinfo') as f:
            for line in f:
                if line.startswith('model name'):
                    return line.split(':', 1)[1].strip()
    except OSError:
        pass
    return None


def collect_cpu(temp_c):
    '''
    psutil.cpu_percent() without interval: the value covers the time elapsed since
    the previous call (i.e. the previous polling pass). Call it once per pass.
    '''
    try:
        load_avg = [round(x, 2) for x in os.getloadavg()]
    except OSError:
        load_avg = None
    return {'model': cpu_model(),
            'cores': psutil.cpu_count(logical=False),
            'threads': psutil.cpu_count(logical=True),
            'percent': psutil.cpu_percent(),
            'load_avg': load_avg,
            'temp_c': temp_c}


def collect_ram():
    ram = psutil.virtual_memory()
    swap = psutil.swap_memory()
    return {'percent': ram.percent,
            'used_gb': _gb(ram.total - ram.available),
            'total_gb': _gb(ram.total),
            'swap_used_gb': _gb(swap.used),
            'swap_total_gb': _gb(swap.total)}


def collect_disk(nvme_temp_c, mount='/'):
    disk = psutil.disk_usage(mount)
    return {'mount': mount,
            'percent': disk.percent,
            'used_gb': _gb(disk.used),
            'total_gb': _gb(disk.total),
            'nvme_temp_c': nvme_temp_c}


def collect_host():
    boot = psutil.boot_time()
    now = datetime.now().astimezone()
    return {'host': socket.gethostname(),
            'boot_time': datetime.fromtimestamp(boot).astimezone().isoformat(timespec='seconds'),
            'uptime_s': int(now.timestamp() - boot)}


def get_top_processes():
    '''
    Returns the 5 most CPU-intensive processes at the time of the call.
    Each element is a psutil.Process object with name, cmdline and cpu_percent attributes.
    '''
    top_processes = []
    try:
        processes = sorted(
            psutil.process_iter(['name', 'cmdline', 'cpu_percent']),
            key=lambda p: p.info['cpu_percent'] or 0,
            reverse=True)
        top_processes = processes[:5]
    except psutil.NoSuchProcess:
        pass
    return top_processes
