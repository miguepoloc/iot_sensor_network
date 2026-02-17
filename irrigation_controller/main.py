import time

# Import configuration
import config
import machine

# Import Core Logic
from core import data_logger, irrigation_logic, telemetry

# Import Drivers
from drivers import bme280, cwt_soil, hd38, rtc_ds1307, sdcard


def main() -> None:
    print(f"🚀 Iniciando Nodo de Riego: {config.NODE_ID}")

    # --- 1. Hardware Initialization ---

    # I2C for RTC and BME280
    i2c: machine.I2C = machine.I2C(0, scl=machine.Pin(config.I2C_SCL), sda=machine.Pin(config.I2C_SDA))

    # RTC
    rtc: rtc_ds1307.RtcDs1307 | None = None
    try:
        rtc = rtc_ds1307.RtcDs1307(i2c)
        print(f"[RTC] Fecha/Hora actual: {rtc.get_timestamp()}")
    except Exception as e:
        print(f"[RTC] Error: {e}")
        rtc = None

    # SD Card
    logger: data_logger.DataLogger | None = None
    try:
        spi: machine.SPI = machine.SPI(
            1,
            baudrate=1000000,
            polarity=0,
            phase=0,
            sck=machine.Pin(config.SPI_SCK),
            mosi=machine.Pin(config.SPI_MOSI),
            miso=machine.Pin(config.SPI_MISO),
        )
        sd: sdcard.SDCard = sdcard.SDCard(spi, machine.Pin(config.SD_CS))
        logger = data_logger.DataLogger(sd)
    except Exception as e:
        print(f"[SD] Error Fatal: {e}")
        logger = None

    # Sensors
    soil_cwt: cwt_soil.CwtSoil = cwt_soil.CwtSoil(
        tx_pin=config.RS485_TX, rx_pin=config.RS485_RX, de_re_pin=config.RS485_DE_RE
    )
    soil_hd38: hd38.HD38 = hd38.HD38(config.HD38_PIN)

    # Actuators
    relay: machine.Pin = machine.Pin(config.RELAY_VALVE_PIN, machine.Pin.OUT)
    relay.value(0)  # Ensure OFF at startup

    # Core Logic
    irrigation_sys: irrigation_logic.IrrigationLogic = irrigation_logic.IrrigationLogic(
        relay, config.MOISTURE_LOW, config.MOISTURE_HIGH
    )
    telemetry_mgr: telemetry.TelemetryManager = telemetry.TelemetryManager(
        config.SIM800_TX, config.SIM800_RX, config.APN, config.SERVER_URL
    )

    # State Variables
    last_send_time: float = 0

    # --- 2. Main Loop ---
    while True:
        try:
            start_time: float = time.time()

            # A. Read Sensors
            print("\n--- Ciclo de Lectura ---")

            # CWT Soil
            soil_data: dict | None = soil_cwt.read_all()
            if not soil_data:
                print("[CWT] Fallo lectura, usando valores vacios")
                soil_data = {"humidity": None, "temperature": None}

            # HD38 (Backup)
            hd38_val: float = soil_hd38.read_percent()

            # BME280
            env_data: dict = bme280.read_bme(i2c)  # Returns dict: {'temp': ..., 'pres': ..., 'hum': ...}

            # Timestamp
            timestamp_str: str = rtc.get_timestamp() if rtc else "NAN"

            # B. Decision Making
            # Priority: Use CWT humidity if available, else HD38
            moisture: float | None = soil_data.get("humidity")
            if moisture is None:
                moisture = hd38_val
                print(f"[Lógica] Usando sensor HD38: {moisture}%")
            else:
                print(f"[Lógica] Usando sensor CWT: {moisture}%")

            is_irrigating: bool = irrigation_sys.process(moisture)

            # C. Data Packet
            packet: dict = {
                "id": config.NODE_ID,
                "timestamp": timestamp_str,
                "soil": {"cwt": soil_data, "hd38_raw": hd38_val},
                "env": env_data,
                "actuators": {"pump": is_irrigating},
            }

            print("Datos:", packet)

            # D. Log to SD (Safety First 💾)
            if logger:
                # Fallback timestamp if no RTC
                if timestamp_str == "NAN":
                    ts = time.localtime()
                    filename: str = f"{ts[0]:04d}-{ts[1]:02d}-{ts[2]:02d}.json"
                else:
                    # Parse timestamp_str "YYYY-MM-DDTHH:MM:SS"
                    try:
                        date_part = timestamp_str.split("T")[0]
                        filename = f"{date_part}.json"
                    except Exception:
                        filename = "data.json"

                logger.save_data(packet, filename)

            # E. Telemetry
            # Send every SEND_INTERVAL_S
            if time.time() - last_send_time > config.SEND_INTERVAL_S:
                print("--- Enviando Telemetría ---")
                if telemetry_mgr.fail_safe_send(packet, logger):
                    last_send_time = time.time()

            end_time: float = time.time()
            elapsed_time: float = end_time - start_time
            print(f"Tiempo de Ciclo: {elapsed_time}s")

            # F. Sleep / Wait
            # If irrigating, we might want shorter sleep to check thresholds
            # But deep sleep would cut power to Relay if not latched.
            # Assuming standard relay -> Light Sleep or time.sleep
            sleep_time: int = config.CHECK_INTERVAL_S

            print(f"Dormitando {sleep_time}s...")
            time.sleep(sleep_time)

        except Exception as e:
            print(f"❌ Error en Loop Principal: {e}")
            time.sleep(10)


if __name__ == "__main__":
    main()
