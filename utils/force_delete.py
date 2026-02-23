import time

import serial


def force_delete():
    print("Conectando al puerto...")
    try:
        s = serial.Serial("/dev/cu.usbserial-0001", 115200, timeout=0.1)
    except Exception as e:
        print(f"Error: {e}")
        return

    print("Interrumpiendo ejecución...")
    for _ in range(50):
        s.write(b"\x03")
        out = s.read(100)
        if b">>>" in out:
            print("REPL interactivo alcanzado.")
            break
        time.sleep(0.05)

    print("Borrando main.py...")
    s.write(b"import os\r\ntry:\n    os.remove('main.py')\nexcept:\n    pass\r\n")
    time.sleep(1)

    print("Reiniciando...")
    s.write(b"\x04")
    time.sleep(1)
    print("Salida final:")
    print(s.read(1000).decode("utf-8", errors="ignore"))
    s.close()


if __name__ == "__main__":
    force_delete()
