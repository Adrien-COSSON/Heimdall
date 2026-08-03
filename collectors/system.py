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
