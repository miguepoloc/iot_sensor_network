# boot.py – Nodo hijo
import machine, os, time
import sdcard
import ntptime
import ds1307
from machine import Pin, I2C
import config

print("[BOOT] Iniciando nodo hijo...")

# === 1. Montaje de tarjeta SD ===
spi = machine.SPI(
    2,
    baudrate=400000,
    polarity=0,
    phase=0,
    sck=Pin(config.SPI_SCK),
    mosi=Pin(config.SPI_MOSI),
    miso=Pin(config.SPI_MISO)
)
cs = Pin(config.SD_CS, Pin.OUT)

sd_montada = False
for intento in range(1, 6):  # hasta 5 intentos
    try:
        sd = sdcard.SDCard(spi, cs)
        vfs = os.VfsFat(sd)
        os.mount(vfs, "/sd")
        print("✅ SD montada correctamente:", os.listdir("/sd"))
        sd_montada = True
        break
    except Exception as e:
        print(f"⚠️ Fallo montando SD (intento {intento}/5):", e)
        time.sleep(1)

if not sd_montada:
    print("❌ No se pudo montar la SD después de varios intentos")

# === 2. Inicialización del RTC DS1307 ===
def sync_rtc():
    print("🕒 Sincronizando RTC...")
    i2c = I2C(0, scl=Pin(config.I2C_SCL), sda=Pin(config.I2C_SDA))
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
        print("⚠️ No se pudo sincronizar por NTP:", e)
        try:
            rtc_time = ds.datetime()
            rtc.datetime((rtc_time[0], rtc_time[1], rtc_time[2], rtc_time[6],
                          rtc_time[3], rtc_time[4], rtc_time[5], 0))
            print("✅ Hora cargada desde RTC externo:", time.localtime())
        except Exception as e2:
            print("❌ Error cargando hora desde RTC DS1307:", e2)

# Ejecutar sincronización del reloj
sync_rtc()
print("✅ Finalizó boot.py – ejecutando main.py...")
