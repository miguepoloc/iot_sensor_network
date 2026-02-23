import json
import socket


class SimpleWebServer:
    def __init__(self, motor_controller, port=80, sensor=None):
        self.motor = motor_controller
        self.port = port
        self.sensor = sensor
        self.server_socket = None

    def start(self):
        """Inicializa el socket del servidor web"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(("", self.port))
        self.server_socket.listen(5)
        self.server_socket.setblocking(False)  # Asíncrono
        print(f"[Web] Servidor iniciado en el puerto {self.port}")

    def get_html(self):
        """Retorna el HTML estático para la interfaz"""
        html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Control Boya</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; margin-top: 50px; background-color: #f4f4f9;}
        h1 { color: #333; }
        button {
            font-size: 1.5em; padding: 15px 30px; margin: 10px; cursor: pointer;
            border: none; border-radius: 10px; color: white; width: 80%; max-width: 300px;
        }
        .btn-up { background-color: #4CAF50; }
        .btn-down { background-color: #2196F3; }
        .btn-stop { background-color: #f44336; }
        .btn-temp { background-color: #ff9800; }
        button:active { opacity: 0.8; transform: scale(0.98); }
        .info-box { margin-top: 20px; font-size: 20px; font-weight: bold; color: #555; }
    </style>
</head>
<body>
    <h1>Boya Oceanográfica</h1>
    <p>Control de Inmersión</p>
    <button class="btn btn-up" onclick="sendCommand('up')">⬆ SUBIR</button><br>
    <button class="btn btn-stop" onclick="sendCommand('stop')">🛑 DETENER</button><br>
    <button class="btn btn-down" onclick="sendCommand('down')">⬇ BAJAR</button>
    <br><hr style="width: 80%; max-width: 400px;"><br>
    <button class="btn btn-temp" onclick="readTemp()">🌡 LEER TEMP</button>
    
    <div class="info-box" id="temp-display">Temperatura: -- °C</div>
    <div class="info-box" id="status">Estado Motor: Detenido</div>
    
    <script>
        function sendCommand(cmd) {
            document.getElementById('status').innerText = "Estado Motor: Enviando " + cmd + "...";
            fetch('/' + cmd)
                .then(response => response.json())
                .then(data => {
                    document.getElementById('status').innerText = "Estado Motor: " + data.status;
                })
                .catch(err => {
                    document.getElementById('status').innerText = "Estado Motor: Error de conexión!";
                });
        }
        function readTemp() {
            document.getElementById('temp-display').innerText = "Temperatura: Leyendo...";
            fetch('/temp')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('temp-display').innerText = "Temperatura: " + data.temp + " °C";
                })
                .catch(err => {
                    document.getElementById('temp-display').innerText = "Temperatura: Error de lectura!";
                });
        }
    </script>
</body>
</html>"""
        return html

    def handle_request(self):
        """Procesa una petición HTTP de forma no bloqueante"""
        if not self.server_socket:
            return

        try:
            conn, _ = self.server_socket.accept()
            # conn.settimeout(0.5)
            request = conn.recv(1024).decode("utf-8")
            if not request:
                conn.close()
                return

            request_lines = request.split("\r\n")
            first_line = request_lines[0]

            # Extraer la ruta (/up, /down, /stop, o /)
            path = first_line.split(" ")[1] if len(first_line.split(" ")) > 1 else "/"

            response_body = ""
            content_type = "text/html"

            if path == "/up":
                self.motor.up()
                response_body = json.dumps({"status": "Subiendo"})
                content_type = "application/json"
            elif path == "/down":
                self.motor.down()
                response_body = json.dumps({"status": "Bajando"})
                content_type = "application/json"
            elif path == "/stop":
                self.motor.stop()
                response_body = json.dumps({"status": "Detenido"})
                content_type = "application/json"
            elif path == "/temp":
                temp_val = "Error"
                if self.sensor:
                    t = self.sensor.read_temperature()
                    if t is not None:
                        temp_val = str(t)
                response_body = json.dumps({"temp": temp_val})
                content_type = "application/json"
            else:
                # Servir la GUI HTML
                response_body = self.get_html()

            response = f"HTTP/1.1 200 OK\r\nContent-Type: {content_type}\r\nConnection: close\r\n\r\n{response_body}"
            conn.sendall(response.encode("utf-8"))
            conn.close()

        except OSError:
            # EWOULDBLOCK / EAGAIN (No hay clientes conectados, sigue de largo)
            pass
        except Exception as e:
            print(f"[Web] Error procesando petición: {e}")
            try:
                conn.close()
            except Exception:
                pass
