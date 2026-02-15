# IoT Sensor Network

Este proyecto implementa una red distribuida de sensores y actuadores basada en microcontroladores ESP32 para aplicaciones de agricultura de precisión y monitoreo ambiental.

## Módulos del Sistema

El repositorio está organizado en tres módulos principales, cada uno diseñado para un rol específico en la red:

### 1. Nodo Padre (Gateway)

**Carpeta**: `Master_nodo_padre/`

* **Función**: Concentrador de datos y pasarela a Internet.
* **Conectividad**: Crea una red Wi-Fi local para los hijos y utiliza un módem SIM800L (LTE/GPRS) para subir datos a la nube.
* **Características**: Almacenamiento local en SD, cola de reintentos para tolerancia a fallos de red.

### 2. Nodo Hijo (Sensor)

**Carpeta**: `Master_nodo_hijo/`

* **Función**: Recolección de datos en campo.
* **Hardware**: Sensores de sueño (CWT RS485), ambientales (BME280) y RTC.
* **Energía**: Operación optimizada con "Deep Sleep" para larga duración de batería.

### 3. Controlador de Riego (Nuevo)

**Carpeta**: `irrigation_controller/`

* **Función**: Sistema autónomo de riego inteligente.
* **Lógica**: Control de electroválvula basado en histéresis de humedad del suelo.
* **Arquitectura**: Diseño modular con drivers desacoplados y "Fail-Safe" telemétrico.

## Estructura del Repositorio

```text
.
├── Master_nodo_padre/      # Código del Gateway
├── Master_nodo_hijo/       # Código del Sensor
├── irrigation_controller/  # Código del Sistema de Riego
└── README.md               # Este archivo
```

## Requisitos

* **Hardware**: ESP32, Módulos SIM800L, Sensores RS485/I2C.
* **Software**: Firmware MicroPython compatible con ESP32.
