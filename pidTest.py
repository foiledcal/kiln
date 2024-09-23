import board
import busio
import digitalio
import time
import PIDPythonAI

pwmPeriod = 1
targetTemp = 1080

x = [1]             #plot x-axis value array
y = [tempC]         #plot y-axis value array
yMax = y[0] + 100   #sets the top value of the y-axis

#PID setup
SetOutputLimits(0,120)     #how many SSR zero-crossings to be on for
SetSampleTime(pwmPeriod)

#create first plot and frame
fig, ax = plt.subplots()
graph = ax.plot(x,y,color = 'g')[0]
plt.ylim(0,yMax)

#start plotting
anim = FuncAnimation(fig, update, frames = None)
plt.show()  #from here, the program will loop within update()

def update(frame):
    global yMax, graph, waitStart, heatStartTime, heatStartTemp
    
    pidOutput = compute()
    if pidOutput == 100:
        heatStartTime = time.time()
        hearStartTemp = tempC
        