import board
import busio
import digitalio
import time

#soft off switch: 1 if open, 0 if closed
offSwitch = digitalio.DigitalInOut(board.D18)
offSwitch.direction = digitalio.Direction.INPUT
offSwitch.pull = digitalio.Pull.UP

while True:
    if offSwitch.value:
        print("Switch is on")
    else:
        print("switch is off")
    time.sleep(0.1)
