import machine


class IrrigationLogic:
    def __init__(self, relay_pin: machine.Pin, moisture_low: float, moisture_high: float) -> None:
        self.relay_pin = relay_pin
        self.moisture_low = moisture_low
        self.moisture_high = moisture_high
        self.is_irrigating: bool = False

    def process(self, moisture_level: float | None) -> bool:
        """
        Determine if irrigation should be ON or OFF based on moisture level.
        Returns: True if irrigation is ON, False otherwise.
        """
        if moisture_level is None:
            return False  # Safety default

        if moisture_level < self.moisture_low:
            self.start_irrigation()
        elif moisture_level > self.moisture_high:
            self.stop_irrigation()

        return self.is_irrigating

    def start_irrigation(self) -> None:
        if not self.is_irrigating:
            print("[Riego] Iniciando Riego (Humedad Baja)")
            self.relay_pin.value(1)  # Asumimos lógica positiva (High = ON)
            self.is_irrigating = True

    def stop_irrigation(self) -> None:
        if self.is_irrigating:
            print("[Riego] Deteniendo Riego (Humedad Alta)")
            self.relay_pin.value(0)
            self.is_irrigating = False
