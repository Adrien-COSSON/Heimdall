# Import libraries
try:
    import pynvml
except ImportError:  # nvidia-ml-py not installed
    pynvml = None

MB = 1024 ** 2


def _optional(fn, *args):
    '''
    Some readings (power...) are not supported on every GPU: None instead of failing.
    '''
    try:
        return fn(*args)
    except pynvml.NVMLError:
        return None


def collect_gpu():
    '''
    Returns the metrics of the first NVIDIA GPU, following the Hermès contract,
    or None if NVML is unavailable (no driver, no GPU, no pynvml).
    '''
    if pynvml is None:
        return None
    try:
        pynvml.nvmlInit()
    except pynvml.NVMLError:
        return None
    try:
        handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        name = pynvml.nvmlDeviceGetName(handle)
        if isinstance(name, bytes):  # older pynvml versions return bytes
            name = name.decode()
        mem = pynvml.nvmlDeviceGetMemoryInfo(handle)
        power_mw = _optional(pynvml.nvmlDeviceGetPowerUsage, handle)
        limit_mw = _optional(pynvml.nvmlDeviceGetEnforcedPowerLimit, handle)
        return {'name': name,
                'load_percent': pynvml.nvmlDeviceGetUtilizationRates(handle).gpu,
                'mem_used_mb': round(mem.used / MB),
                'mem_total_mb': round(mem.total / MB),
                'mem_percent': round(mem.used / mem.total * 100, 1),
                'temp_c': _optional(pynvml.nvmlDeviceGetTemperature, handle, pynvml.NVML_TEMPERATURE_GPU),
                'power_w': round(power_mw / 1000, 1) if power_mw is not None else None,
                'power_limit_w': round(limit_mw / 1000, 1) if limit_mw is not None else None}
    except pynvml.NVMLError:
        return None
    finally:
        # Only shut down when init succeeded (shutdown without init raises)
        pynvml.nvmlShutdown()
