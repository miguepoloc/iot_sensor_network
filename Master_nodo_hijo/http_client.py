# http_client.py - Cliente HTTP para sincronizar hora y enviar datos al nodo padre

import config
import urequests as requests


# Sincroniza hora desde /hora en nodo padre
def get_remote_time():
    try:
        res = requests.get(config.SERVER_URL + config.PATH_HORA)
        if res.status_code == 200:
            print("[HORA] Sincronizada:", res.text)
            return res.text
    except Exception as e:
        print("[HORA] Error al obtener hora:", e)
    return None


# Envío de datos a /data


def send_data(data):
    try:
        url = config.SERVER_URL + config.PATH_DATA
        headers = {"Content-Type": "application/json"}
        res = requests.post(url, json=data, headers=headers)
        print("[HTTP] Respuesta:", res.status_code)
        return res.status_code == 200
    except Exception as e:
        print("[HTTP] Error al enviar datos:", e)
        return False
