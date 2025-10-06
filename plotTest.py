import board
import busio
import digitalio
import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from simple_pid import PID
import random

#y, x, = [], []
#startTime = time.time()
#resolution = 1  #update period in seconds
#timeIntermediary = time.time()
#secCount = 0


x = [1]
y = [random.randint(1,10)]
yMax = y[0]
waitPeriod = 1
startTime = time.time()

fig, ax = plt.subplots()
graph = ax.plot(x,y,color = 'g')[0]
#plt.ylim(0,10)

def update(frame):
    global yMax
    global graph
    global startTime
    if time.time() - startTime > waitPeriod:
        x.append(x[-1] +1)
        y.append(random.randint(1,10))

        graph.set_xdata(x)
        graph.set_ydata(y)
        plt.xlim(x[0], x[-1])
        if y[-1] > yMax:
            yMax = y[-1]
            plt.ylim(0, yMax)
        startTime = time.time()
    print(1)

print(2)
anim = FuncAnimation(fig, update, frames = None)
print(3)
n = 0
while n < 5:
    plt.show()
    print(4)
    global n
    n += 1
print(5)