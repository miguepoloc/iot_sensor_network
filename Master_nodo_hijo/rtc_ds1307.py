# rtc_ds1307.py – Módulo para manejar RTC DS1307 o DS3231 vía I2C con fallback interno

import machine
from machine import I2C, Pin
import config
import time

try:
    import ds1307
except:
    ds1307 = None

class RTC_DS1307:
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
                y, m, d, wd, h, mi, s, _ = self.rtc.datetime()
                return "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}".format(
                    y, m, d, h, mi, s
                )
        except Exception as e:
            print("⚠️ Error leyendo RTC externo:", e)

        # fallback → reloj interno
        t = time.localtime()
        return "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}".format(
            t[0], t[1], t[2], t[3], t[4], t[5]
        )

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
    return RTC_DS1307(i2c)

    
