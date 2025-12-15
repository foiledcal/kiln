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
thermRunCheckPer = 30

#global
heating = False
safeToHeat = False
emergency = False
heatStartTime = 0.0
heatStartTemp = 0.0
heatStopTime = time.time()
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
    if heating:
        heating = False
        heatStopTime = time.time()
        heatStopTemp = tempC()

def heatOn():
    global relay1, relay2, heating, heatStartTime, heatStartTemp
    if safeToHeat and not emergency:
        relay1.value = 1
        relay2.value = 1
        if not heating:
            heating = True
            heatStartTime = time.time()
            heatStartTemp = tempC()
    else:
        heatOff()

def tempC():
    global emergency
    try:
        temp = max31855.temperature
    except Exception as e:
        if e == "thermocouple not connected":
            print("Thermocouple disconnected, halting operation.")
            emergency = True
        else:
            print("Thermocouple amp error, halting operation.")
            emergency = True
        return 0
    else:
        return temp

def tempF():
    return tempC() * 9 / 5 + 32

#------------------------------------------------------------------------------
#                   do stuff
#------------------------------------------------------------------------------

#main loop
def update(frame):
    global safeToHeat, bangStartTime, yMax, graph, plotStartTime, plotPeriod, emergency

    #check switches
    if armSwitch.value and doorSwitch.value:
        safeToHeat = True
    else:
        heatOff()
        safeToHeat = False

    #check thermal runaway
    if time.time() - heatStopTime > thermRunCheckPer:
        #add different types of thermal runaway checks
        #add temp sensor to outside of kiln and inside controller enclosure
        if not heating and tempC() > heatStopTemp:
            emergency = True
    
    if emergency:
        heatOff()
        return

    #Bang-bang period check
    if time.time() - bangStartTime > bangPeriod:
        print("TempC = ",tempC())
        print(safeToHeat)
        bangStartTime = time.time()
        if tempF() < tempTarget:
            heatOn()
        else:
            heatOff()

    #update plot
    if time.time() - plotStartTime > plotPeriod:
        #update data file
        f.write(time.time() + ", " + tempC() + "," + heating + '\n')
        
        x.append(x[-1] +1)
        y.append(tempC())
        graph.set_xdata(x)
        graph.set_ydata(y)
        plt.xlim(x[0], x[-1])
        if y[-1] > yMax:
            yMax = y[-1]
            plt.ylim(0, yMax + 10)
        plotStartTime = time.time()


        

#file init
f = open('data.txt', 'w')

#generate first frame 
fig, ax = plt.subplots()
graph = ax.plot(x,y,color = 'g')[0]
plt.ylim(0,yMax + 10)

#start plotting
anim = FuncAnimation(fig, update, frames = None)
plt.show()