# Characteristics:
#
# 0x180F - Battery life (unsigned int), read-only
# 0x180A - Version of the code (hard-coded unsigned int), read-only
# 0x0492FCEC - Test pattern mode, read or write, write a 1 to start test pattern mode
# 0x00002AA1-111 - x-axis mag, read or notify
# 0x00002AA1-222 - y-axis mag, read or notify
# 0x00002AA1-333 - z-axis mag, read or notify

import sys
sys.path.append("/packages")

from micropython import const

import uasyncio as asyncio
import aioble
import bluetooth
import random
import struct
import feathers3
from pixel import Pixel

DEVICE_NAME = "Electroception"
VERSION     = 202302260121

# org.bluetooth.service.environmental_sensing
_ENV_SENSE_UUID = bluetooth.UUID(0x181A)

# https://btprodspecificationrefs.blob.core.windows.net/assigned-values/16-bit%20UUID%20Numbers%20Document.pdf
_ENV_SENSE_BATT_UUID    = bluetooth.UUID(0x180F)
_ENV_SENSE_VERSION_UUID = bluetooth.UUID(0x180A)
_ENV_SENSE_MAGX_UUID    = bluetooth.UUID('00002AA1-111-1111-1111-1111111111111')
_ENV_SENSE_MAGY_UUID    = bluetooth.UUID('00002AA1-222-2222-2222-2222222222222')
_ENV_SENSE_MAGZ_UUID    = bluetooth.UUID('00002AA1-333-3333-3333-3333333333333')
_ENV_SENSE_DEBUG_UUID   = bluetooth.UUID('0492FCEC-7194-11EB-9439-0242AC130003')

# https://developer.nordicsemi.com/nRF5_SDK/nRF51_SDK_v4.x.x/doc/html/group___b_l_e___a_p_p_e_a_r_a_n_c_e_s.html
# org.bluetooth.characteristic.gap.appearance.xml
_ADV_APPEARANCE_GENERIC_HID = const(960)

# How frequently to send advertising beacons.
_ADV_INTERVAL_MS = 250_000

LIGHT_THRESHOLD    = 3_800 # bigger number, more light
CONNECTION_TIMEOUT = 60.0  # seconds

class BLEService:
    def __init__(self, pin_x, pin_y, pin_z):
        self.pin_x = pin_x
        self.pin_y = pin_y
        self.pin_z = pin_z

        self.connection = None

        # Register GATT server.
        self.service = aioble.Service(_ENV_SENSE_UUID)

        self.batt_characteristic = aioble.Characteristic(
            self.service, _ENV_SENSE_BATT_UUID, read=True
        )
        self.version_characteristic = aioble.Characteristic(
            self.service, _ENV_SENSE_VERSION_UUID, read=True
        )
        self.magx_characteristic = aioble.Characteristic(
            self.service, _ENV_SENSE_MAGX_UUID, read=True, notify=True
        )
        self.magy_characteristic = aioble.Characteristic(
            self.service, _ENV_SENSE_MAGY_UUID, read=True, notify=True
        )
        self.magz_characteristic = aioble.Characteristic(
            self.service, _ENV_SENSE_MAGZ_UUID, read=True, notify=True
        )
        self.debug_characteristic = aioble.Characteristic(
            self.service, _ENV_SENSE_DEBUG_UUID, read=True, write=True
        )

        self.pixel = Pixel()
        self.test_pattern = 0

        aioble.register_services(self.service)


    # Helper to encode the temperature characteristic encoding (sint16, hundredths of a degree).
    def _encode(self, value):
        return struct.pack("<I", int(value))

    async def battery_task(self):
        while True:
            batt_value = feathers3.get_battery_voltage()
            self.batt_characteristic.write(self._encode(batt_value))
            await asyncio.sleep_ms(1_000)

    async def version_task(self):
        while True:
            self.version_characteristic.write(self._encode(VERSION))
            await asyncio.sleep_ms(1_000)

    async def debug_task(self):
        while True:
            await asyncio.sleep_ms(1_000)
            await self.debug_characteristic.written()

            raw_read = self.debug_characteristic.read()
            self.test_pattern = int(raw_read[0])
            print("written: ", self.test_pattern)
            self.debug_characteristic.write(raw_read)

    async def pins_task(self):
        while True:
            await asyncio.sleep_ms(100)
            if self.connection:
                x = self._encode(self.pin_x.hz)
                y = self._encode(self.pin_y.hz)
                z = self._encode(self.pin_z.hz)

                try: # peripheral disconnection can happen within the block of code
                    self.magx_characteristic.write(x)
                    self.magy_characteristic.write(y)
                    self.magz_characteristic.write(z)

                    self.magx_characteristic.notify(self.connection, x)
                    self.magy_characteristic.notify(self.connection, y)
                    self.magz_characteristic.notify(self.connection, z)

                except OSError as e: # you can ignore this error if disconnect was expected
                    print("Error in BLEServices.pins_task: {}".format(e))
                    self.connection = None
                    pass

    # Serially wait for connections. Don't advertise while a central is
    # connected.
    #
    # When exposed to light, you get 20 second to connect to and read from BLE
    # after 20 seconds clients will automtically disconnect, and the light
    # sensor will check ambient light again.
    #
    async def peripheral_task(self):
        while True:
            if feathers3.get_amb_light() > LIGHT_THRESHOLD:
                self.pixel.on()
                try:
                    await asyncio.wait_for(
                        self.advertise_bt()
                        ,timeout=CONNECTION_TIMEOUT
                    )
                except asyncio.TimeoutError:
                    print("Advertising timed out after 2 seconds")
            else:
                self.pixel.off()
                await asyncio.sleep_ms(1_000)

    async def advertise_bt(self):
        async with await aioble.advertise(
            _ADV_INTERVAL_MS,
            name=DEVICE_NAME,
            services=[_ENV_SENSE_UUID],
            appearance=_ADV_APPEARANCE_GENERIC_HID,
        ) as connection:
            print("Connection from", connection.device)
            self.connection = connection
            await connection.disconnected()
            self.connection = None

    # Run both tasks.
    async def main(self):
        print("Starting BLE")
        await asyncio.gather(
            asyncio.create_task(self.battery_task())
            ,asyncio.create_task(self.version_task())
            ,asyncio.create_task(self.pins_task())
            ,asyncio.create_task(self.peripheral_task())
            ,asyncio.create_task(self.pixel.loop())
            ,asyncio.create_task(self.debug_task())
        )
