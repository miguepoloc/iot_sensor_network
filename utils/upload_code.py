import time

import serial

PORT = "/dev/cu.usbserial-0001"
BAUD = 115200
FILE_PATH = "blink_led/main.py"


def send_file_to_esp32():
    print(f"Abriendo puerto {PORT}...")
    try:
        ser = serial.Serial(PORT, BAUD, timeout=1)
    except Exception as e:
        print(f"Error abriendo el puerto: {e}")
        return

    # Enviar Ctrl+C varias veces para estar seguros de que estamos en >>>
    ser.write(b"\x03")
    ser.write(b"\x03")
    time.sleep(0.5)
    ser.reset_input_buffer()

    print("Enviando código de Python para escribir el archivo...")

    with open(FILE_PATH) as f:
        file_content = f.read()

    # Vamos a usar el "Paste Mode" de MicroPython (Ctrl+E) para evitar auto-indentación
    print("Entrando a Paste Mode en la placa...")
    ser.write(b"\x05")  # Entrar a paste mode (Ctrl+E)
    time.sleep(0.5)

    script_str = repr(file_content)
    # Mandamos un pequeño script en python a ejecutarse del lado de MicroPython
    upload_script = f"with open('main.py', 'w') as f:\r\n    f.write({script_str})\r\n"

    ser.write(upload_script.encode("utf-8"))
    time.sleep(1)

    print("Ejecutando script local en la placa (Ctrl+D)...")
    ser.write(b"\x04")  # Ctrl+D Terminar el paste
    time.sleep(1)

    print("Reiniciando placa (otro Ctrl+D)...")
    ser.write(b"\x04")
    time.sleep(1)

    print("Salida de la ESP32:")
    print(ser.read(1000).decode("utf-8", errors="ignore"))

    ser.close()


if __name__ == "__main__":
    send_file_to_esp32()
