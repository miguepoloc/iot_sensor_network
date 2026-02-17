# wifi_client.py - Conexión Wi-Fi con reintento hacia el nodo padre

import time

import config
import network

wlan = network.WLAN(network.STA_IF)
wlan.active(True)


def connect_wifi(timeout_ms=config.WIFI_TIMEOUT_MS):
    print("[WIFI] Conectando a:", config.WIFI_SSID)
    wlan.connect(config.WIFI_SSID, config.WIFI_PASS)

    start = time.ticks_ms()
    while not wlan.isconnected():
        if time.ticks_diff(time.ticks_ms(), start) > timeout_ms:
            print("[WIFI] Tiempo de conexión agotado")
            return False
        time.sleep(1)

    print("[WIFI] Conectado:", wlan.ifconfig())
    return True


def disconnect_wifi():
    wlan.disconnect()
    wlan.active(False)
