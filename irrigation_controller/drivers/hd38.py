# hd38.py – Lectura de humedad de suelo con sensor HD-38 analógico

from machine import ADC, Pin
import time

class HD38:
    def __init__(self, adc_pin):
        adc = ADC(Pin(adc_pin))
        adc.atten(ADC.ATTN_11DB)  # Rango 0–3.3V
        adc.width(ADC.WIDTH_12BIT)  # 0–4095
        self.adc = adc

    def read_percent(self):
        value = self.adc.read()
        percent = max(0, min(100, (value / 4095) * 100))
        return round(percent, 2)
