import sys
sys.path.append('/remote/lib')

import time, gc, os
import neopixel
import feathers3

import machine
import uasyncio as asyncio

from lis3mdl import LIS3MDL
from tact import Tact
from ble_services import BLEService

# Define pins
class Pins:
    def __init__(self):
        self.NEOPIXEL = machine.Pin(13)
        self.SCL = machine.Pin(9)
        self.SDA = machine.Pin(8)
        self.TACT_X = machine.Pin(12, machine.Pin.OUT)
        self.TACT_Y = machine.Pin(6, machine.Pin.OUT)
        self.TACT_Z = machine.Pin(5, machine.Pin.OUT)
PINS = Pins()

# Create a NeoPixel instance
# Brightness of 0.3 is ample for the 1515 sized LED
pixel = neopixel.NeoPixel(PINS.NEOPIXEL, 1)

# Say hello
print("\nHello from FeatherS3!")
print("------------------\n")

lis3mdl = LIS3MDL(machine.I2C(1, scl=PINS.SCL, sda=PINS.SDA))

pin_x = Tact(PINS.TACT_X)
pin_y = Tact(PINS.TACT_Y)
pin_z = Tact(PINS.TACT_Z)

async def drive(pin):
    while True:
        # turn the pin on
        pin.pin.value(True)
        await asyncio.sleep(pin.half_period)

        # turn the pin off
        pin.pin.value(False)
        await asyncio.sleep(pin.half_period)

async def update():
    while True:
        x, y, z = lis3mdl.read()
        # print("Magnetic field: ({}, {}, {})".format(x, y, z))

        pin_x.half_period = x
        pin_y.half_period = y
        pin_z.half_period = z

        # pin_x.half_period = 0 if x == 0 else 1 / math.pow(x * pre_scale_factor, scale_exponent) * 10
        # pin_y.half_period = 0 if y == 0 else 1 / math.pow(y * pre_scale_factor, scale_exponent) * 10
        # pin_z.half_period = 0 if z == 0 else 1 / math.pow(z * pre_scale_factor, scale_exponent) * 10

        print("Frequency: ({}, {}, {})".format(
            pin_x.hz
            ,pin_y.hz
            ,pin_z.hz
            # 0 if pin_x.half_period == 0 else 1/pin_x.half_period,
            # 0 if pin_y.half_period == 0 else 1/pin_y.half_period,
            # 0 if pin_z.half_period == 0 else 1/pin_z.half_period,
        ))
        await asyncio.sleep(0.5)

asyncio.run(asyncio.gather(
    drive(pin_x)
    ,drive(pin_y)
    ,drive(pin_z)
    ,update()
    ,BLEService(pin_x, pin_y, pin_z).main()
))


# half_period = 0.1
# while True:
#     # # turn the pin on
#     # pin_z.pin.value = True
#     # time.sleep(half_period)
#     #
#     # # turn the pin off
#     # pin_z.pin.value = False
#     # time.sleep(half_period)
#
#
#     x, y, z = lis3mdl.read()
#     # x, y, z = lis3mdl.magnetic
#     print("Magnetic field: ({}, {}, {})".format(x, y, z))
#     # half_period = 1 / math.pow(-z, 2) * 10
#     time.sleep(1)
#
