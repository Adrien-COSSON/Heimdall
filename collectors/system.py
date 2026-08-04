# Import library
import psutil

# Monitoring of the different values
def get_metrics():
    if hasattr(psutil, "sensors_temperatures"):
        temps = psutil.sensors_temperatures()
        cpu_temp = temps['k10temp'][0].current
        nvme_temp = temps['nvme'][0].current
    else:
        cpu_temp = None
        nvme_temp = None
    return {'cpu_percent': psutil.cpu_percent(), 
            'ram_memory_percent': psutil.virtual_memory().percent, 
            'disk_usage_percent': psutil.disk_usage("/").percent, 
            'cpu_temp': cpu_temp,
            'nvme_temp': nvme_temp
            }

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