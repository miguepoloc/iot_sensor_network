# ds1307.py - Driver para reloj RTC DS1307 compatible con MicroPython


class DS1307:
    def __init__(self, i2c, address=0x68):
        self.i2c = i2c
        self.addr = address

    def _bcd2dec(self, bcd):
        return (bcd >> 4) * 10 + (bcd & 0x0F)

    def _dec2bcd(self, dec):
        return ((dec // 10) << 4) + (dec % 10)

    def datetime(self, dt=None):
        if dt is None:
            data = self.i2c.readfrom_mem(self.addr, 0x00, 7)
            second = self._bcd2dec(data[0] & 0x7F)
            minute = self._bcd2dec(data[1])
            hour = self._bcd2dec(data[2])
            weekday = self._bcd2dec(data[3])
            day = self._bcd2dec(data[4])
            month = self._bcd2dec(data[5])
            year = self._bcd2dec(data[6]) + 2000
            return (year, month, day, weekday, hour, minute, second, 0)
        else:
            year, month, day, weekday, hour, minute, second, _ = dt
            self.i2c.writeto_mem(
                self.addr,
                0x00,
                bytes(
                    [
                        self._dec2bcd(second),
                        self._dec2bcd(minute),
                        self._dec2bcd(hour),
                        self._dec2bcd(weekday),
                        self._dec2bcd(day),
                        self._dec2bcd(month),
                        self._dec2bcd(year - 2000),
                    ]
                ),
            )
