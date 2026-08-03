# Import libraries
import pynvml


def collect_gpu():
    '''
    xx
    '''
    try:
        pynvml.nvmlInit()
        handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        gpu_name = pynvml.nvmlDeviceGetName(handle)
        gpu_temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
        gpu_load = pynvml.nvmlDeviceGetUtilizationRates(handle)
        gpu_load_used = gpu_load.gpu
        mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
        gpu_mem_pct = (mem_info.used / mem_info.total) * 100
        return {'gpu_name': gpu_name,
                'gpu_temp': gpu_temp,
                'gpu_load': gpu_load_used,
                'gpu_mem_used': mem_info.used / 1024**2,
                'gpu_mem_total': mem_info.total / 1024**2,
                'gpu_mem_pct': gpu_mem_pct}
    except pynvml.NVMLError:
        return None
    finally:
        pynvml.nvmlShutdown()