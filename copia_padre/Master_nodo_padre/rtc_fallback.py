# rtc_fallback.py – Uso de tiempo interno como respaldo si RTC externo falla

import time

def get_timestamp():
    t = time.localtime()
    return "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}".format(t[0], t[1], t[2], t[3], t[4], t[5])