# main.py - Nodo padre: recibe datos de los hijos, guarda en SD y envía por LTE

import json
import time

import uasyncio as asyncio
from lte_queue import enqueue, init_queue, process_queue
from sd_utils import append_json
from sim800l import SIM800L
from wifi_server import start_server

print("🚀 Nodo padre iniciado (modo recepción de hijos)...")

# Inicializar cola de reintentos
init_queue()


# === Función para enviar datos por LTE ===
def send_via_lte(data):
    """
    Intenta enviar un paquete JSON por LTE usando SIM800L.
    Si el envío falla, almacena los datos en la cola de reintentos (pendientes).
    """
    modem = SIM800L()
    try:
        ok = modem.send_json(data)  # 📤 Intentar envío
        if ok:
            print("[📡] Datos enviados correctamente por LTE")
            return True
        else:
            print("[!] Fallo en envío LTE, se guardará en cola")
            ts = data.get("timestamp", str(time.time()))
            enqueue(data, ts)
            return False
    except Exception as e:
        print("[!] Error al enviar por LTE:", e)
        ts = data.get("timestamp", str(time.time()))
        enqueue(data, ts)
        return False


# === Manejo de datos recibidos desde hijos ===
def handle_child_data(data):
    """
    Recibe datos JSON de un hijo, los muestra en consola,
    los guarda en SD y luego intenta enviarlos por LTE.
    """
    try:
        # 👀 Mostrar JSON recibido
        print("\n📥 JSON recibido del hijo:")
        try:
            print(json.dumps(data))  # en formato compacto
        except Exception:
            print(data)  # fallback si falla ujson

        # Guardar en SD
        timestamp = data.get("timestamp", str(time.time()))
        fname = timestamp[:10] + ".json"  # archivo diario
        append_json(data, fname)  # 💾 Guardar en SD
        print(f"[💾] Datos de hijo {data.get('id')} guardados en {fname}")

        # 📡 Intentar envío inmediato por LTE
        send_via_lte(data)

    except Exception as e:
        print("❌ Error procesando datos de hijo:", e)
        enqueue(data, str(time.time()))  # Backup si algo falla


# === Proceso principal ===
async def main():
    # 🚀 Iniciar servidor para recibir datos de hijos
    asyncio.create_task(start_server(handle_child_data))

    # 🔁 Procesar reintentos LTE periódicamente
    while True:
        print("[🔁] Revisando cola de reintentos LTE...")
        process_queue(send_via_lte)  # Reenviar pendientes
        await asyncio.sleep(60)  # esperar 1 min antes de revisar otra vez


# 🚀 Ejecutar bucle principal
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
