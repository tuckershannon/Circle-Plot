#!/usr/bin/python3

#https://i0.wp.com/peppe8o.com/wp-content/uploads/2019/12/GPIO-featured-image-new.jpg?w=1200&ssl=1

import RPi.GPIO as GPIO

enablePin = 7

thetaDirPin = 20
thetaStepPin = 21

radDirPin = 16
radStepPin = 12



def setupMotorPins():
    return 0
    GPIO.setwarnings(False)
    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(thetaDirPin, GPIO.out)
    GPIO.setup(thetaStepPin, GPIO.out)
    GPIO.setup(thetaEnablePin, GPIO.out)
    GPIO.setup(radDirPin, GPIO.out)
    GPIO.setup(radStepPin, GPIO.out)
    GPIO.setup(radEnablePin, GPIO.out)
    print("Motor pins setup completed")

def enableMotors():
    GPIO.output(enablePin, True)
    print("Motors enabled")

def disableMotors():

    GPIO.output(enablePin, False)
    print("Motors disabled")

def takeStep(direction, name):
    if name == "theta":
        GPIO.output(thetaDirPin, direction)
        GPIO.output(thetaStepPin, True)
        GPIO.output(thetaStepPin, False)
    if name == "r":
        GPIO.output(radDirPin, direction)
        GPIO.output(radStepPin, True)
        GPIO.output(radStepPin, False)


#
# def takeRadStep(direction):
#     return 0

