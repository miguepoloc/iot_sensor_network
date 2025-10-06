import time
from cwt_soil import CWT_Soil

def main():
    print("Boot: ESP32 inicializado correctamente\n")

    # Pines según tu wiring (TX=17, RX=16, DE/RE=4)
    sensor = CWT_Soil(tx_pin=17, rx_pin=16, de_re_pin=4, baudrate=4800, addr=1, parity=None)

    while True:
        data = sensor.read_all()
        print("Lectura de suelo:")
        for k, v in data.items():
            if v is not None:
                print(f"  {k}: {v}")
            else:
                print(f"  {k}: ⚠️ sin datos")
        print("\n--- Ciclo completo ---\n")
        time.sleep(5)

if __name__ == "__main__":
    main()
