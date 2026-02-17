# rtc_ds1307.py - Módulo para manejar RTC DS1307 o DS3231 vía I2C con fallback interno

import time

import config
from machine import I2C, Pin

try:
    import ds1307
except Exception:
    ds1307 = None


class RtcDs1307:
    def __init__(self, i2c, addr=0x68):
        self.i2c = i2c
        self.addr = addr
        self.available = False
        self.rtc = None

        try:
            if ds1307 and self.addr in self.i2c.scan():
                self.rtc = ds1307.DS1307(self.i2c)
                self.available = True
                print("✅ RTC DS1307 detectado en I2C")
            else:
                print("⚠️ RTC DS1307 no detectado, usando reloj interno del ESP32")
        except Exception as e:
            print("⚠️ Error inicializando RTC:", e)

    def get_timestamp(self):
        try:
            if self.available and self.rtc:
                y, m, d, _, h, mi, s, _ = self.rtc.datetime()
                return f"{y:04d}-{m:02d}-{d:02d}T{h:02d}:{mi:02d}:{s:02d}"
        except Exception as e:
            print("⚠️ Error leyendo RTC externo:", e)

        # fallback -> reloj interno
        t = time.localtime()
        return f"{t[0]:04d}-{t[1]:02d}-{t[2]:02d}T{t[3]:02d}:{t[4]:02d}:{t[5]:02d}"

    def set_time(self, y, m, d, h, mi, s):
        if self.available and self.rtc:
            try:
                self.rtc.datetime((y, m, d, 0, h, mi, s, 0))
                return True
            except Exception as e:
                print("⚠️ Error configurando RTC externo:", e)
        return False

    def set_time_from_string(self, timestr):
        """
        Recibe un string ISO 8601 (ej. '2025-06-28T14:25:00') y configura el RTC.
        """
        try:
            date_part, time_part = timestr.strip().split("T")
            year, month, day = [int(x) for x in date_part.split("-")]
            hour, minute, second = [int(x) for x in time_part.split(":")]
            ok = self.set_time(year, month, day, hour, minute, second)
            if ok:
                print("✅ RTC actualizado:", self.get_timestamp())
            else:
                print("⚠️ Hora ajustada solo en reloj interno (RTC no disponible)")
        except Exception as e:
            print("❌ Error configurando RTC:", e)


def setup_rtc():
    i2c = I2C(0, scl=Pin(config.I2C_SCL), sda=Pin(config.I2C_SDA))
    return RtcDs1307(i2c)
