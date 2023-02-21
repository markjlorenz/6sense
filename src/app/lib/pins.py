import machine
import feathers3

class Pins:
    def __init__(self):
        self.NEO_PIXEL = machine.Pin(feathers3.RGB_DATA, machine.Pin.OUT)
        self.SCL = machine.Pin(9)
        self.SDA = machine.Pin(8)
        # For piezo setup
        # self.TACT_X = machine.Pin(12, machine.Pin.OUT)
        # self.TACT_Y = machine.Pin(6, machine.Pin.OUT)
        # self.TACT_Z = machine.Pin(5, machine.Pin.OUT)

        # For TENs setup
        self.TACT_X = machine.Pin(17, machine.Pin.OUT)
        self.TACT_Y = machine.Pin(18, machine.Pin.OUT)
        self.TACT_Z = machine.Pin(14, machine.Pin.OUT)

    def lights_off(self):
        feathers3.led_set(False)
        feathers3.set_ldo2_power(False)
