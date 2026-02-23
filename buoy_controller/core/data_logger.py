import os
import time

import config
import machine
from drivers import sdcard


def save_data(data_dict, rtc=None):
    """
    Guarda un diccionario de datos en formato CSV en la tarjeta física SD.
    Monta la SD, escribe los datos y la desmonta para vaciar el caché de memoria (flush)
    y permitir la extracción segura de la SD en cualquier momento.
    """
    print("[SD Logger] Configurando SPI para la SD...")
    spi = machine.SPI(
        1, sck=machine.Pin(config.SPI_SCK), mosi=machine.Pin(config.SPI_MOSI), miso=machine.Pin(config.SPI_MISO)
    )
    cs = machine.Pin(config.SD_CS, machine.Pin.OUT)

    mount_path = "/sd"

    # 1. Forzar desmontaje previo por si quedó enganchada
    try:
        os.umount(mount_path)
    except OSError:
        pass

    # 2. Montar físicamente la SD (pasando por alto la carpeta /sd de la flash interna si existe)
    try:
        sd = sdcard.SDCard(spi, cs)
        vfs = os.VfsFat(sd)
        os.mount(vfs, mount_path)
    except Exception as e:
        print(f"[SD Logger] ERROR montando tarjeta SD de hardware: {e}")
        return False

    # 3. Guardar datos en CSV
    try:
        if rtc and rtc.available:
            timestamp_str = rtc.get_timestamp()
        else:
            timestamp_str = str(time.ticks_ms())

        file_path = f"{mount_path}/{config.FILE_DATA_CSV}"
        print(f"[SD Logger] Escribiendo físicamente CSV en {file_path}")

        # Comprobar si el archivo existe para poner cabeceras
        is_new = False
        try:
            os.stat(file_path)
        except OSError:
            is_new = True

        with open(file_path, "a") as f:
            if is_new:
                f.write("timestamp,temp_agua_c,temp_ambiente_c,humedad_rh,presion_hpa\n")

            # Orden de las columnas a exportar
            row = (
                f"{timestamp_str},{data_dict.get('temp_agua_c', '')},"
                f"{data_dict.get('temp_ambiente_c', '')},{data_dict.get('humedad_rh', '')},"
                f"{data_dict.get('presion_hpa', '')}\n"
            )
            f.write(row)
            f.flush()

        print("[SD Logger] Guardado exitoso")

    except Exception as e:
        print(f"[SD Logger] Excepción escribiendo archivo: {e}")

    # 4. Desmontar obligatoriamente para vaciar buffers a la memoria SD real
    finally:
        try:
            os.umount(mount_path)
            print("[SD Logger] Tarjeta SD desmontada y segura para retirar.")
        except Exception as e:
            print(f"[SD Logger] Error al desmontar: {e}")

    return True


def read_sensors(rtd_sensor=None, i2c_bus=None):
    """Lee los sensores físicos conectados (DS18B20 y BME280)"""
    temp_agua = None
    if rtd_sensor:
        temp_agua = rtd_sensor.read_temperature()

    bme_data = {"temp": None, "hum": None, "pres": None}
    if i2c_bus:
        try:
            from drivers.bme280 import read_bme

            bme_data = read_bme(i2c_bus)
        except ImportError:
            pass

    return {
        "temp_agua_c": temp_agua,
        "temp_ambiente_c": bme_data.get("temp"),
        "humedad_rh": bme_data.get("hum"),
        "presion_hpa": bme_data.get("pres"),
    }
