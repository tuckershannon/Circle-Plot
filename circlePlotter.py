import matplotlib.pyplot as plt
import math
from pygcode import Line, Machine
import time
import piFuncs as pi


class stepperMotor:
    def __init__(self, gearRatio, gearDiameter, name):
        self.stepCount = 0
        self.velocity = 0
        self.stepsPerRev = 1000
        self.gearRatio = gearRatio
        self.mmPerStepX = 0.1
        self.mmPerStepY = 0.1
        self.gearDiameter = gearDiameter
        self.name = name
        self.speed = 10

    def takeStep(self, direction):
        # time.sleep(1/self.speed)
        if direction == 1:
            #print("Motor " + self.name + " step forward")
            self.stepCount += 1
        elif direction == 2:
            #print("Motor " + self.name + " step backward")
            self.stepCount -= 1
        else:
            print("Incorrect direction. Please input direction 1 or 2")


class circlePlotter:
    def __init__(self):
        self.started = True
        self.radius = 200  # mm
        self.traj = []
        self.pathTaken = []
        self.origin = []
        self.currentPos = []
        self.currentTheta = 0.0
        self.currentR = 0.0
        self.rMotor = stepperMotor(gearRatio=1, gearDiameter=1, name="r")
        self.thetaMotor = stepperMotor(gearRatio=10, gearDiameter=10, name="theta")

    def turnOnMotors(self):
        pi.setupMotorPins()
        pi.enableMotors()

    def takeStep(self, motor, direction):
        if motor == 1:
            self.rMotor.takeStep(direction)
            self.updateRadius()
        elif motor == 2:
            self.thetaMotor.takeStep(direction)
            self.updateTheta()
        else:
            print("Incorrect motor selection. Please select motor 1 or 2")
        self.pathTaken.append(self.currentPos)

    def readGcode(self, filepath):
        m = Machine()
        with open(filepath, 'r') as fh:
            for line_text in fh.readlines():
                line = Line(line_text)
                m.process_block(line.block)
                if line.gcodes != []:
                    self.traj.append((m.pos.values['X'], m.pos.values['Y']))

    def showTraj(self):
        xPoints = [x[0] for x in self.traj]
        yPoints = [x[1] for x in self.traj]
        plt.plot(xPoints, yPoints)
        plt.show()

    def showPathTaken(self):
        xPoints = [x[0] for x in self.pathTaken]
        yPoints = [x[1] for x in self.pathTaken]
        plt.plot(xPoints, yPoints)
        plt.show()



    def keyboardcontrol(self):
        print("finish this?")

    def start(self):
        self.readGcode('sandify.gcode')
        self.setOrigin()
        self.turnOnMotors()
        for x in range(0, 800):
            self.moveToPoint(self.traj.pop(0))
        self.showPathTaken()

    def moveToPoint(self, point):

        while not self.closeEnough(point):
            # there are 4 possible movements we can do
            # 1. Move rMotor 1 step forward
            # 2. Move rMotor 1 step backward
            # 3. Move thetaMotor 1 step forward
            # 4. Move thetaMotor 1 step backward
            # Any of these will move us either closer or further away from our target
            # We want to find the one the moves us closest to our target and then do that.

            # First, we should find our current distance from the target
            dx = point[0] - self.currentPos[0]
            dy = point[1] - self.currentPos[1]

            # Next, we should update the distance changed by taking a step for each motor
            self.rMotorStepMovementUpdate()
            self.thetaMotorStepMovementUpdate()

            # Check distance change if we move rMotor 1 step forward
            dx1 = point[0] - (self.currentPos[0] + self.rMotor.mmPerStepX)
            dy1 = point[1] - (self.currentPos[1] + self.rMotor.mmPerStepY)
            # Check distance change if we move rMotor 1 step backward
            dx2 = point[0] - (self.currentPos[0] - self.rMotor.mmPerStepX)
            dy2 = point[1] - (self.currentPos[1] - self.rMotor.mmPerStepY)
            # Check distance change if we move thetaMotor 1 step forward
            dx3 = point[0] - (self.currentPos[0] + self.thetaMotor.mmPerStepX)
            dy3 = point[1] - (self.currentPos[1] + self.thetaMotor.mmPerStepY)
            # Check distance change if we move thetaMotor 1 step backward
            dx4 = point[0] - (self.currentPos[0] - self.thetaMotor.mmPerStepX)
            dy4 = point[1] - (self.currentPos[1] - self.thetaMotor.mmPerStepY)

            d = math.sqrt(dx ** 2 + dy ** 2)
            d1 = math.sqrt(dx1 ** 2 + dy1 ** 2)
            d2 = math.sqrt(dx2 ** 2 + dy2 ** 2)
            d3 = math.sqrt(dx3 ** 2 + dy3 ** 2)
            d4 = math.sqrt(dx4 ** 2 + dy4 ** 2)

            # check to see if all actions will result in being further from goal
            if d <= d1 and d <= d2 and d <= d3 and d <= d4:
                # we are as close as possible, break out of loop
                break
            # now take the action with the shortest resultant distance
            if d1 <= d2 and d1 <= d3 and d1 <= d4:
                self.takeStep(1, 1)
            elif d2 <= d1 and d2 <= d3 and d2 <= d4:
                self.takeStep(1, 2)
            elif d3 <= d1 and d3 <= d2 and d3 <= d4:
                self.takeStep(2, 1)
            elif d4 <= d1 and d4 <= d2 and d4 <= d3:
                self.takeStep(2, 2)

            print(self.currentPos)

    def closeEnough(self, point):
        if abs(self.currentPos[0] - point[0]) < self.rMotor.mmPerStepX:
            if abs(self.currentPos[1] - point[1]) < self.rMotor.mmPerStepY:
                if abs(self.currentPos[0] - point[0]) < self.thetaMotor.mmPerStepX:
                    if abs(self.currentPos[1] - point[1]) < self.thetaMotor.mmPerStepY:
                        return True
        return False

    def rMotorStepMovementUpdate(self):
        extensionPerStep = ((
                                    1.0 / self.rMotor.stepsPerRev) / self.rMotor.gearRatio) * self.rMotor.gearDiameter * math.pi

        self.rMotor.mmPerStepX = extensionPerStep * math.cos(self.currentTheta)
        self.rMotor.mmPerStepY = extensionPerStep * math.sin(self.currentTheta)

    def thetaMotorStepMovementUpdate(self):
        degreeChangePerStep = ((1 / self.thetaMotor.stepsPerRev) / self.thetaMotor.gearRatio) * 2 * math.pi
        self.thetaMotor.mmPerStepX = self.currentR * math.cos(
            self.currentTheta + degreeChangePerStep) - self.currentR * math.cos(self.currentTheta)
        self.thetaMotor.mmPerStepY = self.currentR * math.sin(
            self.currentTheta + degreeChangePerStep) - self.currentR * math.sin(self.currentTheta)

    def updateTheta(self):
        thetaStepsPerRev = self.thetaMotor.stepsPerRev * self.thetaMotor.gearRatio
        self.currentTheta = 2 * math.pi * (self.thetaMotor.stepCount % thetaStepsPerRev) / thetaStepsPerRev
        self.updateCurrentPos()

    def updateRadius(self):
        self.currentR = (self.rMotor.stepCount / self.rMotor.stepsPerRev) * self.rMotor.gearDiameter * math.pi
        self.updateCurrentPos()

    def updateCurrentPos(self):
        currentX = self.currentR * math.cos(self.currentTheta)
        currentY = self.currentR * math.sin(self.currentTheta)

        self.currentPos = [currentX, currentY]

    def setOrigin(self):
        #self.currentPos = self.traj[0]
        self.currentPos = [0.0,0.0]
        self.origin = self.currentPos
