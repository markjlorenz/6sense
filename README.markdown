# 6 Sense

[Unexpected Maker FeatherS3 Development Board](https://esp32s3.com/)

## Enabling Bluetooth

Bluetooth is enabled by the ambient light sensor.  To activate it, turn on the flashlight on your phone, and hold it over the device.  Through the white case, it will take a fairly bright light to trigger the sensor.

For all of the below instructions:
```
PROJECT=`pwd`
```

## Installing UF2s

```
# https://esp32s3.com/install_uf2.html
# https://micropython.org/download/feathers3/
# https://github.com/adafruit/tinyuf2/releases

# Put the device in to boot mode by clicking `RST` and then `BOOT`
#
# For micropython:
cp -X $PROJECT/uf2/micropython-feathers3-20220618-v1.19.1.uf2 /Volumes/UFTHRS3BOOT/CURRENT.uf2

# For circuitpython:
cp -X $PROJECT/uf2/adafruit-circuitpython-unexpectedmaker_feathers3-en_US-8.0.0-rc.2.uf2 /Volumes/UFTHRS3BOOT/CURRENT.uf2
```

## Managing Firmware

```
# `pip3 install esptool` if not already installed
# put the device into DFU mode by:
# - press and hold `BOOT`
# - press and release `RST`
# - release `BOOT`

# Find the USB device
MODEM=`ls /dev/cu.usbmodem*`
# It will look like this: /dev/cu.usbmodem14301

esptool.py --chip esp32s3 --port $MODEM erase_flash

# For micropython, as a bin
esptool.py --chip esp32s3 --port $MODEM write_flash -z 0x0 $PROJECT/uf2/feathers3-20220618-v1.19.1.bin

# Or, use UF2s for either CircuitPython or MicroPython
cd $PROJECT/uf2/tinyuf2-adafruit_feather_esp32s3-0.12.3

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
mpremote connect $DEVICE mount src/app exec "import development.py"
```

```
# Copy the aioble library on the device to make development faster
cd $PROJECT/src
mpremote connect $DEVICE cp -r packages/aioble/ :
cd $PROJECT
```

```
# wifi code, incase you need it.
import network

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

wlan.connect('$WIFI_NAME', '$PASSWORD')

while not wlan.isconnected():
    pass
```

## Depoying

```
# Copy the aioble library on the device to make development faster
# If not already done.
cd $PROJECT/src
mpremote connect $DEVICE cp -r packages/aioble/ :

# Copy /lib and code.py
cd $PROJECT
mpremote connect $DEVICE mkdir :/lib
mpremote connect $DEVICE cp  src/app/lib/* :/lib/
mpremote connect $DEVICE cp  src/app/code.py :/boot.py
```

## Trouble

If you get into trouble with mpremote not being able to make filesystem commands, connect to the REPL and remove boot.py:
```
mpremote connect $DEVICE
ctrl+c

>>> import os
>>> os.remove("/boot.py")
```

Connecting to the REPL will also give you access to the serial output.

You can also view the seral ouput with `screen`
```
screen $DEVICE 11520
# quite screen with `ctrl+a ctrl+\`
```

If you get into a lot of trouble or are running into file permission issues, see the flashing instructions in the Managing Firmware section above.

## Operating Characteristics:

- 0.081A idle current draw
- Roughly the same when hooked up to electrodes
- The TENs pads feel pretty good at ~12.5V

## TODO

-[x] Speed up the sample rate on the LIS3MDL
-[x] Use voltage instead of piezo https://www.youtube.com/watch?v=8G6jujtK6s0
-[x] Program for voltage
-[x] Print new sensor base
