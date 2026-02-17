# hd38.py Lectura de humedad de suelo con sensor HD-38 analógico


import machine


class HD38:
    def __init__(self, adc_pin: int) -> None:
        adc = machine.ADC(machine.Pin(adc_pin))
        adc.atten(machine.ADC.ATTN_11DB)  # Rango 0-3.3V
        adc.width(machine.ADC.WIDTH_12BIT)  # 0-4095
        self.adc = adc

    def read_percent(self) -> float:
        value = self.adc.read()
        percent = max(0, min(100, (value / 4095) * 100))
        return float(round(percent, 2))
