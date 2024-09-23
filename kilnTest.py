#$ source env/bin/activate
#$ cd /home/pi/mu_code
#$ python kilnTest.py
-----------------------------------------------------------
#imports
-----------------------------------------------------------
import board
import busio
import digitalio
import time

import adafruit_max31855
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
#from simple_pid import PID
import PIDPythonAI
-----------------------------------------------------------
#IO setup
-----------------------------------------------------------
#thermocouple amp
spi = board.SPI()
cs = digitalio.DigitalInOut(board.D5)
max31855 = adafruit_max31855.MAX31855(spi, cs)
tempC = max31855.temperature
tempF = tempC * 9 / 5 + 32

#relays
relay1 = digitalio.DigitalInOut(board.D16)
relay1.direction = digitalio.Direction.OUTPUT
relay2 = digitalio.DigitalInOut(board.D18)
relay2.direction = digitalio.Direction.OUTPUT

#door switch: 1 if open, 0 if closed
doorSwitch = digitalio.DigitalInOut(board.D2)
doorSwitch.direction = digitalio.Direction.INPUT
doorSwitch.pull = digitalio.Pull.UP

#soft off switch: 1 if open, 0 if closed
offSwitch = digitalio.DigitalInOut(board.D3)
offSwitch.direction = digitalio.Direction.INPUT
offSwitch.pull = digitalio.Pull.UP
-----------------------------------------------------------
#variables
-----------------------------------------------------------
#user defined variables
pwmPeriod = 1       #period between PWM updates in seconds
targetTemp = 1080   #celsius

#global variables
safeToHeat = 0      #controls whether relays can be enabled
heatStartTime = 0   #used in thermal runaway checks
heatStartTemp = 0   #used in thermal runaway checks
waitStart = 0       #used in keeping PWM frequency
x = [1]             #plot x-axis value array
y = [tempC]         #plot y-axis value array
yMax = y[0] + 100   #sets the top value of the y-axis
-----------------------------------------------------------
#do stuff
-----------------------------------------------------------
#PID setup
SetOutputLimits(0,100)      #percentile
SetSampleTime(pwmPeriod)

#create first plot and frame
fig, ax = plt.subplots()
graph = ax.plot(x,y,color = 'g')[0]
plt.ylim(0,yMax)

#do not progress until door is shut and soft switch is on
while not safeToHeat:
    if not doorSwitch and not offSwitch: safeToHeat = 1

#start plotting
anim = FuncAnimation(fig, update, frames = None)
plt.show()  #from here, the program will loop within update()

#updates the data and graph
def update(frame):
    global yMax, graph, waitStart, heatStartTime, heatStartTemp

    #safety checks
    if doorSwitch: error(1)
    if offSwitch: error(2)
    thermalRunawayCheck()

    #PID heat control
    compute()

    #bang-bang heat control
    if time.time() > waitStart + pwmPeriod:     #if it's time to check
        if tempC < targetTemp:                  #if need to heat
            if not waitStart and safeToHeat:    #if not heating and relays enabled
                heatOn()                        #turn on elements
                heatStartTime = time.time()     #start runaway timer
                heatStartTemp = tempC           #start runaway reference temp
        else:                                   #if temp is above target
            heatOff()                           #stop heating
            heatStartTime = 0                   #reset runaway timer
            heatStartTemp = 0                   #reset runaway reference temp

        #update the plot
        x.append(x[-1] + 1)
        y.append(tempC)
        graph.set_xdata(x)
        graph.set_ydata(y)
        plt.xlim(x[0], x[-1])
        if y[-1] > yMax - 100:      #update y axis range
            yMax = y[-1] = 100
            plt.ylim(0, yMax)

        waitStart = time.time()     #reset pwm timer

-----------------------------------------------------------
#user-defined functions
-----------------------------------------------------------
def heatOff():
    global safeToHeat, relay1, relay2

    safeToHeat = 0
    relay1.value = 0
    relay2.value = 0

def heatOn():
    #variables for checking thermal runaway
    global heatStartTime, heatStartTemp, relay1, relay2

    heatStartTime = time.time()
    heatStartTemp = tempC

    if safeToHeat:
        relay1.value = 1
        relay2.value = 1

def thermalRunawayCheck():
    #if heating for 5s and temp not risen more than 10%
    if time.time() - heatStartTime > 5 and tempC  < heatStartTemp * 1.1:
        heatOff()
        error(3)

def error(code):
    heatOff()
    print("Error {}: ".format(code))
    match code:
        case "1": print("Door open.")
        case "2": print("Element switch is off.")
        case "3": print("Thermal runaway.")