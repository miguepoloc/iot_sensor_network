from machine import UART, Pin
import time

class CWT_Soil:
    def __init__(self, tx_pin, rx_pin, de_re_pin, baudrate=9600):
        self.uart = UART(2, tx=tx_pin, rx=rx_pin, baudrate=baudrate)
        self.control = Pin(de_re_pin, Pin.OUT)
        self.control.off()

    def send_modbus(self, addr, func, reg, qty):
        req = bytearray([
            addr,
            func,
            reg >> 8, reg & 0xFF,
            qty >> 8, qty & 0xFF
        ])
        crc = self.calc_crc(req)
        req += crc.to_bytes(2, 'little')
        self.control.on()
        time.sleep(0.01)
        self.uart.write(req)
        time.sleep(0.01)
        self.control.off()
        time.sleep(0.01)

    def read_response(self, length):
        timeout = time.ticks_ms() + 1000
        while time.ticks_ms() < timeout:
            if self.uart.any() >= length:
                return self.uart.read(length)
        return None

    def calc_crc(self, data):
        crc = 0xFFFF
        for pos in data:
            crc ^= pos
            for i in range(8):
                if (crc & 1):
                    crc >>= 1
                    crc ^= 0xA001
                else:
                    crc >>= 1
        return crc

    def read_values(self):
        # Simulación: en aplicación real, implementa varias lecturas por dirección
        self.send_modbus(0x01, 0x03, 0x0000, 0x07)  # Leer 7 registros desde 0x0000
        res = self.read_response(17)
        if res:
            try:
                ph = (res[3] << 8 | res[4]) / 10.0
                ec = (res[5] << 8 | res[6]) / 100.0
                N  = res[7] << 8 | res[8]
                P  = res[9] << 8 | res[10]
                K  = res[11] << 8 | res[12]
                temp = (res[13] << 8 | res[14]) / 10.0
                hum = (res[15] << 8 | res[16]) / 10.0
                return {"ph": ph, "ec": ec, "N": N, "P": P, "K": K, "soil_temp": temp, "soil_hum": hum}
            except:
                return {}
        return {}

