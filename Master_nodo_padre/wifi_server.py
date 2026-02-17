# wifi_server.py - Punto de acceso y servidor HTTP para recibir datos y entregar hora

import json
import time

import config
import network
import uasyncio as asyncio

# Configuración del punto de acceso Wi-Fi
ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid=config.AP_SSID, password=config.AP_PASSWORD)
print(f"[WIFI] Punto de acceso activado como {config.AP_SSID}")


# Iniciar servidor HTTP con callback
async def start_server(on_data):
    async def handle_client(reader, writer):
        try:
            request_line = await reader.readline()
            method, path, _ = request_line.decode().split()
            headers = {}

            # === Leer cabeceras ===
            while True:
                line = await reader.readline()
                if line == b"\r\n":
                    break
                if b":" in line:
                    key, value = line.decode().split(":", 1)
                    headers[key.strip()] = value.strip()

            # === POST: /data (recibir datos de hijos) ===
            if method == "POST" and path == "/data":
                length = int(headers.get("Content-Length", 0))
                body = await reader.read(length)
                data = json.loads(body)

                # Pasar datos al callback
                on_data(data)

                # Responder al hijo
                writer.write("HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nOK")

            # === GET: /hora (los hijos piden la hora) ===
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

    # Crear servidor asíncrono
    await asyncio.start_server(handle_client, "0.0.0.0", 80)
    print("[HTTP] Servidor iniciado en /data y /hora")

    while True:
        await asyncio.sleep(3600)
