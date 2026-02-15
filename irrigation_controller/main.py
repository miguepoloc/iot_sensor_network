import time
import machine
import ujson
from machine import I2C, Pin, SoftI2C

# Import configuration
import config

# Import Drivers
from drivers.cwt_soil import CWT_Soil
from drivers.hd38 import HD38
from drivers.bme280 import read_bme
from drivers.ds1307 import DS1307
from drivers.sdcard import SDCard

# Import Core Logic
from core.irrigation_logic import IrrigationLogic
from core.data_logger import DataLogger
from core.telemetry import TelemetryManager

def main():
    print(f"🚀 Iniciando Nodo de Riego: {config.NODE_ID}")

    # --- 1. Hardware Initialization ---
    
    # I2C for RTC and BME280
    i2c = I2C(0, scl=Pin(config.I2C_SCL), sda=Pin(config.I2C_SDA))
    
    # RTC
    try:
        from drivers.rtc_ds1307 import RTC_DS1307
        rtc = RTC_DS1307(i2c)
        print(f"[RTC] Fecha/Hora actual: {rtc.get_timestamp()}")
    except Exception as e:
        print(f"[RTC] Error: {e}")
        rtc = None

    # SD Card
    try:
        spi = machine.SPI(1, baudrate=1000000, polarity=0, phase=0, 
                          sck=Pin(config.SPI_SCK), mosi=Pin(config.SPI_MOSI), miso=Pin(config.SPI_MISO))
        sd = SDCard(spi, Pin(config.SD_CS))
        logger = DataLogger(sd)
    except Exception as e:
        print(f"[SD] Error Fatal: {e}")
        logger = None

    # Sensors
    soil_cwt = CWT_Soil(tx_pin=config.RS485_TX, rx_pin=config.RS485_RX, de_re_pin=config.RS485_DE_RE)
    soil_hd38 = HD38(config.HD38_PIN)

    # Actuators
    relay = Pin(config.RELAY_VALVE_PIN, Pin.OUT)
    relay.value(0) # Ensure OFF at startup

    # Core Logic
    irrigation_sys = IrrigationLogic(relay, config.MOISTURE_LOW, config.MOISTURE_HIGH)
    telemetry = TelemetryManager(config.SIM800_TX, config.SIM800_RX, config.APN, config.SERVER_URL)

    # State Variables
    last_send_time = 0
    
    # --- 2. Main Loop ---
    while True:
        try:
            start_time = time.time()
            
            # A. Read Sensors
            print("\n--- Ciclo de Lectura ---")
            
            # CWT Soil
            soil_data = soil_cwt.read_all()
            if not soil_data:
                print("[CWT] Fallo lectura, usando valores vacios")
                soil_data = {"humidity": None, "temperature": None}
            
            # HD38 (Backup)
            hd38_val = soil_hd38.read_percent()
            
            # BME280
            env_data = read_bme(i2c) # Returns dict: {'temp': ..., 'pres': ..., 'hum': ...}
            
            # Timestamp
            timestamp_str = rtc.get_timestamp() if rtc else "NAN"

            # B. Decision Making
            # Priority: Use CWT humidity if available, else HD38
            moisture = soil_data.get("humidity")
            if moisture is None:
                moisture = hd38_val
                print(f"[Lógica] Usando sensor HD38: {moisture}%")
            else:
                print(f"[Lógica] Usando sensor CWT: {moisture}%")

            is_irrigating = irrigation_sys.process(moisture)

            # C. Data Packet
            packet = {
                "id": config.NODE_ID,
                "timestamp": timestamp_str,
                "soil": {
                    "cwt": soil_data,
                    "hd38_raw": hd38_val
                },
                "env": env_data,
                "actuators": {
                    "pump": is_irrigating
                }
            }
            
            print("Datos:", packet)

            # D. Log to SD (Safety First 💾)
            if logger:
                filename = "{:04d}-{:02d}-{:02d}.json".format(ts[0], ts[1], ts[2])
                logger.save_data(packet, filename)

            # E. Telemetry
            # Send every SEND_INTERVAL_S
            if time.time() - last_send_time > config.SEND_INTERVAL_S:
                print("--- Enviando Telemetría ---")
                if telemetry.fail_safe_send(packet, logger):
                    last_send_time = time.time()
            
            # F. Sleep / Wait
            # If irrigating, we might want shorter sleep to check thresholds
            # But deep sleep would cut power to Relay if not latched.
            # Assuming standard relay -> Light Sleep or time.sleep
            sleep_time = config.CHECK_INTERVAL_S
            
            print(f"Dormitando {sleep_time}s...")
            time.sleep(sleep_time)

        except Exception as e:
            print(f"❌ Error en Loop Principal: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()
