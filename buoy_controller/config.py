# config.py - Configuración de la Boya Oceanográfica
# Este archivo concentra todos los parámetros, pines y configuraciones lógicas
# para no tener que editar el código principal al hacer cambios en campo.

# --- Identificación del Nodo ---
NODE_ID = "buoy_01"

# --- Configuración del Access Point (AP) para el control web ---
AP_SSID = "Boya_Control_AP"
AP_PASS = "secreto1234"  # Cambia por una contraseña de 8 caract. mínimo
AP_IP = "192.168.4.1"  # Por defecto de MicroPython, donde estará la interfaz UI

# --- Configuración Tiempos de Inmersión (Misión Automática) ---
INMERSION_TIME_S = 1  # Cuántos segundos toma el motor en llevar el sensor abajo
BOTTOM_PAUSE_S = 3  # Cuánto tiempo se queda abajo para estabilizar datos
EXTRACTION_TIME_S = 1  # Cuántos segundos toma subir los sensores (usualmente igual al de bajada)
WAIT_BETWEEN_CYCLES_S = 5  # Tiempo en reposo entre misiones (Ej: 300 = 5 Minutos para evitar Biofouling)
MOTOR_TIMEOUT_S = 30  # Por seguridad: tiempo máximo que el motor puede estar encendido seguido

# --- Configuración Lógica SD ---
FILE_DATA_CSV = "dataTotal_boya_01.csv"

# --- Asignación de Pines Físicos (Placa: Master_nodo_hijo ESP32) ---

# --- Configuración del Controlador de Motor ---
# Opciones soportadas: "L298N", "HW166", "SERVO"
MOTOR_DRIVER_TYPE = "SERVO"

# Pines si usas Puente H clásico L298N (o módulo de 2 relés)
L298N_PIN_UP = 17  # Pin de dirección 1 (Adelante/Subir)
L298N_PIN_DOWN = 16  # Pin de dirección 2 (Atrás/Bajar)

# Pines si usas módulo HW-166 (TB6612FNG)
HW166_PIN_AIN1 = 16  # Dirección A es el cable verde, el cercano a la SD
HW166_PIN_AIN2 = 17  # Dirección B es el cable azul, el que está más cerca del borde
HW166_PIN_PWM = 4  # Pin que entrega la potencia (PWM)

# Pines si usas Servomotor (SG90 o rotación continua)
SERVO_PIN = 33  # Pin de señal PWM (naranja/amarillo)

# Sensores de Temperatura
DS18B20_PIN = 17

# Sensores I2C (RTC, Sensores extra fututos)
I2C_SCL = 22
I2C_SDA = 21

# Tarjeta SD / SPI
SD_CS = 5
SPI_SCK = 18
SPI_MOSI = 23
SPI_MISO = 19
