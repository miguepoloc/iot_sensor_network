import sys
from unittest.mock import MagicMock

# --- 1. CONFIGURACIÓN DE MOCKS (Simulación de Hardware) ---

# Mockear 'machine' (MicroPython)
mock_machine = MagicMock()
sys.modules["machine"] = mock_machine

# Mockear 'ds1307' (Librería del driver)
# Necesitamos mockear el módulo completo antes de que rtc_ds1307 lo importe
mock_ds1307_module = MagicMock()
sys.modules["irrigation_controller.drivers.ds1307"] = mock_ds1307_module

# Crear una clase falsa para simular el comportamiento del DS1307 real
class MockDS1307Driver:
    def __init__(self, i2c):
        self.i2c = i2c
        self.current_time = (2023, 10, 25, 2, 12, 30, 45, 0) # Fecha fija para pruebas

    def datetime(self, new_dt=None):
        if new_dt:
            print(f"[MOCK] Configurando hora del RTC a: {new_dt}")
            self.current_time = new_dt
            return None
        return self.current_time

# Asignar la clase al módulo mockeado
mock_ds1307_module.DS1307 = MockDS1307Driver


# --- 2. IMPORTAR EL CÓDIGO A PROBAR ---
# Ahora que el entorno está "trucado", importamos la clase real
import os
sys.path.append(os.getcwd()) # Asegurar que encuentra los paquetes

try:
    from irrigation_controller.drivers.rtc_ds1307 import RtcDs1307
except ImportError:
    # Fallback si se ejecuta desde otra ruta
    sys.path.append(os.path.join(os.getcwd(), 'irrigation_controller', 'drivers'))
    from rtc_ds1307 import RtcDs1307


# --- 3. PRUEBA LÓGICA ---
def test_simulacion_rtc():
    print("\n🔹 Iniciando prueba simulada del RTC...")

    # 3.1 Simular Bus I2C
    mock_i2c = MagicMock()
    # Simular que 'scan()' encuentra la dirección 0x68 (104)
    mock_i2c.scan.return_value = [0x68] 

    # 3.2 Instanciar el driver con el I2C simulado
    rtc = RtcDs1307(i2c=mock_i2c)

    # Verificar si se detectó (se creó el objeto rtc interno)
    if rtc.rtc:
        print("✅ ÉXITO: El driver detectó el RTC simulado.")
    else:
        print("❌ ERROR: El driver no inicializó el objeto RTC.")

    # 3.3 Probar lectura de hora
    timestamp = rtc.get_timestamp()
    print(f"📡 Timestamp leída: {timestamp}")

    esperado = "2023-10-25T12:30:45"
    if timestamp == esperado:
        print("✅ ÉXITO: El formato del timestamp es correcto.")
    else:
        print(f"❌ ERROR: Se esperaba {esperado}, se recibió {timestamp}")

    # 3.4 Probar escritura de hora
    print("✍️ Intentando configurar nueva hora...")
    resultado = rtc.set_time(2024, 1, 1, 0, 0, 0)
    
    if resultado:
        print("✅ ÉXITO: set_time() devolvió True.")
    else:
        print("❌ ERROR: set_time() falló.")

if __name__ == "__main__":
    test_simulacion_rtc()
