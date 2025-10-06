import machine
from machine import I2C, deepsleep, Pin
import time, os
import config
from wifi_client import connect_wifi, disconnect_wifi
from http_client import get_remote_time, send_data
from rtc_ds1307 import RTC_DS1307
from sd_utils import save_json, copy_json
from power_control import power_on_all, power_off_all
from hd38 import HD38
from cwt_soil import CWT_Soil
from bme280 import read_bme
from retry_queue import init_queue, enqueue, process_queue

print(f"\n🚀 Nodo hijo {config.NODE_ID} iniciando...")

# 🕒 RTC vía I2C
i2c = I2C(0, scl=Pin(config.I2C_SCL), sda=Pin(config.I2C_SDA))
rtc = RTC_DS1307(i2c)

# Inicializar sistema de reintentos
init_queue()

# 🌐 Conexión Wi-Fi
try:
    wifi_ok = connect_wifi()
except Exception as e:
    print("⚠️ Error inicializando Wi-Fi:", e)
    wifi_ok = False

# ⏱️ Sincronizar hora si hay red
if wifi_ok:
    try:
        remote_time = get_remote_time()
        if remote_time:
            rtc.set_time_from_string(remote_time)
            print("✅ RTC sincronizado:", remote_time)
    except Exception as e:
        print("⚠️ Error sincronizando RTC:", e)

# Timestamp inicial
try:
    timestamp = rtc.get_timestamp()
except:
    timestamp = "1970-01-01T00:00:00"

# ⚡ Encender sensores
power_on_all()
print("⏳ Esperando inicialización del CWT Soil...")
time.sleep(30)  # darle tiempo al sensor a arrancar

# Instancia CWT
cwt_sensor = CWT_Soil(
    tx_pin=config.UART_RS485_TX,
    rx_pin=config.UART_RS485_RX,
    de_re_pin=config.RS485_DE_RE,
    baudrate=4800,
    addr=1,
    parity=None
)

# Mantener encendido 5 min tomando lecturas cada 30 s
start = time.time()
while time.time() - start < 300:  # 5 min

    # HD-38
    hd_sensor = HD38(config.HD38_ADC_PIN)
    hd_value = hd_sensor.read_percent()
    soil_hd38 = {"humidity": hd_value}

    # === CWT con reintentos (máx 3) ===
    soil_cwt = {}
    for intento in range(3):
        cwt_data = cwt_sensor.read_all() or {}
        if all(k in cwt_data and cwt_data[k] is not None 
               for k in ["humidity","nitrogen","phosphorus","potassium",
                         "conductivity","pH","salinity","temperature","tds"]):
            soil_cwt = cwt_data
            print(f"[CWT] Lectura válida en intento {intento+1}")
            break
        else:
            print(f"⚠️ [CWT] Datos incompletos en intento {intento+1}, reintentando...")
            time.sleep(1)

    if not soil_cwt:
        print("❌ [CWT] No se logró obtener datos completos tras 3 intentos")
        soil_cwt = {k: None for k in ["humidity","nitrogen","phosphorus",
                                      "potassium","conductivity","pH",
                                      "salinity","temperature","tds"]}

    # Ambientales
    ambient = read_bme(i2c) or {"temp": None, "hum": None, "pres": None}

    # Armar paquete de datos
    data = {
        "id": config.NODE_ID,
        "timestamp": rtc.get_timestamp(),
        "ambient": ambient,
        "soil_hd38": soil_hd38,
        "soil_cwt": soil_cwt
    }

    # 💾 Guardar en SD
    try:
        save_json(data, config.PATH_FILE)
        copy_json(data, config.PATH_COPY)
        save_json(data, config.PATH_TOTAL)
        try: os.sync()
        except: pass
        print("💾 Datos almacenados:", data)
    except Exception as e:
        print("❌ Error guardando:", e)

    # 📡 Intentar envío
    if wifi_ok:
        try:
            if send_data(data):
                print("✅ Datos enviados al nodo padre")
            else:
                enqueue(data, timestamp)
        except:
            enqueue(data, timestamp)

    # esperar 30 s antes de la siguiente muestra
    time.sleep(30)

# 🔌 Apagar sensores y Wi-Fi
power_off_all()
disconnect_wifi()

# 😴 Dormir 2 minutos
print("😴 Deep sleep por 2 min...\n")
time.sleep(1)
deepsleep(120000)
