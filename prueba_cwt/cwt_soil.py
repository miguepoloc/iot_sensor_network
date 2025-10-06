from machine import UART, Pin
import time

class CWT_Soil:
    def __init__(self, tx_pin=17, rx_pin=16, de_re_pin=4, baudrate=4800, addr=1, parity=None):
        self.addr = addr
        self.uart = UART(2, baudrate=baudrate, bits=8, parity=parity, stop=1, tx=tx_pin, rx=rx_pin)
        self.control = Pin(de_re_pin, Pin.OUT)
        self.control.off()

    def calc_crc(self, data):
        crc = 0xFFFF
        for ch in data:
            crc ^= ch
            for _ in range(8):
                if crc & 1:
                    crc >>= 1
                    crc ^= 0xA001
                else:
                    crc >>= 1
        return bytes([crc & 0xFF, (crc >> 8) & 0xFF])

    def build_request(self, reg, qty=1):
        req = bytearray([self.addr, 0x03, reg >> 8, reg & 0xFF, 0x00, qty])
        req += self.calc_crc(req)
        return req

    def send_request(self, reg, qty=1):
        cmd = self.build_request(reg, qty)
        self.uart.read()  # limpiar buffer
        self.control.on()
        time.sleep_ms(2)
        self.uart.write(cmd)
        self.uart.flush()
        time.sleep_ms(5)
        self.control.off()

        # Esperar respuesta (7 + 2*qty bytes)
        length = 5 + 2 * qty
        timeout = time.ticks_ms() + 500
        resp = b""
        while time.ticks_ms() < timeout and len(resp) < length:
            if self.uart.any():
                resp += self.uart.read(1)
        return resp if len(resp) >= length else None

    def parse_response(self, resp):
        if not resp or len(resp) < 7:
            return None
        data, crc_rx = resp[:-2], resp[-2:]
        if crc_rx != self.calc_crc(data):
            return None
        return (resp[3] << 8) | resp[4]

    def read_all(self):
        """
        Según el datasheet:
        0x0000: Humedad (x0.1 %)
        0x0001: Temperatura (x0.1 °C)
        0x0002: Conductividad (uS/cm)
        0x0003: pH (x0.1)
        0x0004: N (mg/kg)
        0x0005: P (mg/kg)
        0x0006: K (mg/kg)
        0x0007: Salinidad (mg/L)
        0x0008: TDS (mg/L)
        """
        results = {}

        mapping = {
            "humidity": (0x0000, 10.0, "%"),
            "temperature": (0x0001, 10.0, "°C"),
            "conductivity": (0x0002, 1.0, "uS/cm"),
            "pH": (0x0003, 10.0, ""),
            "nitrogen": (0x0004, 1.0, "mg/kg"),
            "phosphorus": (0x0005, 1.0, "mg/kg"),
            "potassium": (0x0006, 1.0, "mg/kg"),
            "salinity": (0x0007, 1.0, "mg/L"),
            "tds": (0x0008, 1.0, "mg/L"),
        }

        for key, (reg, scale, unit) in mapping.items():
            resp = self.send_request(reg, 1)
            val = self.parse_response(resp)
            if val is not None:
                results[key] = val / scale
            else:
                results[key] = None
            time.sleep_ms(200)

        return results
