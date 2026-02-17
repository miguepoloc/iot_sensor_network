# config.py - Configuración del nodo hijo MicroPython (adaptado al nodo padre)

# Identificador del nodo hijo
NODE_ID = "36"

# Archivos locales en la SD
PATH_FILE = "CSVnodoHijo_36.json"
PATH_COPY = "CopiaCSVnodoHijo_36.json"
PATH_TOTAL = "dataTotal_hijo_36.json"

# Wi-Fi del nodo padre (AP)
WIFI_SSID = "NodoPadre_AP"
WIFI_PASS = ""

# Dirección del servidor (nodo padre en modo AP)
SERVER_URL = "http://192.168.4.1"
PATH_DATA = "/data"
PATH_HORA = "/hora"

# Pines I2C para BME280 y RTC
I2C_SCL = 22
I2C_SDA = 21

# Pin ADC para HD-38
HD38_ADC_PIN = 36  # GPIO36 (ADC1_0)

# Pines para UART RS485 (sensor CWT)
UART_RS485_TX = 17
UART_RS485_RX = 16
RS485_DE_RE = 4  # Dirección RS485 (DE + RE)

# Pines SPI para microSD
SD_CS = 5
SPI_SCK = 18
SPI_MOSI = 23
SPI_MISO = 19

# Control de energía (solo sensor CWT)
PIN_CWT_POWER = 33  # Relé o MOSFET para sensor de suelo

# Pines adicionales
LED_PIN = 32
RELAY_CONTROL = 25  # Puede ser para encender LED, u otro control

# Intervalos de muestreo
SAMPLING_TIME_MS = 90000  # 3600000 - 1 hora
WIFI_TIMEOUT_MS = 90000  # 180000 - 3 minutos
