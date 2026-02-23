# boot.py - Script de arranque
# Se ejecuta automáticamete después de encender antes de ejecutar main.py.

import time

import network

try:
    import config
except ImportError:
    pass


def init_ap():
    """Inicializa la ESP32 como un Punto de Acceso WiFi para la interfaz Web."""
    print("Iniciando modo Access Point (AP)...")
    ap = network.WLAN(network.AP_IF)
    ap.active(True)

    # Configurar Nombre y Clave de la red, usando WPA2
    try:
        ssid = config.AP_SSID
        pwd = config.AP_PASS
    except Exception:
        ssid = "Boya_AP_Rescue"
        pwd = "password"

    ap.config(essid=ssid, password=pwd, authmode=3)  # authmode=3 es WPA2-PSK

    # Esperamos a que la red esté activa
    while not ap.active():
        time.sleep(0.5)

    ip_info = ap.ifconfig()
    print("=======================================")
    print(f"AP Establecido! Conéctate al WiFi: '{ssid}'")
    print(f"Ingresa en tu navegador a: http://{ip_info[0]}")
    print("=======================================")


# Iniciar WiFi AP al arrancar
init_ap()
