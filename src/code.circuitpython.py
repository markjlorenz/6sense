import time, gc, os
import neopixel
import board, digitalio
import feathers3
import busio
import math
from adafruit_lis3mdl import LIS3MDL
import asyncio


# Create a NeoPixel instance
# Brightness of 0.3 is ample for the 1515 sized LED
pixel = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.3, auto_write=True, pixel_order=neopixel.RGB)

# Say hello
print("\nHello from FeatherS3!")
print("------------------\n")

# # Create a colour wheel index int
# color_index = 0

# Turn on the power to the NeoPixel
# feathers3.set_ldo2_power(True)

# Rainbow colours on the NeoPixel
# while True:
#     # Get the R,G,B values of the next colour
#     r,g,b = feathers3.rgb_color_wheel( color_index )
#     # Set the colour on the NeoPixel
#     pixel[0] = ( r, g, b, 0.5)
#     # Increase the wheel index
#     color_index += 1

#     # If the index == 255, loop it
#     if color_index == 255:
#         color_index = 0
#         # Invert the internal LED state every half colour cycle
#         feathers3.led_blink()

#     # Sleep for 15ms so the colour cycle isn't too fast
#     time.sleep(0.015)

i2c = busio.I2C(board.SCL, board.SDA)
lis3mdl = LIS3MDL(i2c)

class Tact:
    def __init__(self, board_pin):
        self.pin = digitalio.DigitalInOut(board_pin)
        self.pin.direction = digitalio.Direction.OUTPUT
        self.half_period = 0

pin_x = Tact(board.MISO)
pin_y = Tact(board.MOSI)
pin_z = Tact(board.SCK)

async def drive(pin):
    while True:
        # turn the pin on
        pin.pin.value = True
        await asyncio.sleep(pin.half_period)

        # turn the pin off
        pin.pin.value = False
        await asyncio.sleep(pin.half_period)

scale_exponent = 2
pre_scale_factor = 1.01
async def update():
    while True:
        x, y, z = lis3mdl.magnetic
        # print("Magnetic field: ({}, {}, {})".format(x, y, z))

        pin_x.half_period = 0 if x == 0 else 1 / math.pow(x * pre_scale_factor, scale_exponent) * 10
        pin_y.half_period = 0 if y == 0 else 1 / math.pow(y * pre_scale_factor, scale_exponent) * 10
        pin_z.half_period = 0 if z == 0 else 1 / math.pow(z * pre_scale_factor, scale_exponent) * 10

        # pin_x.half_period = 0 if x == 0 else 1 / math.pow(x, scale_exponent) * 10
        # pin_y.half_period = 0 if y == 0 else 1 / math.pow(y, scale_exponent) * 10
        # pin_z.half_period = 0 if z == 0 else 1 / math.pow(z, scale_exponent) * 10

        print("half period: ({}, {}, {})".format(
            0 if pin_x.half_period == 0 else 1/pin_x.half_period,
            0 if pin_y.half_period == 0 else 1/pin_y.half_period,
            0 if pin_z.half_period == 0 else 1/pin_z.half_period,
        ))
        await asyncio.sleep(0.01)

asyncio.run(asyncio.gather(drive(pin_x), drive(pin_y), drive(pin_z), update()))


# half_period = 0.1
# while True:
#     # turn the pin on
#     pin_z.pin.value = True
#     time.sleep(half_period)

#     # turn the pin off
#     pin_z.pin.value = False
#     time.sleep(half_period)

#     x, y, z = lis3mdl.magnetic
#     print("Magnetic field: ({}, {}, {})".format(x, y, z))
#     half_period = 1 / math.pow(-z, 2) * 10
#     time.sleep(0.01)

