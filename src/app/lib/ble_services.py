import sys
sys.path.append('/src/packages')
sys.path.append("")

from micropython import const

import uasyncio as asyncio
import aioble
import bluetooth
import random
import struct
import feathers3

# org.bluetooth.service.environmental_sensing
_ENV_SENSE_UUID = bluetooth.UUID(0x181A)

# https://btprodspecificationrefs.blob.core.windows.net/assigned-values/16-bit%20UUID%20Numbers%20Document.pdf
# org.bluetooth.characteristic.temperature
_ENV_SENSE_BATT_UUID = bluetooth.UUID(0x180F)
# _ENV_SENSE_MAG_UUID = bluetooth.UUID(0x2AA1)
_ENV_SENSE_MAGX_UUID = bluetooth.UUID('00002AA1-111-1111-1111-1111111111111')
_ENV_SENSE_MAGY_UUID = bluetooth.UUID('00002AA1-222-2222-2222-2222222222222')
_ENV_SENSE_MAGZ_UUID = bluetooth.UUID('00002AA1-333-3333-3333-3333333333333')

# https://developer.nordicsemi.com/nRF5_SDK/nRF51_SDK_v4.x.x/doc/html/group___b_l_e___a_p_p_e_a_r_a_n_c_e_s.html
# org.bluetooth.characteristic.gap.appearance.xml
_ADV_APPEARANCE_GENERIC_HID = const(960)

# How frequently to send advertising beacons.
_ADV_INTERVAL_MS = 250_000

class BLEService:

    def __init__(self, pin_x, pin_y, pin_z):
        self.pin_x = pin_x
        self.pin_y = pin_y
        self.pin_z = pin_z

        # Register GATT server.
        self.service = aioble.Service(_ENV_SENSE_UUID)

        self.batt_characteristic = aioble.Characteristic(
            self.service, _ENV_SENSE_BATT_UUID, read=True, notify=True
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

        aioble.register_services(self.service)

    # Helper to encode the temperature characteristic encoding (sint16, hundredths of a degree).
    def _encode(self, value):
        # return struct.pack("<h", int(value))
        return struct.pack("<I", int(value))

    async def battery_task(self):
        while True:
            batt_value = feathers3.get_battery_voltage()
            self.batt_characteristic.write(self._encode(batt_value))
            await asyncio.sleep_ms(1000)

    async def pins_task(self):
        while True:
            self.magx_characteristic.write(self._encode(self.pin_x.hz))
            self.magy_characteristic.write(self._encode(self.pin_y.hz))
            self.magz_characteristic.write(self._encode(self.pin_z.hz))
            await asyncio.sleep_ms(1000)

    # Serially wait for connections. Don't advertise while a central is
    # connected.
    async def peripheral_task(self):
        while True:
            async with await aioble.advertise(
                _ADV_INTERVAL_MS,
                name="6sense",
                services=[_ENV_SENSE_UUID],
                appearance=_ADV_APPEARANCE_GENERIC_HID,
            ) as connection:
                print("Connection from", connection.device)
                await connection.disconnected()

    # Run both tasks.
    async def main(self):
        print("Starting BLE")
        await asyncio.gather(
            asyncio.create_task(self.battery_task())
            ,asyncio.create_task(self.pins_task())
            ,asyncio.create_task(self.peripheral_task())
        )
