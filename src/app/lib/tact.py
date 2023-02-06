import math

SCALE_EXPONENT = 2
# PRE_SCALE_FACTOR = 1.01
PRE_SCALE_FACTOR = 0.9

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
        self._half_period = 0 if value == 0 else 1 / math.pow(value * PRE_SCALE_FACTOR, SCALE_EXPONENT) * 10
        self._hz = 0 if self._half_period == 0 else 1/self._half_period

    @property
    def hz(self):
        return self._hz

    @hz.setter
    def hz(self, value):
        raise NotImplemented("Shouldn't be setting this value directly")
