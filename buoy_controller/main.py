import config
import machine
import uasyncio as asyncio
from core.data_logger import read_sensors, save_data
from core.motor_control import BaseMotorController, MotorHW166, MotorL298N, MotorServo
from core.web_server import SimpleWebServer
from drivers.ds18b20 import DS18B20Sensor
from drivers.rtc_ds1307 import RtcDs1307

# Variables globales de control
motor: BaseMotorController = None
server = None
sensor_temp = None
sensor_rtc = None
sw_top = None
sw_bottom = None
mission_active = False  # Evita lanzar dos misiones automáticas al tiempo


async def buoy_mission_cycle():
    """
    Corutina principal que controla la inmersión automática
    Baja, espera, toma datos, sube y descansa.
    """
    global mission_active, sensor_temp, sensor_rtc, motor, sw_top, sw_bottom
    while True:
        try:
            if not mission_active:
                mission_active = True
                print("\n--- [Misión] Iniciando nuevo ciclo automático ---")

                # 1. Bajar Sensores
                print("[Misión] Bajando sensores hasta tocar fin de carrera fondo (Bottom)...")
                motor.down()

                # Bucle asíncrono esperando el fin de carrera (asume presionado = 0)
                timeout_tenths = 0
                max_tenths = config.MOTOR_TIMEOUT_S
                while sw_bottom.value() == 1 and timeout_tenths < max_tenths:
                    await asyncio.sleep_ms(100)
                    timeout_tenths += 1

                if timeout_tenths >= max_tenths:
                    print("[Misión] ⚠️ Timeout de seguridad alcanzado al BAJAR!")

                motor.stop()

                # 2. Descansar en el fondo para equilibrar lectura
                print(f"[Misión] Pausando en el fondo {config.BOTTOM_PAUSE_S}s...")
                await asyncio.sleep(config.BOTTOM_PAUSE_S)

                # 3. Leer y Guardar Datos
                print("[Misión] Leyendo sensores...")
                datos = read_sensors(sensor_temp, i2c)
                save_data(datos, rtc=sensor_rtc)

                # 4. Subir Sensores y Recoger cable
                print("[Misión] Subiendo sensores hasta tocar fin de carrera tope (Top)...")
                motor.up()

                # Bucle asíncrono esperando el fin de carrera tope
                timeout_tenths = 0
                while sw_top.value() == 1 and timeout_tenths < max_tenths:
                    await asyncio.sleep_ms(100)
                    timeout_tenths += 1

                if timeout_tenths >= max_tenths:
                    print("[Misión] ⚠️ Timeout de seguridad alcanzado al SUBIR!")

                motor.stop()

                print(f"[Misión] Ciclo Terminado. Durmiendo por {config.WAIT_BETWEEN_CYCLES_S}s.")
                mission_active = False

            # 5. Esperar hasta el próximo ciclo largo
            await asyncio.sleep(config.WAIT_BETWEEN_CYCLES_S)

        except Exception as e:
            print(f"[Misión] Error en el ciclo: {e}")
            motor.stop()
            mission_active = False
            await asyncio.sleep(10)  # Reintento si algo falla muy feo


async def web_server_task():
    """
    Corutina secundaria que atiende a los clientes WiFi sin bloquear el motor.
    """
    global server
    print("[Main] Inicializando Web Server Task...")
    while True:
        server.handle_request()
        # Cede el control rápido (10 milisegundos) al sistema para otros procesos
        await asyncio.sleep_ms(10)


async def main():
    """
    Entrypoint Asíncrono
    """
    global motor, server, sensor_temp, sensor_rtc, i2c, sw_top, sw_bottom
    print("\n==============================")
    print("Iniciando Controlador de Boya")
    print(f"ID Nodo: {config.NODE_ID}")
    print("==============================\n")

    # Inyección de Dependencias del Controlador del Motor
    driver_type = getattr(config, "MOTOR_DRIVER_TYPE", "HW166")
    if driver_type == "L298N":
        print("[Setup] Usando Driver L298N")
        motor = MotorL298N(pin_up=config.L298N_PIN_UP, pin_down=config.L298N_PIN_DOWN)
    elif driver_type == "HW166":
        print("[Setup] Usando Driver HW-166")
        motor = MotorHW166(pin_ain1=config.HW166_PIN_AIN1, pin_ain2=config.HW166_PIN_AIN2, pin_pwm=config.HW166_PIN_PWM)
    elif driver_type == "SERVO":
        print("[Setup] Usando Driver de Servomotor SG90 (Pin de señal PWM)")
        motor = MotorServo(pin_signal=config.SERVO_PIN)
    else:
        raise ValueError(f"Driver de motor '{driver_type}' no soportado")

    # Iniciar Reloj ds1307 (si está disponible en I2C)
    print("[Setup] Inicializando I2C y RTC...")
    try:
        i2c = machine.SoftI2C(scl=machine.Pin(config.I2C_SCL), sda=machine.Pin(config.I2C_SDA))
        sensor_rtc = RtcDs1307(i2c)
    except Exception as e:
        print(f"[Setup] Error iniciando buses I2C: {e}")
        sensor_rtc = None

    # Iniciar Sensor de Temperatura DS18B20 (1-Wire)
    print("[Setup] Inicializando Sensor Temp DS18B20...")
    try:
        sensor_temp = DS18B20Sensor(config.DS18B20_PIN)
    except Exception as e:
        print(f"[Setup] Error iniciando sensor temp: {e}")
        sensor_temp = None

    # Iniciar Sensores de Fin de Carrera (Limit Switches)
    print("[Setup] Inicializando Sensores de Fin de Carrera (Pull-Up)...")
    sw_top = machine.Pin(config.LIMIT_SWITCH_TOP, machine.Pin.IN, machine.Pin.PULL_UP)
    sw_bottom = machine.Pin(config.LIMIT_SWITCH_BOTTOM, machine.Pin.IN, machine.Pin.PULL_UP)

    # Iniciar servidor (el AP ya fue creado por boot.py en segundo plano)
    server = SimpleWebServer(motor_controller=motor, port=80, sensor=sensor_temp)
    server.start()

    print("[Main] uasyncio loop arrancando...")
    # Crear tareas paralelas concurrentes
    asyncio.create_task(web_server_task())
    asyncio.create_task(buoy_mission_cycle())

    # Mantener el programa principal corriendo
    while True:
        await asyncio.sleep(1)


# Punto de entrada de MicroPython
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nPrograma detenido por usuario.")
        if motor:
            motor.stop()
