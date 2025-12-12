#------------------------------------------------------------------------------
#                   imports
#------------------------------------------------------------------------------
import board
import busio
import digitalio
import time

import adafruit_max31855
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

#https://www.etechnophiles.com/raspberry-pi-3-b-pinout-with-gpio-functions-schematic-and-specs-in-detail/

#------------------------------------------------------------------------------
#                   IO setup
#------------------------------------------------------------------------------

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
cs = digitalio.DigitalInOut(board.D5)
max31855 = adafruit_max31855.MAX31855(spi, cs)

#------------------------------------------------------------------------------
#                   variables
#------------------------------------------------------------------------------

#user-defined
tempTarget = 90
bangPeriod = 2
plotPeriod = 2
thermRunCheckPer = 10

#global
heating = False
safeToHeat = False
heatStartTime = 0.0
heatStopTime = 0.0
heatStopTemp = 0
relay1.value = 0
relay2.value = 0
bangStartTime = 0.0
x = [1]             #plot x-axis value array
y = [1]             #plot y-axis value array
yMax = y[0]         #sets the top value of the y-axis
plotStartTime = 0.0

#------------------------------------------------------------------------------
#                   user-defined functions
#------------------------------------------------------------------------------

def heatOff():
    global relay1, relay2, heating, heatStopTime, heatStopTemp
    relay1.value = 0
    relay2.value = 0
    heating = False
    heatStopTime = time.time()
    heatStopTemp = tempC()

def heatOn():
    global relay1, relay2, heating, heatStartTime
    if safeToHeat:
        relay1.value = 1
        relay2.value = 1
        if not heating:
            heating = True
            heatStartTime = time.time()
    else:
        relay1.value = 0
        relay2.value = 0

def switchCheck():
    if armSwitch.value and doorSwitch.value:
        return "safe"
    else:
        return "notSafe"

def tempC():
    return max31855.temperature

def tempF():
    return max31855.temperature * 9 / 5 + 32

def thermalRunawayCheck():
    global safeToHeat
    if time.time() - heatStopTime > thermRunCheckPer and tempC() > heatStopTemp:
        heatOff()
        safeToHeat = False

#------------------------------------------------------------------------------
#                   do stuff
#------------------------------------------------------------------------------

#main loop
def update(frame):
    global safeToHeat, bangStartTime, yMax, graph, plotStartTime, plotPeriod

    #check switches
    if switchCheck() == "notSafe":
        heatOff()
        safeToHeat = False
    else:
        safeToHeat = True

    #check thermal runaway
    #thermalRunawayCheck()

    #Bang-bang period check
    if time.time() - bangStartTime > bangPeriod:
        print(tempF())
        bangStartTime = time.time()
        if tempF() < tempTarget and safeToHeat:
            heatOn()
        else:
            heatOff()

    #update plot
    if time.time() - plotStartTime > plotPeriod:
        #print("TempC = ",tempC())
        x.append(x[-1] +1)
        y.append(tempC())
        graph.set_xdata(x)
        graph.set_ydata(y)
        plt.xlim(x[0], x[-1])
        if y[-1] > yMax:
            yMax = y[-1]
            plt.ylim(0, yMax + 10)
        plotStartTime = time.time()
        

#generate first frame 
fig, ax = plt.subplots()
graph = ax.plot(x,y,color = 'g')[0]
plt.ylim(0,yMax + 10)

#start plotting
anim = FuncAnimation(fig, update, frames = None)
plt.show()