import time


class AtlasRTD:
    def __init__(self, i2c_bus, address=102):
        """
        Inicializa el sensor EZO RTD de Atlas Scientific.
        :param i2c_bus: objeto machine.I2C ya inicializado.
        :param address: Dirección I2C del sensor (por defecto 102 / 0x66).
        """
        self.i2c = i2c_bus
        self.address = address

    def read_temperature(self):
        """
        Envía el comando de lectura ('R'), espera el tiempo adecuado
        y retorna el valor de la temperatura leída como float.
        """
        try:
            # Enviar el comando 'R' para leer
            self.i2c.writeto(self.address, b"R")

            # El manual y código base indican esperar 600ms para lecturas
            time.sleep_ms(600)

            # Solicitar hasta 20 bytes del dispositivo
            data = self.i2c.readfrom(self.address, 20)

            # El primer byte es el código de respuesta
            response_code = data[0]

            if response_code == 1:
                # Éxito: El resto de los bytes son los caracteres de los datos
                # Buscamos hasta encontrar el byte nulo (0x00)
                end_idx = 1
                while end_idx < len(data) and data[end_idx] != 0:
                    end_idx += 1

                # Decodificamos solo los caracteres válidos
                temp_str = data[1:end_idx].decode("utf-8")
                return float(temp_str)

            elif response_code == 2:
                print("[Atlas RTD] Error: Comando fallido.")
            elif response_code == 254:
                print("[Atlas RTD] Error: Lectura pendiente.")
            elif response_code == 255:
                print("[Atlas RTD] Error: No hay datos.")
            else:
                print(f"[Atlas RTD] Error desconocido {response_code}")

        except Exception as e:
            print(f"[Atlas RTD] Excepción I2C: {e}")

        return None

    def sleep(self):
        """Envía el comando para poner a dormir el sensor."""
        try:
            self.i2c.writeto(self.address, b"Sleep")
        except Exception as e:
            print(f"[Atlas RTD] Error poniéndo a dormir: {e}")
