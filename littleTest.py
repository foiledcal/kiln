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
armSwitch = digitalio.DigitalInOut(board.D26)
armSwitch.direction = digitalio.Direction.INPUT
armSwitch.pull = digitalio.Pull.DOWN

#thermocouple amp
spi = board.SPI()
cs = digitalio.DigitalInOut(board.D5)               #GPIO5
max31855 = adafruit_max31855.MAX31855(spi, cs)

tempTarget = 100
refreshPeriod = 2

def tempC():
    return max31855.temperature

def tempF():
    return max31855.temperature * 9 / 5 + 32

relay1.value = 0
relay2.value = 0
startTime = time.time()


while True:
    if not armSwitch.value:
        relay1.value = 0
        relay2.value = 0

    if time.time() - startTime > refreshPeriod:
        print(tempF())
        startTime = time.time()
        if armSwitch.value:
            if tempF() < tempTarget:
                relay1.value = 1
                relay2.value = 1
            else:
                relay1.value = 0
                relay2.value = 0

        
        
while True:
    print(armSwitch.value)
    if armSwitch.value:
        relay1.value = 0
        relay2.value = 0
        time.sleep(0.5)
    else:
        relay1.value = 1
        relay2.value = 1
        time.sleep(0.5)