import time

import machine

from . import ds1307


class RtcDs1307:
    def __init__(self, i2c: machine.I2C, addr: int = 0x68) -> None:
        self.i2c = i2c
        self.addr = addr

        try:
            if self.addr in self.i2c.scan():
                self.rtc = ds1307.DS1307(self.i2c)
                print("✅ RTC DS1307 detectado en I2C")
            else:
                print("⚠️ RTC DS1307 no detectado, usando reloj interno del ESP32")
        except Exception as e:
            print("⚠️ Error inicializando RTC:", e)

    def get_timestamp(self) -> str:
        try:
            dt = self.rtc.datetime()
            if dt is None:
                raise Exception("RTC returned None")
            y, m, d, _, h, mi, s, _ = dt
            return f"{y:04d}-{m:02d}-{d:02d}T{h:02d}:{mi:02d}:{s:02d}"
        except Exception as e:
            print("⚠️ Error leyendo RTC externo:", e)

        # fallback → reloj interno
        t = time.localtime()
        return f"{t[0]:04d}-{t[1]:02d}-{t[2]:02d}T{t[3]:02d}:{t[4]:02d}:{t[5]:02d}"

    def set_time(self, y: int, m: int, d: int, h: int, mi: int, s: int) -> bool:
        try:
            self.rtc.datetime((y, m, d, 0, h, mi, s, 0))
            return True
        except Exception as e:
            print("⚠️ Error configurando RTC externo:", e)
        return False

    def set_time_from_string(self, timestr: str) -> None:
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
