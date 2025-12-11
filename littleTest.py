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

#global
heating = False
safeToHeat = False
heatStartTime = time.time()
heatStopTime = time.time()
relay1.value = 0
relay2.value = 0
bangStartTime = time.time()
x = [1]             #plot x-axis value array
y = [100]           #plot y-axis value array
yMax = y[0]         #sets the top value of the y-axis
plotStartTime = time.time()

#------------------------------------------------------------------------------
#                   user-defined functions
#------------------------------------------------------------------------------

def tempC():
    return max31855.temperature

def tempF():
    return max31855.temperature * 9 / 5 + 32

def switchCheck():
    if armSwitch.value and doorSwitch.value:
        return "safe"
    else:
        return "notSafe"

def heatOn():
    global relay1, relay2, heating, heatStartTime
    if switchCheck() == "safe":
        relay1.value = 1
        relay2.value = 1
        if not heating:
            heating = True
            heatStartTime = time.time()
    else:
        relay1.value = 0
        relay2.value = 0

def heatOff():
    global relay1, relay2, heating, heatStopTime
    relay1.value = 0
    relay2.value = 0
    heating = False
    heatStopTime = time.time()

#------------------------------------------------------------------------------
#                   do stuff
#------------------------------------------------------------------------------

#while True:
#    #check switches
#    if switchCheck() == "notSafe":
#        heatOff()
#        safeToHeat = False
#
#    #check thermal runaway
#
#
#    #Bang-bang period check
#    if time.time() - bangStartTime > bangPeriod:
#        print(tempF())
#        bangStartTime = time.time()
#        if tempF() < tempTarget and safeToHeat:
#            heatOn()
#        else:
#            heatOff()

#main loop
def update(frame):
    global safeToHeat, bangStartTime, yMax, graph, plotStartTime, plotPeriod

    #check switches
    if switchCheck() == "notSafe":
        heatOff()
        safeToHeat = False

    #check thermal runaway

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