# sim800l.py – Comunicación por SIM800L vía comandos AT (POST JSON mejorado)

from machine import UART
import time
import ujson
class SIM800L:
    def __init__(self, tx_pin, rx_pin, apn, server_url):
        self.uart = UART(1, baudrate=9600, tx=tx_pin, rx=rx_pin, timeout=2000)
        self.apn = apn
        self.server_url = server_url
        self.flush()

    def flush(self):
        while self.uart.any():
            self.uart.read()

    def send_cmd(self, cmd, delay=2):
        """Envia comando AT y retorna respuesta"""
        print(">>", cmd)
        self.uart.write((cmd + "\r\n").encode())
        time.sleep(delay)
        resp = self.uart.read()
        print("<<", resp)
        return resp

    def check_network(self):
        """Verifica registro en red y calidad de señal"""
        resp = self.send_cmd("AT+CREG?", 2)
        if resp and b",1" in resp or b",5" in resp:
            print("✅ Registrado en red GSM")
        else:
            print("❌ No registrado en red GSM")
            return False

        resp = self.send_cmd("AT+CSQ", 2)
        if resp and b"+CSQ" in resp:
            print("📶 Señal:", resp)
        return True

    def send_json(self, data, retries=3):
        """Envía un JSON por HTTP POST con reintentos"""
        json_data = ujson.dumps(data)
        for intento in range(1, retries + 1):
            print(f"\n--- Intento {intento} de envío ---")
            try:
                self.flush()
                self.send_cmd("AT", 2)

                if not self.check_network():
                    continue

                # Configurar GPRS
                self.send_cmd('AT+SAPBR=3,1,"CONTYPE","GPRS"', 2)
                self.send_cmd(f'AT+SAPBR=3,1,"APN","{self.apn}"', 2)
                self.send_cmd("AT+SAPBR=1,1", 8)
                self.send_cmd("AT+SAPBR=2,1", 3)

                # HTTP POST
                self.send_cmd("AT+HTTPINIT", 2)
                self.send_cmd(f'AT+HTTPPARA="URL","{self.server_url}"', 2)
                self.send_cmd('AT+HTTPPARA="CONTENT","application/json"', 2)
                self.send_cmd(f"AT+HTTPDATA={len(json_data)},5000", 2)
                time.sleep(0.5)
                self.uart.write(json_data.encode())
                print(">> JSON:", json_data)
                time.sleep(1)

                resp = self.send_cmd("AT+HTTPACTION=1", 8)
                if resp and b"200" in resp:
                    print("✅ Servidor respondió 200 OK")
                else:
                    print("⚠️ Respuesta inesperada:", resp)

                self.send_cmd("AT+HTTPREAD", 5)
                self.send_cmd("AT+HTTPTERM", 2)
                self.send_cmd("AT+SAPBR=0,1", 3)

                return True

            except Exception as e:
                print("❌ Error en intento", intento, ":", e)

        print("❌ No se pudo enviar tras varios intentos")
        return False
