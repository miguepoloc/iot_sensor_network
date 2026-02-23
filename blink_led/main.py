import time

import machine


def blink_led():
    """
    Función de prueba para parpadear el LED integrado de la ESP32.
    En la mayoría de las placas de desarrollo ESP32, el LED integrado está en el pin 2.
    """
    # Configurar el pin 2 como salida
    led = machine.Pin(2, machine.Pin.OUT)

    print("Iniciando prueba de Blink de LED...")

    try:
        while True:
            led.value(1)  # Encender el LED
            print("LED: ONX")
            time.sleep(1)  # Esperar 1 segundo

            led.value(0)  # Apagar el LED
            print("LED: OFFX")
            time.sleep(1)  # Esperar 1 segundo

    except KeyboardInterrupt:
        # Apagar el LED si el usuario detiene la ejecución
        led.value(0)
        print("\nPrueba finalizada.")


if __name__ == "__main__":
    blink_led()
