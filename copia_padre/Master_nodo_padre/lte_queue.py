# lte_queue.py – Sistema de cola para reintentos de envío LTE en caso de fallo

import ujson
import os

QUEUE_DIR = "/sd/pendientes"

# Asegura que el directorio exista
def init_queue():
    try:
        if "pendientes" not in os.listdir("/sd"):
            os.mkdir(QUEUE_DIR)
    except Exception as e:
        print("[ERROR] Creando carpeta de reintentos:", e)

# Guardar un paquete no enviado
def enqueue(data, timestamp):
    try:
        safe_ts = timestamp.replace(":", "-")
        fname = "{}/fail_{}.json".format(QUEUE_DIR, safe_ts)
        with open(fname, "w") as f:
            ujson.dump(data, f)
        print("[⬇] Guardado en cola de reintento:", fname)
    except Exception as e:
        print("[ERROR] Al guardar en cola LTE:", e)

# Intentar reenviar todos los archivos pendientes
def process_queue(sender_func):
    try:
        for fname in os.listdir(QUEUE_DIR):
            if fname.endswith(".json"):
                path = "{}/{}".format(QUEUE_DIR, fname)
                with open(path) as f:
                    data = ujson.load(f)
                try:
                    sender_func(data)
                    os.remove(path)
                    print("[✔] Reenviado y eliminado:", fname)
                except Exception as e:
                    print("[!] Falló reenvío de", fname, ":", e)
    except Exception as e:
        print("[ERROR] Procesando cola LTE:", e)

