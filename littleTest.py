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

#arming switch: off is FALSE, on is TRUE
armSwitch = digitalio.DigitalInOut(board.D26)
armSwitch.direction = digitalio.Direction.INPUT
armSwitch.pull = digitalio.Pull.DOWN

#door switch: closed circuit is FALSE, open circuit is TRUE
doorSwitch = digitalio.DigitalInOut(board.D6)
doorSwitch.direction = digitalio.Direction.INPUT
doorSwitch.pull = digitalio.Pull.DOWN

#thermocouple amp
spi = board.SPI()
cs = digitalio.DigitalInOut(board.D5)               #GPIO5
max31855 = adafruit_max31855.MAX31855(spi, cs)

tempTarget = 90
refreshPeriod = 2

def tempC():
    return max31855.temperature

def tempF():
    return max31855.temperature * 9 / 5 + 32

def safetyCheck():
    if armSwitch.value and doorSwitch.value:
        return "safe"
    else:
        return "notSafe"

def heatOn():
    global relay1, relay2
    if safetyCheck() == "safe":
        relay1.value = 1
        relay2.value = 1
    else:
        relay1.value = 0
        relay2.value = 0

def heatOff():
    global relay1, relay2
    relay1.value = 0
    relay2.value = 0


relay1.value = 0
relay2.value = 0
bangStartTime = time.time()

while True:
    #safety check first
    if safetyCheck() == "notSafe":
        heatOff()

    #Bang-bang period check
    if time.time() - bangStartTime > refreshPeriod:
        print(tempF())
        bangStartTime = time.time()
        if tempF() < tempTarget:
            heatOn()
        else:
            heatOff()