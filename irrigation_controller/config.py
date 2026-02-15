# config.py - Configuración del Nodo Controlador de Riego
# Define pines, umbrales y parámetros de conexión.

# --- Identificación ---
NODE_ID = "irrigation_ctrl_01"

# --- Conectividad ---
# Wi-Fi (Opcional, si se usa para debug o respaldo)
WIFI_SSID = "MiRedWiFi"
WIFI_PASS = "clave123"

# GSM / GPRS (SIM800L)
APN = "internet.claro.com.co"  # Cambiar según operador
SERVER_URL = "http://tuservidor.com/api/irrigacion/datos"

# --- Pines de Hardware (ESP32) ---

# I2C (RTC DS1307 + BME280)
I2C_SCL = 22
I2C_SDA = 21

# UART para SIM800L
SIM800_TX = 27  # Conectar a RX del SIM800L
SIM800_RX = 26  # Conectar a TX del SIM800L

# UART para Sensor Suelo CWT (RS485)
RS485_TX = 17
RS485_RX = 16
RS485_DE_RE = 4  # Control de flujo RS485

# ADC para Sensor Suelo HD-38 (Respaldo)
HD38_PIN = 36   # VP / ADC1_0

# SPI para Tarjeta SD
SD_CS = 5
SPI_SCK = 18
SPI_MOSI = 23
SPI_MISO = 19

# --- Control de Actuadores ---
RELAY_VALVE_PIN = 25  # Pin que controla la electroválvula (High = ON)

# --- Lógica de Riego ---
# Umbrales de humedad de suelo (%)
# Si baja de LOW -> Activar Riego
# Si sube de HIGH -> Detener Riego
MOISTURE_LOW = 30.0
MOISTURE_HIGH = 70.0

# Intervalos de tiempo
CHECK_INTERVAL_S = 60       # Frecuencia de lectura de sensores (segundos)
SEND_INTERVAL_S = 300       # Frecuencia de envío de datos (segundos) - 5 min
IRRIGATION_MAX_TIME_S = 1800 # Tiempo máximo de riego continuo (seguridad)
