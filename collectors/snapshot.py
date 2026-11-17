# Import libraries
from datetime import datetime

from collectors.system import read_temperatures, collect_cpu, collect_ram, collect_disk, collect_host
from collectors.gpu import collect_gpu
from collectors.services import collect_services

CONTRACT_VERSION = 1


def collect_snapshot(thresholds, polling_s, service_names=()):
    '''
    One measurement pass, shared by alerts, latest.json and history.db.
    The "alerts" field is filled afterwards by the AlertManager.
    '''
    temps = read_temperatures()
    snapshot = {'version': CONTRACT_VERSION,
                'timestamp': datetime.now().astimezone().isoformat(timespec='seconds')}
    snapshot.update(collect_host())
    snapshot.update({'polling_s': polling_s,
                     'cpu': collect_cpu(temps['cpu']),
                     'ram': collect_ram(),
                     'disk': collect_disk(temps['nvme']),
                     'gpu': collect_gpu(),
                     'services': collect_services(service_names),
                     'thresholds': dict(thresholds),
                     'alerts': []})
    return snapshot
