# power_control.py - Control de energía de periféricos de alto consumo

import time

import config
from machine import Pin

# Pines de control de energía (usados para relés o MOSFETs)
sim800_power = Pin(config.PIN_SIM800L_POWER, Pin.OUT)
cwt_power = Pin(config.PIN_CWT_POWER, Pin.OUT)


def power_on_all():
    """Enciende todos los módulos conectados a control de energía."""
    print("⚡ Encendiendo SIM800L y sensor CWT...")
    sim800_power.on()
    cwt_power.on()
    time.sleep(2)  # Espera para que se estabilicen


def power_off_all():
    """Apaga todos los módulos conectados a control de energía."""
    print("🔌 Apagando SIM800L y sensor CWT...")
    sim800_power.off()
    cwt_power.off()
