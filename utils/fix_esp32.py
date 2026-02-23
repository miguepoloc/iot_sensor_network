import time

import serial

PORT = "/dev/cu.usbserial-0001"
BAUD = 115200


def fix_esp32():
    print(f"Abriendo puerto {PORT}...")
    try:
        ser = serial.Serial(PORT, BAUD, timeout=1)
    except Exception as e:
        print(f"Error abriendo el puerto: {e}")
        return

    print("Enviando señales de interrupción (Ctrl+C)...")
    for _ in range(5):
        ser.write(b"\x03")  # Ctrl+C
        time.sleep(0.1)

    time.sleep(0.5)
    ser.reset_input_buffer()

    print("Enviando comandos para borrar main.py...")
    # Entrar al REPL crudo puede fallar si está muy atascado,
    # enviaremos los comandos desde el REPL normal primero.
    ser.write(b"import os\r\n")
    time.sleep(0.1)
    ser.write(b"try: os.remove('main.py')\r\nexcept: pass\r\n")
    time.sleep(0.1)

    # Soft reset
    print("Reiniciando la placa (Ctrl+D)...")
    ser.write(b"\x04")

    time.sleep(1)
    print("Limpiando buffer final:")
    print(ser.read(1000).decode("utf-8", errors="ignore"))

    ser.close()
    print("Hecho. Intenta usar mpremote cp de nuevo.")


if __name__ == "__main__":
    fix_esp32()
