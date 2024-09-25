#$ source env/bin/activate
#$ cd /home/pi/mu_code
#$ python kilnTest.py
#-----------------------------------------------------------
#imports
#-----------------------------------------------------------
import board
import busio
import digitalio
import time

import adafruit_max31855
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
#from simple_pid import PID
import PIDPythonAI
#-------------------------------------------------------------------------------
#IO setup
#-------------------------------------------------------------------------------
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
#-------------------------------------------------------------------------------
#variables
#-------------------------------------------------------------------------------
#user defined variables
pwmPeriod = 2                   #2s update period should be responsive enough
targetTemp = 1080               #hard-coded target lol

#control variables
outputRes = 120 * pwmPeriod     #120 zero-crossings per second
safeToHeat = 1                  #controls whether relays can be enabled
heatStartTime = 0               #used in thermal runaway checks
heatStartTemp = 0               #used in thermal runaway checks
pulseStart = 0                #used in keeping PWM frequency
oldOutput = 0                   #helps check if new orders from pwm

#plotting variables
x = [1]             #plot x-axis value array
y = [tempC]         #plot y-axis value array
yMax = y[0] + 100   #sets the top value of the y-axis
#------------------------------------------------------------------------------
#user-defined functions
#-------------------------------------------------------------------------------
def heatOff():
    global relay1, relay2, heating
    relay1.value = 0
    relay2.value = 0
    heating = 0

def heatOn():
    #variables for checking thermal runaway
    global heatStartTime, heatStartTemp, relay1, relay2, heating

    heatStartTime = time.time()
    heatStartTemp = tempC

    if safeToHeat:
        relay1.value = 1
        relay2.value = 1
        heating = 1

def heating():
    if relay1.value == 1 or relay2.value == 1: return 1
    else: return 0

def thermalRunawayCheck():
    #if heating for 5s and temp not risen more than 10 degrees (may need to be adjusted)
    if time.time() - heatStartTime > 5 and tempC  < heatStartTemp + 10:
        heatOff()
        error(3)

    #if cooling for 5s and temp not fallen more than 10 degrees
    elif time.time() - heatStartTime > 5 and tempC > heatStartTemp - 10:
        heatOff()
        error(4)

def error(code):
    heatOff()
    safeToHeat = 0
    print("Error {}: ".format(code))
    match code:
        case "1": print("Door open.")
        case "2": print("Element switch is off.")
        case "3": print("Thermal runaway.")
        case "4": print("Unexpected heating.")

#updates the data and graph
def update(frame):
    global yMax, graph, pulseStart, heatStartTime, heatStartTemp, oldOutput

    #safety checks
    #if doorSwitch: error(1)
    #if offSwitch: error(2)
    thermalRunawayCheck()

    #PWM
    pidOutput = PIDPythonAI.compute()

    #check for an update from PWM
    if pidOutput != oldOutput:              #pwm updated, new orders
        oldOutput = pidOutput               #update oldOutput
        if pidOutput == 240:                #set heat to on until next update
            heatOn()
        elif pidOutput == 0:                #set heat to off until next update
                heatOff()
        else:
            pulseStart = time.time()
            heatOn()

    #if in the middle of a partial heating period
    if time.time() > pulseStart + pidOutput / 120:
        pulseStart = 0    #reset pulse timer
        heatOff()         #stop heating

    #update the plot
    x.append(x[-1] + 1)
    y.append(tempC)
    graph.set_xdata(x)
    graph.set_ydata(y)
    plt.xlim(x[0], x[-1])
    if y[-1] > yMax - 100:      #update y axis range
        yMax = y[-1] = 100
        plt.ylim(0, yMax)
#-------------------------------------------------------------------------------
#do stuff
#-------------------------------------------------------------------------------
#PID setup
PIDPythonAI.SetOutputLimits(0,outputRes)     #how many SSR zero-crossings to be on for
PIDPythonAI.SetSampleTime(pwmPeriod)

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



