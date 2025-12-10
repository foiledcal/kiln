import board
import busio
import digitalio
import time

import adafruit_max31855

#relays
relay1 = digitalio.DigitalInOut(board.D24)          
relay1.direction = digitalio.Direction.OUTPUT
relay2 = digitalio.DigitalInOut(board.D23)          
relay2.direction = digitalio.Direction.OUTPUT

#soft off switch: off is TRUE, on is FALSE
offSwitch = digitalio.DigitalInOut(board.D26)
offSwitch.direction = digitalio.Direction.INPUT
offSwitch.pull = digitalio.Pull.UP

while True:
    print(offSwitch.value)
    if offSwitch.value:
        relay1.value = 0
        relay2.value = 0
        time.sleep(0.5)
    else:
        relay1.value = 1
        relay2.value = 1
        time.sleep(0.5)