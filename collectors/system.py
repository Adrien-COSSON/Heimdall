# Import library
import psutil

# Monitoring of the different values
def get_metrics():
    return {"cpu_percent": psutil.cpu_percent(), 
            "ram_memory_percent": psutil.virtual_memory().percent, 
            "disk_usage_percent": psutil.disk_usage("/").percent, 
            "sensor_temp": psutil.sensors_temperatures()}