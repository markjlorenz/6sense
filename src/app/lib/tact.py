import math
import uasyncio as asyncio

SCALE_EXPONENT   = 1
BOOST            = 1
OFFSET           = 10

# For piezo
#PRE_SCALE_FACTOR = 20_000 / 32_768

# For TENs
PRE_SCALE_FACTOR = 100 / 32_768

# PRE_SCALE_FACTOR = 1.01
# BOOST = 10_000

# Default value, can be overriden
#
# As suggested by doi:10.1088/1741-2560/13/4/046014
# they recommend 200us, but I think the smallest resolution the micropython
# can get is 1 ms.
PULSE_WIDTH = 1 # ms

class Tact:
    def __init__(self, board_pin):
        self.pulse_width = PULSE_WIDTH
        self.pin = board_pin
        self._half_period = 0
        self._hz = 0

    @property
    def half_period(self):
        return self._half_period

    @half_period.setter
    def half_period(self, value):
        self._half_period = 1 / OFFSET if value == 0 else 1 / (math.pow(abs(value) * PRE_SCALE_FACTOR, SCALE_EXPONENT) * BOOST + OFFSET)
        self._hz = 0 if self._half_period == 0 else 1 / self._half_period

    @property
    def hz(self):
        return self._hz

    @hz.setter
    def hz(self, value):
        raise NotImplemented("Shouldn't be setting this value directly")

    async def drive(self):
        while True:
            self.pin.value(True)
            # Scheduler will not yield on `sleep_ms`: https://github.com/peterhinch/micropython-async/blob/master/v3/docs/TUTORIAL.md#23-delays
            await asyncio.sleep_ms(self.pulse_width)

            self.pin.value(False)
            # Scheduler WILL yield on `sleep`
            off_seconds = (2 * self.half_period) - (self.pulse_width / 1_000_000)
            await asyncio.sleep(off_seconds)
