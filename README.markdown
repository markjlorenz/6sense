# 6 Sense

[Unexpected Maker FeatherS3 Development Board](https://esp32s3.com/)

```
# https://esp32s3.com/install_uf2.html
# https://micropython.org/download/feathers3/
# https://github.com/adafruit/tinyuf2/releases

# Put the device in to boot mode by clicking `RST` and then `BOOT`
#
# For micropython:
cp -X uf2/micropython-feathers3-20220618-v1.19.1.uf2 /Volumes/UFTHRS3BOOT/CURRENT.uf2

# For circuitpython:
cp -X uf2/adafruit-circuitpython-unexpectedmaker_feathers3-en_US-8.0.0-rc.2.uf2 /Volumes/UFTHRS3BOOT/CURRENT.uf2
```

```
# `pip3 install esptool` if not already installed
# put the device into DFU mode by:
# - press and hold `BOOT`
# - press and release `RST`
# - release `BOOT`

# Find the USB device
MODEM=`ls /dev/cu.usbmodem*`
# It will look like this: /dev/cu.usbmodem14301

# For circuitpython:
esptool.py --chip esp32s3 --port $MODEM erase_flash

cd uf2/tinyuf2-adafruit_feather_esp32s3-0.12.3

esptool.py --chip esp32s3 -p $MODEM --before=default_reset --after=no_reset write_flash --flash_mode dio --flash_size detect --flash_freq 80m 0x0 bootloader.bin 0x8000 partition-table.bin 0xe000 ota_data_initial.bin 0x410000 tinyuf2.bin
```

```
# pip3 install mpremote
DEVICE=`ls /dev/cu.usbmodem*`
# Will look like: /dev/cu.usbmodem_fs3_1

# Get a python REPL
mpremote connect $DEVICE

# List files on the device
mpremote connect $DEVICE ls

# Mount the source directory and run the code
mpremote connect $DEVICE mount src/app exec "import code.py"
```

```
# Copy the aioble library on the device to make development faster
mpremote connect $DEVICE cp -r src/packages/aioble/ :
```

FeatherS3 helper library: https://github.com/UnexpectedMaker/esp32s3/blob/main/code/micropython/helper%20libraries/feathers3/feathers3.py


import esp32

esp32.hall_sensor()

```
# wifi code, incase you need it.
import network

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

wlan.connect('Lorenz-Family_v2.0', 'firebase')

while not wlan.isconnected():
    pass
```
