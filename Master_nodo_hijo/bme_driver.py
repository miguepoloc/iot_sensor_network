# bme_driver.py - Driver para sensor BME280 compatible con MicroPython
# Basado en la librería oficial BME280 adaptada para ESP32

import struct

from machine import I2C

BME280_I2C_ADDR = 0x76


class BME280:
    def __init__(self, i2c: I2C, address=BME280_I2C_ADDR):
        self.i2c = i2c
        self.address = address
        self._load_calibration_params()
        self._configure()

    def _read8(self, register):
        return int.from_bytes(self.i2c.readfrom_mem(self.address, register, 1), "little")

    def _read16(self, register):
        return int.from_bytes(self.i2c.readfrom_mem(self.address, register, 2), "little")

    def _read_s16(self, register):
        return struct.unpack("<h", self.i2c.readfrom_mem(self.address, register, 2))[0]

    def _load_calibration_params(self):
        self.dig_T1 = self._read16(0x88)
        self.dig_T2 = self._read_s16(0x8A)
        self.dig_T3 = self._read_s16(0x8C)
        self.dig_P1 = self._read16(0x8E)
        self.dig_P2 = self._read_s16(0x90)
        self.dig_P3 = self._read_s16(0x92)
        self.dig_P4 = self._read_s16(0x94)
        self.dig_P5 = self._read_s16(0x96)
        self.dig_P6 = self._read_s16(0x98)
        self.dig_P7 = self._read_s16(0x9A)
        self.dig_P8 = self._read_s16(0x9C)
        self.dig_P9 = self._read_s16(0x9E)
        self.dig_H1 = self._read8(0xA1)
        self.dig_H2 = self._read_s16(0xE1)
        self.dig_H3 = self._read8(0xE3)
        e4 = self._read8(0xE4)
        e5 = self._read8(0xE5)
        e6 = self._read8(0xE6)
        self.dig_H4 = (e4 << 4) | (e5 & 0x0F)
        self.dig_H5 = (e6 << 4) | (e5 >> 4)
        self.dig_H6 = self._read8(0xE7)

    def _configure(self):
        self.i2c.writeto_mem(self.address, 0xF2, b"\x01")  # Humidity oversampling x1
        self.i2c.writeto_mem(self.address, 0xF4, b"\x27")  # Pressure and temp oversampling x1, mode normal
        self.i2c.writeto_mem(self.address, 0xF5, b"\xa0")  # Config register

    def read_raw_data(self):
        data = self.i2c.readfrom_mem(self.address, 0xF7, 8)
        raw_pres = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
        raw_temp = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)
        raw_hum = (data[6] << 8) | data[7]
        return raw_temp, raw_pres, raw_hum

    def compensate_temperature(self, adc_t):
        var1 = (((adc_t >> 3) - (self.dig_T1 << 1)) * self.dig_T2) >> 11
        var2 = (((((adc_t >> 4) - self.dig_T1) * ((adc_t >> 4) - self.dig_T1)) >> 12) * self.dig_T3) >> 14
        self.t_fine = var1 + var2
        temp = (self.t_fine * 5 + 128) >> 8
        return temp / 100

    def compensate_pressure(self, adc_p):
        var1 = self.t_fine - 128000
        var2 = var1 * var1 * self.dig_P6
        var2 = var2 + ((var1 * self.dig_P5) << 17)
        var2 = var2 + (self.dig_P4 << 35)
        var1 = ((var1 * var1 * self.dig_P3) >> 8) + ((var1 * self.dig_P2) << 12)
        var1 = (((1 << 47) + var1) * self.dig_P1) >> 33
        if var1 == 0:
            return 0  # avoid exception caused by division by zero
        p = 1048576 - adc_p
        p = (((p << 31) - var2) * 3125) // var1
        var1 = (self.dig_P9 * (p >> 13) * (p >> 13)) >> 25
        var2 = (self.dig_P8 * p) >> 19
        p = ((p + var1 + var2) >> 8) + (self.dig_P7 << 4)
        return p / 25600

    def compensate_humidity(self, adc_h):
        v_x1_u32r = self.t_fine - 76800
        v_x1_u32r = ((((adc_h << 14) - (self.dig_H4 << 20) - (self.dig_H5 * v_x1_u32r)) + 16384) >> 15) * (
            (
                (((((v_x1_u32r * self.dig_H6) >> 10) * (((v_x1_u32r * self.dig_H3) >> 11) + 32768)) >> 10) + 2097152)
                * self.dig_H2
                + 8192
            )
            >> 14
        )
        v_x1_u32r = v_x1_u32r - (((((v_x1_u32r >> 15) * (v_x1_u32r >> 15)) >> 7) * self.dig_H1) >> 4)
        v_x1_u32r = max(0, min(v_x1_u32r, 419430400))
        return (v_x1_u32r >> 12) / 1024.0

    def read_compensated_data(self):
        raw_temp, raw_pres, raw_hum = self.read_raw_data()
        temp = self.compensate_temperature(raw_temp)
        pres = self.compensate_pressure(raw_pres)
        hum = self.compensate_humidity(raw_hum)
        return temp, pres, hum
