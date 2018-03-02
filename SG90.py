import time
import serial

try:
    ser = serial.Serial('/dev/ttyUSB0', timeout = 1)
except:
    pass

def right(deg):
    try:
        ser.write(str(deg).encode())
    except:
        pass

def left(deg):
    try:
        ser.write(str(deg).encode())
    except:
        pass

def stop():
    pass
