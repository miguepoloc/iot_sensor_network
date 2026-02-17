# # rtc_ds1307.py - Módulo para manejar RTC DS1307 o DS3231 vía I2C
import ds1307


class RtcDs1307:
    def __init__(self, i2c):
        self.rtc = ds1307.DS1307(i2c)

    def get_timestamp(self):
        y, m, d, _, h, mi, s, _ = self.rtc.datetime()
        return f"{y:04d}-{m:02d}-{d:02d}T{h:02d}:{mi:02d}:{s:02d}"

    def set_time(self, y, m, d, h, mi, s):
        self.rtc.datetime((y, m, d, 0, h, mi, s, 0))
