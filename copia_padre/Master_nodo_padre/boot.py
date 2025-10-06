# boot.py – Configuración inicial del nodo (montaje de microSD y reloj)

import machine
import os
import sdcard
import config
import time
import network
import ntptime
from rtc_ds1307 import RTC_DS1307
import ds1307

print("[BOOT] Preparando pines de control de energía...")

# === 0. Inicializar pines de control (relés o MOSFETs) ===
try:
    sim800_power = machine.Pin(config.PIN_SIM800L_POWER, machine.Pin.OUT)
    cwt_power = machine.Pin(config.PIN_CWT_POWER, machine.Pin.OUT)

    sim800_power.off()  # Apagar módulos por defecto al arrancar
    cwt_power.off()
    print("✅ Pines de relé configurados correctamente")
except Exception as e:
    print("⚠️ Error al configurar pines de relé:", e)

# === 1. Montaje de tarjeta SD ===
print("[BOOT] Iniciando SPI y montaje de SD...")
spi = machine.SPI(2, baudrate=1000000, polarity=0, phase=0,
                  sck=machine.Pin(config.SPI_SCK),
                  mosi=machine.Pin(config.SPI_MOSI),
                  miso=machine.Pin(config.SPI_MISO))
cs = machine.Pin(config.SD_CS, machine.Pin.OUT)

try:
    sd = sdcard.SDCard(spi, cs)
    vfs = os.VfsFat(sd)
    os.mount(vfs, "/sd")
    print("✅ SD montada correctamente:", os.listdir("/sd"))
except OSError as e:
    if "timeout" in str(e).lower():
        print("⚠️ Advertencia: SD montada con retardo, posible respuesta lenta.")
    else:
        print(f"[✘] Error OSError al montar la SD: {e}")

# === 2. Sincronización del RTC ===
def sync_rtc():
    print("🕒 Sincronizando RTC...")
    i2c = machine.I2C(0, scl=machine.Pin(config.I2C_SCL), sda=machine.Pin(config.I2C_SDA))
    ds = ds1307.DS1307(i2c)
    rtc = machine.RTC()

    try:
        print("🌐 Intentando sincronizar con servidor NTP...")
        ntptime.settime()  # UTC
        utc_time = time.localtime(time.time() + config.TIMEZONE_OFFSET)
        rtc.datetime((utc_time[0], utc_time[1], utc_time[2], utc_time[6],
                      utc_time[3], utc_time[4], utc_time[5], 0))
        ds.datetime((utc_time[0], utc_time[1], utc_time[2], utc_time[6],
                     utc_time[3], utc_time[4], utc_time[5]))
        print("✅ Hora sincronizada desde NTP:", utc_time)
    except Exception as e:
        print("⚠️ No se pudo sincronizar por NTP. Intentando cargar desde RTC DS1307...")
        try:
            rtc_time = ds.datetime()
            rtc.datetime((rtc_time[0], rtc_time[1], rtc_time[2], rtc_time[6],
                          rtc_time[3], rtc_time[4], rtc_time[5], 0))
            print("✅ Hora cargada desde RTC externo:", time.localtime())
        except Exception as e:
            print("❌ Error cargando hora desde RTC DS1307:", e)

# Ejecutar sincronización del reloj
sync_rtc()
print("✅ Finalizó boot.py – ejecutando main.py...\n")
time.sleep(1)

