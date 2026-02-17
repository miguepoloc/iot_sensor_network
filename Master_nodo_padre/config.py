# config.py - Parámetros de configuración del nodo padre (MicroPython)

# Identificador del nodo
NODE_ID = "18257"

# Pines I2C (RTC y BME280)
I2C_SCL = 22
I2C_SDA = 21

# Pines ADC (HD-38 analógico)
HD38_ADC_PIN = 36  # GPIO36 (VP) - ADC1_0

# UART para sensor CWT (RS485 Modbus)
UART_RS485_TX = 17
UART_RS485_RX = 16
RS485_DE_RE = 4  # Control dirección del MAX485

# UART para SIM800L (LTE)
SIM800_TX = 26  # RX del ESP32
SIM800_RX = 27  # TX del ESP32

# Pines SPI para microSD
SD_CS = 5
SPI_SCK = 18
SPI_MOSI = 23
SPI_MISO = 19

# Pines para controlar energía (relés o MOSFETs)
PIN_SIM800L_POWER = 25  # GPIO que enciende el relé del SIM800L
PIN_CWT_POWER = 33  # GPIO que enciende el relé del sensor CWT

# Red Wi-Fi (como Access Point para nodos hijos)
AP_SSID = "NodoPadre_AP"
AP_PASSWORD = "12345678"

# URL del servidor al que se envían los datos por LTE
SERVER_URL = "https://webhook.site/0979b11a-2219-480a-a5b8-f025447ad0e5"

# APN del operador móvil (cambiar según operador)
APN = "internet.comcel.com.co"

# Intervalo de medición (en segundos)
READ_INTERVAL = 30  # 1800 - 30 minutos

# Frecuencia del LoRa (opcional si se usa LoRa en el futuro)
LORA_FREQ = 915e6
