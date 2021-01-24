#!/usr/bin/python3

#https://i0.wp.com/peppe8o.com/wp-content/uploads/2019/12/GPIO-featured-image-new.jpg?w=1200&ssl=1
#import RPi.GPIO as GPIO

thetaDirPin = 5
thetaStepPin = 6
thetaEnablePin = 13
radDirPin = 12
radStepPin = 16
radEnablePin = 20


def setupMotorPins():
    return 0
#     GPIO.setwarnings(False)
#     GPIO.cleanup()
#     GPIO.setmode(GPIO.BCM)
#     GPIO.setup(thetaDirPin, GPIO.out)
#     GPIO.setup(thetaStepPin, GPIO.out)
#     GPIO.setup(thetaEnablePin, GPIO.out)
#     GPIO.setup(radDirPin, GPIO.out)
#     GPIO.setup(radStepPin, GPIO.out)
#     GPIO.setup(radEnablePin, GPIO.out)
#     print("Motor pins setup completed")

def enableMotors():
    # GPIO.output(thetaEnablePin, True)
    # GPIO.output(radEnablePin, True)
    print("Motors enabled")

def disableMotors():
    # GPIO.output(thetaEnablePin, False)
    # GPIO.output(radEnablePin, False)
    print("Motors disabled")

def takeThetaStep(direction):
    return 0
    # GPIO.output(thetaDirPin, direction)
    # GPIO.output(thetaStepPin, direction)



