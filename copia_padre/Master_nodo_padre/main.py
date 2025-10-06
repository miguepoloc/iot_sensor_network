# main.py – Ciclo principal del nodo padre (lectura, almacenamiento, envío y servidor Wi-Fi)

import machine
from machine import I2C, deepsleep
import time
import config
from hd38 import HD38
from cwt_soil import CWT_Soil
from sim800l import SIM800L
from rtc_ds1307 import RTC_DS1307
from config import CWT_TX, CWT_RX, CWT_DE_RE
from sd_utils import append_json
from bme280 import read_bme
from wifi_server import start_server, connected_nodes
from lte_queue import init_queue, enqueue, process_queue
from power_control import power_on_all, power_off_all

# 🔧 Inicialización de sensores y periféricos
print("🚀 Iniciando nodo padre...")
i2c = I2C(0, scl=config.I2C_SCL, sda=config.I2C_SDA)
rtc = RTC_DS1307(i2c)
hd38 = HD38(config.HD38_ADC_PIN)
cwt = CWT_Soil(
    tx_pin=CWT_TX,
    rx_pin=CWT_RX,
    de_re_pin=CWT_DE_RE
)
modem = SIM800L()
init_queue()

# 🔁 Ciclo de toma de datos único (deep sleep al final)
def run_cycle():
    timestamp = rtc.get_timestamp()
    print("\n[⏰] Timestamp:", timestamp)

    # ⚡ Encender sensores y módulos
    power_on_all()
    time.sleep(2)  # estabilización

    # 📏 Lectura de sensores
    hd = hd38.read_percent()
    print("[HD-38] Humedad del suelo (%):", hd)

    cwt_raw = cwt.read_values()
    print("[CWT] Datos recibidos:")
    for k, v in cwt_raw.items():
        print(f"   - {k}: {v}")

    ambient = read_bme(i2c)
    print("[BME280] Lectura ambiental:")
    for k, v in ambient.items():
        print(f"   - {k}: {v}")

    # 🧩 Ensamble de datos
    soil_data = {"hd38": hd}
    soil_data.update(cwt_raw)

    data = {
        "id": config.NODE_ID,
        "timestamp": timestamp,
        "ambient": ambient,
        "soil": soil_data,
        "connected_children": list(connected_nodes)
    }

    # 💾 Guardar en SD
    append_json(data, timestamp[:10] + ".json")
    print("[💾] Datos almacenados en SD")

    # 🔁 Procesar reintentos
    print("[📡] Procesando cola de reintentos LTE...")
    process_queue(modem.send_json)

    # 📤 Intentar enviar el dato actual
    try:
        modem.send_json(data)
        print("[✉️] Datos enviados correctamente vía LTE")
    except Exception as e:
        print("[!] Error en envío LTE:", e)
        enqueue(data, timestamp)

    # 🔌 Apagar sensores y periféricos
    power_off_all()
    time.sleep(1)

    # 😴 Entrar en deep sleep
    print("😴 Entrando en deep sleep...")
    deepsleep(config.SLEEP_INTERVAL_MS)

# 🔧 Servidor Wi-Fi para nodos hijos
import uasyncio as asyncio

async def main():
    await start_server()  # Mantiene el servidor activo (aunque deep sleep interrumpe después de un ciclo)

# 🚀 Iniciar ciclo principal y servidor
run_cycle()
loop = asyncio.get_event_loop()
loop.run_until_complete(main())


