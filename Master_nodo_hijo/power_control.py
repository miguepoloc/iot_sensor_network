# power_control.py – Control de energía del sensor CWT para nodo hijo

from machine import Pin
import config
import time

# Pin de control (relé o MOSFET)
cwt_power = Pin(config.PIN_CWT_POWER, Pin.OUT)

def power_on_all():
    """Enciende el sensor CWT (activando relé o MOSFET)"""
    print("⚡ Encendiendo sensor CWT...")
    cwt_power.off()
    time.sleep(30)  # Tiempo para estabilizar voltaje

def power_off_all():
    """Apaga el sensor CWT"""
    print("🔌 Apagando sensor CWT...")
    cwt_power.on()
