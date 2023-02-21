# Meaning of the lights:
# - When the neopixel is cycling the color wheel, BLE is enabled.
# - If the LED is blinking fast (0.25s period), then the LIS3MDL is missing.
# - If the blue LED is blinking slow (1s period), then the code crashed.
# - If the LIS3MDL is plugged back in, no lights will be on.

import uasyncio as asyncio

from lis3mdl import LIS3MDL
from tact import Tact
from ble_services import BLEService
from pins import Pins
import error_lights

# Say hello
print("\nBooting!")
print("------------------\n")

PINS = Pins()

# Make sure the lights are off to start
PINS.lights_off()

lis3mdl = LIS3MDL(PINS)

pin_x = Tact(PINS.TACT_X)
pin_y = Tact(PINS.TACT_Y)
pin_z = Tact(PINS.TACT_Z)

ble = BLEService(pin_x, pin_y, pin_z)

async def update():
    while True:
        x, y, z = lis3mdl.read()
        # print("Magnetic field: ({}, {}, {})".format(x, y, z))

        pin_x.half_period = x
        pin_y.half_period = y
        pin_z.half_period = z

        print("Frequency: ({: >5}, {: >5}, {: >5})".format(
            int(pin_x.hz)
            ,int(pin_y.hz)
            ,int(pin_z.hz)
        ))
        await asyncio.sleep(0.01)

try:
    asyncio.run(asyncio.gather(
        pin_x.drive()
        ,pin_y.drive()
        ,pin_z.drive()
        ,update()
        ,ble.main()
    ))

except OSError as e:
    if e.errno == errno.ENODEV:
        error_lights.no_magnometer(e)
    elif e.errno == errno.ETIMEDOUT:
        error_lights.no_magnometer(e)
    else:
        raise

except Exception as e:
    error_lights.unknown_exception(e)

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
