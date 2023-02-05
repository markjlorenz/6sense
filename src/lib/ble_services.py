import sys
sys.path.append('/remote/lib')
sys.path.append("")

from micropython import const

import uasyncio as asyncio
import aioble
import bluetooth

import random
import struct

# org.bluetooth.service.environmental_sensing
_ENV_SENSE_UUID = bluetooth.UUID(0x181A)
# org.bluetooth.characteristic.temperature
_ENV_SENSE_TEMP_UUID = bluetooth.UUID(0x2A6E)
# org.bluetooth.characteristic.gap.appearance.xml
_ADV_APPEARANCE_GENERIC_THERMOMETER = const(768)

# How frequently to send advertising beacons.
_ADV_INTERVAL_MS = 250_000

class BLEService:

    def __init__(self):
        # Register GATT server.
        self.temp_service = aioble.Service(_ENV_SENSE_UUID)
        self.temp_characteristic = aioble.Characteristic(
            self.temp_service, _ENV_SENSE_TEMP_UUID, read=True, notify=True
        )
        aioble.register_services(self.temp_service)

    # Helper to encode the temperature characteristic encoding (sint16, hundredths of a degree).
    def _encode_temperature(self, temp_deg_c):
        return struct.pack("<h", int(temp_deg_c * 100))

    # This would be periodically polling a hardware sensor.
    async def sensor_task(self):
        t = 24.5
        while True:
            self.temp_characteristic.write(self._encode_temperature(t))
            t += random.uniform(-0.5, 0.5)
            await asyncio.sleep_ms(1000)

    # Serially wait for connections. Don't advertise while a central is
    # connected.
    async def peripheral_task(self):
        while True:
            async with await aioble.advertise(
                _ADV_INTERVAL_MS,
                name="6sense",
                services=[_ENV_SENSE_UUID],
                appearance=_ADV_APPEARANCE_GENERIC_THERMOMETER,
            ) as connection:
                print("Connection from", connection.device)
                await connection.disconnected()

    # Run both tasks.
    async def main(self):
        await asyncio.gather(
            asyncio.create_task(self.sensor_task())
            ,asyncio.create_task(self.peripheral_task())
        )
