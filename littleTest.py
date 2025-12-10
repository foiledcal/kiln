import board
import busio
import digitalio
import time

import adafruit_max31855
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

#relays
relay1 = digitalio.DigitalInOut(board.D22)          
relay1.direction = digitalio.Direction.OUTPUT
relay2 = digitalio.DigitalInOut(board.D27)          
relay2.direction = digitalio.Direction.OUTPUT

relay1.value = 1
relay2.value = 1
