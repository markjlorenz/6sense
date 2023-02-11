from pixel import Pixel
import feathers3
import time

def unknown_exception(e):
    print(e)
    _blink_error_seconds(1)

def no_magnometer(e):
    print(e)
    _blink_error_seconds(0.25)

def _blink_error_seconds(interval):
    Pixel().off() # turn off the Neo to save battery
    while True:
        feathers3.led_blink()
        time.sleep(interval) # seconds
