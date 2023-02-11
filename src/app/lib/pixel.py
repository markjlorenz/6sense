import neopixel
import feathers3
import uasyncio as asyncio
from pins import Pins

SPEED = 10  #ms

class Pixel:
    def __init__(self):
        self.pixel = neopixel.NeoPixel(Pins().NEO_PIXEL, 1)
        self.color_index = 0

    def on(self):
        feathers3.set_ldo2_power(True)
        return self

    def off(self):
        feathers3.set_ldo2_power(False)
        return self

    async def loop(self):
        await asyncio.gather(
            asyncio.create_task(self.loop_task())
        )

    async def loop_task(self):
        print("loop pixel")
        while True:
            r,g,b = feathers3.rgb_color_wheel(self.color_index)
            self.pixel[0] = ( r, g, b, 0.5)
            self.pixel.write()
            self.color_index += 1
            await asyncio.sleep_ms(SPEED)
