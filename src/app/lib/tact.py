import math
import uasyncio as asyncio

SCALE_EXPONENT = 1
PRE_SCALE_FACTOR = 20_000 / 32_768
BOOST = 1

# PRE_SCALE_FACTOR = 1.01
# BOOST = 10_000

class Tact:
    def __init__(self, board_pin):
        self.pin = board_pin
        self._half_period = 0
        self._hz = 0

    @property
    def half_period(self):
        return self._half_period

    @half_period.setter
    def half_period(self, value):
        self._half_period = 0 if value == 0 else 1 / math.pow(abs(value) * PRE_SCALE_FACTOR, SCALE_EXPONENT) * BOOST
        self._hz = 0 if self._half_period == 0 else 1/self._half_period

    @property
    def hz(self):
        return self._hz

    @hz.setter
    def hz(self, value):
        raise NotImplemented("Shouldn't be setting this value directly")

    async def drive(self):
        while True:
            # turn the pin on
            self.pin.value(True)
            await asyncio.sleep(self.half_period)

            # turn the pin off
            self.pin.value(False)
            await asyncio.sleep(self.half_period)
