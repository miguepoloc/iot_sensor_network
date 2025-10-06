# wifi_server.py – Punto de acceso y servidor HTTP para recibir datos y entregar hora

import network
import uasyncio as asyncio
import json
from sd_utils import append_json
import config
import time

# Configuración del punto de acceso Wi-Fi
ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid="NodoPadre_AP", password="12345678")
print("[WIFI] Punto de acceso activado como NodoPadre_AP")

# Servidor HTTP (asíncrono)
async def handle_client(reader, writer):
    try:
        request_line = await reader.readline()
        method, path, _ = request_line.decode().split()
        headers = {}

        while True:
            line = await reader.readline()
            if line == b"\r\n":
                break
            if b":" in line:
                key, value = line.decode().split(":", 1)
                headers[key.strip()] = value.strip()

        if method == "POST" and path == "/data":
            length = int(headers.get("Content-Length", 0))
            body = await reader.read(length)
            data = json.loads(body)
            print("[DATA] Recibido:", data)
            filename = "{}-{:02d}-{:02d}.json".format(*time.localtime()[0:3])
            append_json(data, filename)
            writer.write("HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nOK")

        elif method == "GET" and path == "/hora":
            now = time.localtime()
            timestr = "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}".format(*now[:6])
            writer.write("HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\n" + timestr)

        else:
            writer.write("HTTP/1.1 404 Not Found\r\n\r\n")

        await writer.drain()
        await writer.aclose()

    except Exception as e:
        print("[HTTP ERROR]", e)

# Iniciar servidor HTTP
async def start_server():
    server = await asyncio.start_server(handle_client, "0.0.0.0", 80)
    print("[HTTP] Servidor iniciado en /data y /hora")

    # Reemplazo de serve_forever()
    while True:
        await asyncio.sleep(3600)

