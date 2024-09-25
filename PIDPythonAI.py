import time

# working variables
last_time = 0
Input = 0.0         #current temp
Output = 0.0
Setpoint = 0.0      #target temp
ITerm = 0.0
lastInput = 0.0
kp = 0.0
ki = 0.0
kd = 0.0
SampleTime = 1000
outMin = 0.0
outMax = 0.0
inAuto = False

MANUAL = 0
AUTOMATIC = 1

DIRECT = 0
REVERSE = 1
controllerDirection = DIRECT

def millis():
    return int(round(time.time() * 1000))

def compute():
    global last_time, Input, Output, Setpoint, ITerm, lastInput, kp, ki, kd, outMin, outMax, inAuto
    if not inAuto:
        return
    now = millis()
    timeChange = (now - last_time)
    if timeChange >= SampleTime:
        # Compute all the working error variables
        error = Setpoint - Input
        ITerm += (ki * error)
        if ITerm > outMax:
            ITerm = outMax
        elif ITerm < outMin:
            ITerm = outMin
        dInput = (Input - lastInput)
        
        # Compute PID output
        Output = kp * error + ITerm - kd * dInput
        if Output > outMax:
            Output = outMax
        elif Output < outMin:
            Output = outMin
        
        # Remember some variables for next time
        lastInput = Input
        last_time = now
        
        return Output

def SetTunings(Kp, Ki, Kd):
    global kp, ki, kd
    if Kp < 0 or Ki < 0 or Kd < 0:
        return
    
    SampleTimeInSec = SampleTime / 1000.0
    kp = Kp
    ki = Ki * SampleTimeInSec
    kd = Kd / SampleTimeInSec
    
    if controllerDirection == REVERSE:
        kp = -kp
        ki = -ki
        kd = -kd

def SetSampleTime(NewSampleTime):
    global SampleTime, ki, kd
    if NewSampleTime > 0:
        ratio = NewSampleTime / SampleTime
        
        ki *= ratio
        kd /= ratio
        SampleTime = NewSampleTime

def SetOutputLimits(Min, Max):
    global Output, ITerm, outMin, outMax
    if Min > Max:
        return
    outMin = Min
    outMax = Max
    
    if Output > outMax:
        Output = outMax
    elif Output < outMin:
        Output = outMin

    if ITerm > outMax:
        ITerm = outMax
    elif ITerm < outMin:
        ITerm = outMin

def SetMode(Mode):
    global inAuto
    newAuto = (Mode == AUTOMATIC)
    if newAuto != inAuto:
        # we just went from manual to auto
        Initialize()
    inAuto = newAuto

def Initialize():
    global lastInput, ITerm, Output, outMin, outMax
    lastInput = Input
    ITerm = Output
    if ITerm > outMax:
        ITerm = outMax
    elif ITerm < outMin:
        ITerm = outMin

def SetControllerDirection(Direction):
    global controllerDirection
    controllerDirection = Direction

