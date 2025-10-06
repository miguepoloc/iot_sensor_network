# sim800l.py – Comunicación por SIM800L vía comandos AT (POST JSON)

from machine import UART
import time
import ujson
import config

class SIM800L:
    def __init__(self):
        self.uart = UART(1, baudrate=9600, tx=config.SIM800_TX, rx=config.SIM800_RX)
        self.flush()

    def flush(self):
        while self.uart.any():
            self.uart.read()

    def send_cmd(self, cmd, delay=1):
        self.uart.write((cmd + '\r\n').encode())
        time.sleep(delay)
        return self.uart.read()

    def send_json(self, data):
        json_data = ujson.dumps(data)
        self.send_cmd('AT')
        self.send_cmd('AT+SAPBR=3,1,"CONTYPE","GPRS"')
        self.send_cmd(f'AT+SAPBR=3,1,"APN","{config.APN}"')
        self.send_cmd('AT+SAPBR=1,1', 3)
        self.send_cmd('AT+HTTPINIT')
        self.send_cmd(f'AT+HTTPPARA="URL","{config.SERVER_URL}"')
        self.send_cmd('AT+HTTPPARA="CONTENT","application/json"')
        self.send_cmd(f'AT+HTTPDATA={len(json_data)},10000')
        time.sleep(0.5)
        self.uart.write(json_data.encode())
        time.sleep(1)
        self.send_cmd('AT+HTTPACTION=1', 3)
        self.send_cmd('AT+HTTPTERM')
        self.send_cmd('AT+SAPBR=0,1')
