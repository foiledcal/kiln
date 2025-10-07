import board
import busio
import digitalio
import time

import adafruit_max31855


spi = board.SPI()
cs = digitalio.DigitalInOut(board.D5)               #GPIO5
max31855 = adafruit_max31855.MAX31855(spi, cs)

#soft off switch: 1 if open, 0 if closed
offSwitch = digitalio.DigitalInOut(board.D18)
offSwitch.direction = digitalio.Direction.INPUT
offSwitch.pull = digitalio.Pull.DOWN

while True:
    if offSwitch.pull:
        print("Switch is on")
    else:
        print("switch is off")
    time.sleep(0.1)
