# bme280.py – Adaptador para lectura usando el driver bme280_driver.py

from .bme_driver import BME280

def read_bme(i2c):
    try:
        bme = BME280(i2c=i2c)
        temp, pres, hum = bme.read_compensated_data()
        return {
            "temp": round(temp, 2),
            "pres": round(pres, 2),
            "hum": round(hum, 2)
        }
    except Exception as e:
        print("Error leyendo BME280:", e)
        return {"temp": None, "pres": None, "hum": None}

