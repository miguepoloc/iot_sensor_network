# retry_queue.py – Reintentos de envío HTTP para nodo hijo


import ujson
import os

QUEUE_DIR = "/sd/pendientes"

# 🗂️ Crear carpeta si no existe
def init_queue():
    try:
        if "pendientes" not in os.listdir("/sd"):
            os.mkdir(QUEUE_DIR)
    except Exception as e:
        print("[WARN] No se pudo crear carpeta de reintentos:", e)

# ➕ Agregar archivo JSON si el envío falla
def enqueue(data, timestamp):
    try:
        safe_ts = timestamp.replace(":", "-")
        fname = "{}/fail_{}.json".format(QUEUE_DIR, safe_ts)
        with open(fname, "w") as f:
            ujson.dump(data, f)
        print("[SAVE] Guardado para reintento:", fname)
    except Exception as e:
        print("[ERROR] Guardando reintento:", e)

# 🔁 Procesar archivos pendientes
def process_queue(send_func):
    try:
        files = os.listdir(QUEUE_DIR)
        for fname in files:
            if fname.endswith(".json"):
                path = "{}/{}".format(QUEUE_DIR, fname)
                with open(path) as f:
                    data = ujson.load(f)
                try:
                    if send_func(data):
                        os.remove(path)
                        print("[OK] Reenviado y eliminado:", fname)
                    else:
                        print("[WAIT] Falló reenvío (se mantiene):", fname)
                except Exception as e:
                    print("[ERROR] Reenviando {}: {}".format(fname, e))
    except Exception as e:
        print("[ERROR] Procesando reintentos:", e)
