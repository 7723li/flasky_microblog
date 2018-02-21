import RPi.GPIO as gpio
import time

gpio.setwarnings(False)
gpio.setmode(gpio.BOARD)
servoPin = 18
gpio.setup(servoPin, gpio.OUT, initial = False)
pwm = gpio.PWM(servoPin, 50)
pwm.start(0)
i = 0

def turn(i):
    pwm.ChangeDutyCycle(2.5 + 10 * i / 180)
    time.sleep(0.02)
    pwm.ChangeDutyCycle(0)

def stop():
    pwm.ChangeDutyCycle(0)

def right():
    for i in range(181, 0, -10):
        pwm.ChangeDutyCycle(2.5 + 10 * i / 180)
        time.sleep(0.02)
        pwm.ChangeDutyCycle(0)
        time.sleep(0.05)

def left():
    for i in range(0, 181, 10):
        pwm.ChangeDutyCycle(2.5 + 10 * i / 180)
        time.sleep(0.02)
        pwm.ChangeDutyCycle(0)
        time.sleep(0.05)

