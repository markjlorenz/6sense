import machine

ADDRESS = 0x1c
REG_X   = 0x28 #| 0x80  # OR with 0x80 to set the MSB for reading
REG_Y   = 0x2A #| 0x80  # OR with 0x80 to set the MSB for reading
REG_Z   = 0x2C #| 0x80  # OR with 0x80 to set the MSB for reading
REG_CTL = 0x22
SCALE   = 1 # https://github.com/adafruit/Adafruit_LIS3MDL/blob/master/Adafruit_LIS3MDL.cpp#L188
class LIS3MDL:

    def __init__(self, PINS):
        self.i2c = machine.I2C(1, scl=PINS.SCL, sda=PINS.SDA)

        # Check if the LIS3MDL is connected
        if self.i2c.scan()[0] == ADDRESS:
            print("LIS3MDL found")
        else:
            raise LIS3MDLMissing()

        # Set the device into continuous mode
        self.i2c.writeto_mem(ADDRESS, REG_CTL, b'\x00')

    def read(self):
        x_reading = self.i2c.readfrom_mem(ADDRESS, REG_X, 2)
        y_reading = self.i2c.readfrom_mem(ADDRESS, REG_Y, 2)
        z_reading = self.i2c.readfrom_mem(ADDRESS, REG_Z, 2)

        return (
            self._to_int(x_reading)  / SCALE
            ,self._to_int(y_reading) / SCALE
            ,self._to_int(z_reading) / SCALE
        )

    def read_control(self):
        ctl_value = self.i2c.readfrom_mem(ADDRESS, REG_CTL, 1)
        return "{:08b}".format(ctl_value[0])

    def _to_int(self, reading):
        # need to swap bytes so that the MSByte is on the left.
        b_flipped = bytearray(len(reading))
        for i in range(len(reading)):
            b_flipped[i] = reading[len(reading) - i - 1]
        b_flipped = bytes(b_flipped)
        # return "{:08b} {:08b}".format(ms_reading[0], ms_reading[1])

        # Convert the raw data to a signed 16-bit integer
        b_flipped = b_flipped[0] << 8 | b_flipped[1]
        if b_flipped > 32767:
            b_flipped -= 65536
        return b_flipped

class LIS3MDLMissing(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return self.message
