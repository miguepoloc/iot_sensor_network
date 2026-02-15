# Irrigation Controller Module

This module implements a Smart Irrigation System using ESP32, CWT Soil Sensors, and SIM800L LTE connectivity.

## Directory Structure

```bash
irrigation_controller/
├── main.py                 # Entry point
├── config.py               # Configuration (Pins, Thresholds)
├── core/                   # Logic Modules
│   ├── irrigation_logic.py # Hysteresis control
│   ├── data_logger.py      # SD Card storage
│   └── telemetry.py        # SIM800L management
├── drivers/                # Hardware Drivers
└── lib/                    # Utilities
```

## Features

* **Hysteresis Control**: Prevents valve from toggling rapidly around the threshold.
* **Offline First**: Data is always saved to SD card before transmission.
* **Fail-Safe Telemetry**: Tries to send data via LTE, logs failures.
* **Modular Drivers**: Drivers are injected with dependencies (Pins, I2C), not hardcoded.

## Setup

1. Connect hardware according to pins defined in `config.py`.
2. Upload the entire `irrigation_controller` folder to the ESP32.
3. Reset the board. The system auto-starts via `main.py` (if renamed to `/main.py` or called from boot).

## Configuration

Edit `config.py` to change:

* `MOISTURE_LOW` / `MOISTURE_HIGH`: Irrigation thresholds.
* `CHECK_INTERVAL_S`: How often to read sensors.
* `SEND_INTERVAL_S`: How often to upload data.
