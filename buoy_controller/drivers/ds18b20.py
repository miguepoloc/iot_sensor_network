import time

import ds18x20
import machine
import onewire


class DS18B20Sensor:
    def __init__(self, pin_num):
        """
        Inicializador del sensor de temperatura calibrado DS18B20
        usando el protocolo 1-Wire de Dallas Semiconductor.
        """
        self.pin = machine.Pin(pin_num)
        self.ds = ds18x20.DS18X20(onewire.OneWire(self.pin))
        self.roms = []

        try:
            self.roms = self.ds.scan()
            if self.roms:
                print(f"[DS18B20] Sensor encontrado. ROMs: {len(self.roms)}")
            else:
                print("[DS18B20] ⚠️ No se detectaron sensores 1-Wire (revisar resistencia 4.7k)")
        except Exception as e:
            print(f"[DS18B20] Error escaneando bus 1-Wire: {e}")

    def read_temperature(self):
        """
        Ordena al sensor realizar la lectura (toma aprox 750ms internamente)
        y devuelve la temperatura en grados Celsius del primer sensor detectado.
        """
        if not self.roms:
            # Reintentar escaneo por si se conectó tarde
            self.roms = self.ds.scan()
            if not self.roms:
                return None

        try:
            self.ds.convert_temp()
            # El manual del ds18b20 dice que hay que esperar 750ms
            # tras pedir conversión antes de leer la ROM
            time.sleep_ms(750)

            # Leemos solo el primer sensor del bus
            temp = self.ds.read_temp(self.roms[0])

            # Validar lecturas erróneas (por ejemplo, cable roto devuelve 85.0C exactos a veces)
            if temp == 85.0:
                print("[DS18B20] ⚠️ Adv: Lectura 85.0C sospechosa (error de alimentación/bus)")

            return temp

        except Exception as e:
            print(f"[DS18B20] Error leyendo temperatura: {e}")
            return None
