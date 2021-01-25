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
            # print("Motor " + self.name + " step forward")
            self.stepCount += 1
        elif direction == 2:
            # print("Motor " + self.name + " step backward")
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
        startPoint = self.currentPos
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

            p1x = self.currentPos[0] + self.rMotor.mmPerStepX
            p1y = self.currentPos[1] + self.rMotor.mmPerStepY
            p2x = self.currentPos[0] - self.rMotor.mmPerStepX
            p2y = self.currentPos[1] - self.rMotor.mmPerStepY
            p3x = self.currentPos[0] + self.thetaMotor.mmPerStepX
            p3y = self.currentPos[1] + self.thetaMotor.mmPerStepY
            p4x = self.currentPos[0] - self.thetaMotor.mmPerStepX
            p4y = self.currentPos[1] - self.thetaMotor.mmPerStepY


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
            d1t = math.sqrt(dx1 ** 2 + dy1 ** 2)
            d2t = math.sqrt(dx2 ** 2 + dy2 ** 2)
            d3t = math.sqrt(dx3 ** 2 + dy3 ** 2)
            d4t = math.sqrt(dx4 ** 2 + dy4 ** 2)

            d1 = self.pointLineDist(point[0],point[1],startPoint[0],startPoint[1],p1x,p1y)
            d2 = self.pointLineDist(point[0], point[1],startPoint[0],startPoint[1], p2x, p2y)
            d3 = self.pointLineDist(point[0], point[1],startPoint[0],startPoint[1], p3x, p3y)
            d4 = self.pointLineDist(point[0], point[1],startPoint[0],startPoint[1], p4x, p4y)

            if d < d1t:
                d1 = 0
            if d < d2t:
                d2 = 0
            if d < d3t:
                d3 = 0
            if d < d4t:
                d4 = 0


            if d <= d1 or d <= d2 or d <= d3 or d <= d4:
                d1 = d1t
                d2 = d2t
                d3 = d3t
                d4 = d4t

            # check to see if all actions will result in being further from goal
            if (d <= d1 or d1 == 0) and (d <= d2 or d2 == 0) and (d <= d3 or d3 ==0) and (d <= d4 or d4 ==0):
                # we are as close as possible, break out of loop
                break

            distanceList = [d1,d2,d3,d4]
            minDistance = min([x for x in distanceList if x != 0])
            minDistance = distanceList.index(minDistance)

            if minDistance == 0:
                self.takeStep(1, 1)
            elif minDistance == 1:
                self.takeStep(1, 2)
            elif minDistance == 2:
                self.takeStep(2, 1)
            else:
                self.takeStep(2, 2)

            print(self.currentPos)

    def closeEnough(self, point):
        if abs(self.currentPos[0] - point[0]) < abs(self.rMotor.mmPerStepX*2):
            if abs(self.currentPos[1] - point[1]) < abs(self.rMotor.mmPerStepY*2):
                if abs(self.currentPos[0] - point[0]) < abs(self.thetaMotor.mmPerStepX*2):
                    if abs(self.currentPos[1] - point[1]) < abs(self.thetaMotor.mmPerStepY*2):
                        return True
        return False

    def rMotorStepMovementUpdate(self):
        extensionPerStep = (1.0 / self.rMotor.stepsPerRev) * self.rMotor.gearDiameter * math.pi


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
        currentX = self.origin[0] + self.currentR * math.cos(self.currentTheta)
        currentY = self.origin[1] + self.currentR * math.sin(self.currentTheta)

        self.currentPos = [currentX, currentY]

    def setOrigin(self):
        # self.currentPos = self.traj[0]
        self.currentPos = self.traj[0]
        self.origin = self.currentPos

    def pointLineDist(self, x1, y1, x2, y2, x3, y3):  # x3,y3 is the point
        px = x2 - x1
        py = y2 - y1

        norm = px * px + py * py

        u = ((x3 - x1) * px + (y3 - y1) * py) / float(norm)

        if u > 1:
            u = 1
        elif u < 0:
            u = 0

        x = x1 + u * px
        y = y1 + u * py

        dx = x - x3
        dy = y - y3

        # Note: If the actual distance does not matter,
        # if you only want to compare what this function
        # returns to other results of this function, you
        # can just return the squared distance instead
        # (i.e. remove the sqrt) to gain a little performance

        dist = (dx * dx + dy * dy) ** .5

        return dist
