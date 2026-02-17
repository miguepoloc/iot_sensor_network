from drivers import sim800l


class TelemetryManager:
    def __init__(self, tx_pin: int, rx_pin: int, apn: str, server_url: str) -> None:
        self.modem = sim800l.SIM800L(tx_pin, rx_pin, apn, server_url)

    def fail_safe_send(self, data: dict, logger) -> bool:
        """
        Tries to send data via LTE. If fails, ensures data is logged (already logged by main, but double check).
        Actually, main logs first. This just sends.
        Returns True if sent, False if failed.
        """
        print("[Telemetria] Iniciando envio...")
        if self.modem.send_json(data):
            print("[Telemetria] Envio exitoso.")
            return True
        else:
            print("[Telemetria] Fallo el envio.")
            return False
