# rtc_fallback.py - Uso de tiempo interno como respaldo si RTC externo falla

import time


def get_timestamp():
    t = time.localtime()
    return f"{t[0]:04d}-{t[1]:02d}-{t[2]:02d}T{t[3]:02d}:{t[4]:02d}:{t[5]:02d}"
