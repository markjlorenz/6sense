import machine
import ustruct

ADDRESS   = 0x1c
REG_X     = 0x28 #| 0x80  # OR with 0x80 to set the MSB for reading
REG_Y     = 0x2A #| 0x80  # OR with 0x80 to set the MSB for reading
REG_Z     = 0x2C #| 0x80  # OR with 0x80 to set the MSB for reading
REG_CTL_3 = 0x22
REG_CTL_1 = 0x20
SCALE     = 1 # https://github.com/adafruit/Adafruit_LIS3MDL/blob/master/Adafruit_LIS3MDL.cpp#L188

class LIS3MDL:

    def __init__(self, PINS):
        self.i2c = machine.I2C(1, scl=PINS.SCL, sda=PINS.SDA)

        # Check if the LIS3MDL is connected
        if self.i2c.scan()[0] == ADDRESS:
            print("LIS3MDL found")
        else:
            raise LIS3MDLMissing()

        # Set the device into continuous mode
        self.i2c.writeto_mem(ADDRESS, REG_CTL_3, b'\x00')

        # Enable high output data rate
        self.i2c.writeto_mem(
            ADDRESS,
            REG_CTL_1,
            (0b00011100).to_bytes(1, 'big')
        )

    def read(self):
        x_reading = self.i2c.readfrom_mem(ADDRESS, REG_X, 2)
        y_reading = self.i2c.readfrom_mem(ADDRESS, REG_Y, 2)
        z_reading = self.i2c.readfrom_mem(ADDRESS, REG_Z, 2)

        return (
            self._from_bytes(x_reading) / SCALE
            ,self._from_bytes(y_reading) / SCALE
            ,self._from_bytes(z_reading) / SCALE
        )


    def _from_bytes(self, value):
        return ustruct.unpack("<h", value)[0]

class LIS3MDLMissing(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return self.message
