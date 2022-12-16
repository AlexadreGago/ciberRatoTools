import sys
from croblink import *
from math import *
import xml.etree.ElementTree as ET

CELLROWS = 7
CELLCOLS = 14
motorStrengthMap = {
    "front": (0.15, 0.15),
    "frontslow": (0.03, 0.03),
    "backward": (-0.15, -0.15),
    "left": (-0.15, 0.15),
    "right": (0.15, -0.15),
    "slightLeft": (0.13, 0.15),
    "slightRight": (0.15, 0.13),
    "stoppedRight": (0.03, -0.03),
    "stoppedLeft": (-0.03, 0.03),
    "stop": (0, 0)
}
slowmotorStrengthMap = {
    "front": (0.06, 0.06),
    "frontslow": (0.03, 0.03),
    "backward": (-0.06, -0.06),
    "left": (-0.06, 0.06),
    "right": (0.06, -0.06),
    "slightLeft": (0.04, 0.06),
    "slightRight": (0.06, 0.04),
    "stoppedRight": (0.04, -0.04),
    "stoppedLeft": (-0.04, 0.04),
    "stop": (0, 0)
}
directionMap = {
    "right": 0,
    "up": 90,
    "left": -180,
    "down": -90
}

inverseDirectionMap = {
    "left": "right",
    "right": "left",#{"left": "up", "right": "down"},
    "up": "down",
    "down": "up"
}

directions = ["right", "down", "left", "up"]



lastdecision = "stop"

def roundPowerOf2(x):
    """round to nearest multiple of 2

    Args:
        x (float): the number to round

    Returns:
        int: the rounded number
    """
    return int(round(x / 2.0)) * 2

class MyRob(CRobLinkAngs):
    """The robot class

    """

    def __init__(self, rob_name, rob_id, angles, host):
        CRobLinkAngs.__init__(self, rob_name, rob_id, angles, host)
        self.x = 0
        self.y = 0
        self.prevVertex = (0,0)
        self.state = "wander"
        self.direction = "right"
        
        self.LastLPower = 0
        self.LastRPower = 0
        self. lastoutR = 0
        self.lastoutL = 0
        self.lastx = 0
        self.lasty = 0
        
        self.blockTurns = 0
        
        self.initialx = 0
        self.initialy = 0

        self.rightCounter = 0
        self.leftCounter = 0
        self.calls = 0
        self.turnDirection = ""

    # In this map the center of cell (i,j), (i in 0..6, j in 0..13) is mapped to labMap[i*2][j*2].
    # to know if there is a wall on top of cell(i,j) (i in 0..5), check if the
    # value of labMap[i*2+1][j*2] is space or not

    def setMap(self, labMap):
        self.labMap = labMap

    def printMap(self):
        for l in reversed(self.labMap):
            print(''.join([str(l) for l in l]))

    def run(self):
        """the main loop of the robot
        This function contains the main logic of the robot, represented by its state.

        Args:
            None

        Returns:
            None
        """
        if self.status != 0:
            print("Connection refused or error")
            quit()

        self.readSensors()
        self.initialx = self.measures.x
        self.initialy = self.measures.y
        while True:

            if self.measures.stop:
                self.readSensors()
            if self.measures.start:
                if self.state == "vertexDiscovery":
                    self.vertexDiscovery(self.direction)
                elif self.state == "turning":
                    self.turning()
                else:
                    self.wander()
    
    
    def updateGPS(self,inLPower,inRPower, correction = False):
        """update the GPS coordinates of the robot

        Args:
            direction (str): the direction of the robot
            correction (bool, optional): if the update is a correction. Defaults to False.

        Returns:
            None
        """
        outL = (inLPower + self.lastoutL)/2 #we dont have noise value
        outR = (inRPower + self.lastoutR)/2
        lin = (outL + outR)/2

        if correction:
            #snap to grid coordinates, sensors are 0.438m in front of the center of the robot
            if self.direction == "right":
                self.x = roundPowerOf2(self.x) - 0.438
            elif self.direction == "left":
                self.x = roundPowerOf2(self.x) + 0.438
            elif self.direction == "up":
                self.y = roundPowerOf2(self.y) - 0.438
            elif self.direction == "down":
                self.y = roundPowerOf2(self.y) + 0.438
            # print("corrected to: ", self.x, self.y)
          
        else:
            
            if self.direction in {"right", "left"}:
                self.x = self.lastx + (lin) # * cos(radians(self.measures.compass)
                y = self.lasty + (lin * sin(radians(self.measures.compass)))
                self.y = roundPowerOf2(y)
            
            if self.direction in {"up", "down"}:
                self.y = self.lasty + (lin * sin(radians(self.measures.compass)))
                x = self.lastx + (lin * cos(radians(self.measures.compass)))
                self.x = roundPowerOf2(x)
        
        self.lastoutL = outL
        self.lastoutR = outR
        self.lastx = self.x
        self.lasty = self.y
        return
    
    def nextDirection(self, turn):
        """get the next direction of the robot

        Args:
            turn (str): the direction to turn

        Returns:
            str: the next direction
        """
        if turn == "right":
            return directions[(directions.index(self.direction) + 1) % 4]
        else:
            return directions[(directions.index(self.direction) - 1) % 4]

    
    def vertexDiscovery(self,direction):
        """turn the robot

        Args:
            direction (str): the direction to turn

        Returns:
            None
        """
        # print(self.measures.lineSensor)
       
        if self.calls == 0:

            self.rightCounter += int(self.measures.lineSensor[5])
            self.rightCounter += int(self.measures.lineSensor[6])
            
            self.leftCounter += int(self.measures.lineSensor[0])
            self.leftCounter += int(self.measures.lineSensor[1])

            self.move("frontslow")
            self.calls += 1 
            
            print("first call")

        elif self.calls == 1:
            print("second call")
            
            self.rightCounter += int(self.measures.lineSensor[5])
            self.rightCounter += int(self.measures.lineSensor[6])
            
            self.leftCounter += int(self.measures.lineSensor[0])
            self.leftCounter += int(self.measures.lineSensor[1])

            self.calls += 1 
            slight = True
            if self.rightCounter > 2:
                print("certain right turn")
                self.turnDirection = "right"

                self.direction = self.nextDirection("right")
                self.move("front")
                self.state = "turning"
                slight = False
                
            if self.leftCounter > 2:
                print("certain left turn")
                self.turnDirection = "left"
                self.move("front")

                self.direction = self.nextDirection("left")

                self.state = "turning"
                slight = False

            # NOT A TURN SO, SLIGHT TURN FIRST BY WHICH COUNTER IS HGIGHER THEN BY COMPASS
            if slight:
                if self.rightCounter < self.leftCounter:
                    print("noiseeeeeeeeeeeeeeeeeeeeeeeeeeeee biiiiiiiiiiiiiiiiiitch")
                    self.move("slightLeft")
                elif self.rightCounter > self.leftCounter:
                    print("noiseeeeeeeeeeeeeeeeeeeeeeeeeeeee biiiiiiiiiiiiiiiiiitch")
                    self.move("slightRight")
                else:
                    if self.measures.compass < directionMap[self.direction]:
                        print("noiseeeeeeeeeeeeeeeeeeeeeeeeeeeee biiiiiiiiiiiiiiiiiitch")

                        self.move("slightLeft") 
                    else:
                        print("noiseeeeeeeeeeeeeeeeeeeeeeeeeeeee biiiiiiiiiiiiiiiiiitch")
                        self.move("slightRight") 


        else:
            print("third call")
            self.calls = 0
            self.rightCounter = 0
            self.leftCounter = 0
            self.state = "wander"
            
                
            # else: self.state = "wander"   
    def turning(self):

        print("PUTA",self.direction,self.measures.lineSensor)

        if self.turnDirection =="":
            self.state="wander"
        if self.turnDirection == "right":
            if self.measures.compass > directionMap[self.direction] -4 :
                # if int(self.measures.lineSensor[0])+int(self.measures.lineSensor[1])+int(self.measures.lineSensor[5])+int(self.measures.lineSensor[6]) ==0:
                #     #FUCKUP GO BACK
                #     print("fuckup")
                #     self.state = "vertexDiscovery"
                #     self.turnDirection = ""
                #     self.calls = 0
                #     self.rightCounter = 0
                #     self.leftCounter = 0
                #     self.direction = self.nextDirection("right")
                # else:
                print("im aligned")
                self.state="wander"
                self.turnDirection=""
                
            elif(self.measures.lineSensor[6] == "1"):
                self.move("right")
            elif(self.measures.lineSensor[5]=="1"):
                self.move("slightRight")
            else:
                self.move("stoppedRight")
                
        if self.turnDirection == "left":
            if self.measures.compass < directionMap[self.direction]+8 :
                # if int(self.measures.lineSensor[0])+int(self.measures.lineSensor[1])+int(self.measures.lineSensor[5])+int(self.measures.lineSensor[6]) ==0:
                #     #FUCKUP GO BACK
                #     print("fuckup")
                #     self.state = "vertexDiscovery"
                #     self.turnDirection = ""
                #     self.calls = 0
                #     self.rightCounter = 0
                #     self.leftCounter = 0
                #     self.direction = self.nextDirection("right")
                # else:
                print("im aligned")
                self.state="wander"
                self.turnDirection=""
                
            elif(self.measures.lineSensor[0] == "1"):
                self.move("left")
            elif(self.measures.lineSensor[1]=="1"):
                self.move("slightLeft")
            else:
                self.move("stoppedLeft")
                


            #! eventually check for fucck
            # elif self.measures.lineSensor == ["0", "0", "0", "0", "0", "0", "0"]:
            #     # self.state="vertexDiscovery"
            #     # self.detectedsensors = self.measures.lineSensor
            #     self.move("right")
            # else:
            #     self.move("front")

            
            
    def move(self, direction):
        print("direction: ", direction)
        
        if self.direction in {"right", "left"}:

            if self.x % 2 < 0.8 or self.x % 2 > 1.2:
                #SLOW EVERYTHING DOWN
                self.driveMotors(*slowmotorStrengthMap[direction])
                self.updateGPS(*slowmotorStrengthMap[direction])
            else:
                #GO FAST
                self.driveMotors(*motorStrengthMap[direction])
                self.updateGPS(*motorStrengthMap[direction])
        else:
            if self.y % 2 < 0.8 or self.y % 2 > 1.2:
                #SLOW EVERYTHING DOWN
                self.driveMotors(*slowmotorStrengthMap[direction])
                self.updateGPS(*slowmotorStrengthMap[direction])
            else:
                #GO FAST
                self.driveMotors(*motorStrengthMap[direction])
                self.updateGPS(*motorStrengthMap[direction])
            
        
        self.readSensors()
        
        # print("x: " + str(self.x) + " y: " + str(self.y))
        # print("compass: " + str(self.measures.compass))
        # print("gpsx: " + str(self.measures.x-self.initialx) + " gpsy: " + str(self.measures.y-self.initialy))
        # print("------------------")
        
    # def vertexDiscovery(self):
    #     rightsensor = []
    #     leftsensor = []
    #     # adjustDistanceForward = 0.438
    #     print(self.detectedsensors)
    #     print(self.measures.lineSensor)
    #     # while self.adjustForward(adjustDistanceForward):
    #     #     if self.measures.lineSensor[6] == "1":
    #     #         rightsensor.append("1")
    #     #     if self.measures.lineSensor[0] == "1":
    #     #         leftsensor.append("1")
    #     #     print("adjustingForward")
    #     # while self.decideTurn():
    #     #     self.move("stop")
    #     #     print("decidingTurn")
    #     # while self.turn():
    #     #     print("turning")
    #     return 0
    
    def adjustForward(self, remDistance):
        if (done):
            return 1
        self.move("front")
        remDistance -= 0.30
        return 0
    
    def decideTurn(self):
        if decided:
            self.decision = decidedDirection
            return 1
        return 0
    
    def turn(self):
        if turned:
            self.prevVertex = (self.x, self.y)
            self.direction = direction
            return 1
        
        return 0
            

    def allowTurns(self):
        if abs(self.x - self.prevVertex[0]) >1.5  or abs(self.y - self.prevVertex[1]) >1.5:
            self.blockTurns = 0
        self.blockTurns = 1
        return
        
    def wander(self):
        # print("wander")
        # print(self.measures.lineSensor)
        # self.allowTurns()
        # if these sensors are "1" check if we´re near vertex
            
        if (int(self.measures.lineSensor[5]) + int(self.measures.lineSensor[6])>= 1):
            # print("wandervertexDiscovery")
            self.state="vertexDiscovery"
            self.rightCounter = 0
            self.leftCounter = 0
            
        # turn slightly left if right edge detected
        elif (int(self.measures.lineSensor[0]) + int(self.measures.lineSensor[1])>= 1):
            # print("wandervertexDiscovery")
            self.state="vertexDiscovery"
            self.rightCounter = 0
            self.leftCounter = 0
            
        # go front if 3 middle sensors detect line
        elif (int(self.measures.lineSensor[3])+int(self.measures.lineSensor[2])+ int(self.measures.lineSensor[4])) >= 1 :
            self.move("front")

        elif self.measures.lineSensor == ["0", "0", "0", "0", "0", "0", "0"]:
            # self.state="vertexDiscovery"
            # self.detectedsensors = self.measures.lineSensor
            self.move("right")
        else:
            self.move("front")


class Map():
    def __init__(self, filename):
        tree = ET.parse(filename)
        root = tree.getroot()

        self.labMap = [[' '] * (CELLCOLS * 2 - 1)
                       for i in range(CELLROWS * 2 - 1)]
        i = 1
        for child in root.iter('Row'):
            line = child.attrib['Pattern']
            row = int(child.attrib['Pos'])
            if row % 2 == 0:  # this line defines vertical lines
                for c in range(len(line)):
                    if (c + 1) % 3 == 0:
                        if line[c] == '|':
                            self.labMap[row][(c + 1) // 3 * 2 - 1] = '|'
                        else:
                            None
            else:  # this line defines horizontal lines
                for c in range(len(line)):
                    if c % 3 == 0:
                        if line[c] == '-':
                            self.labMap[row][c // 3 * 2] = '-'
                        else:
                            None

            i = i + 1


rob_name = "pClient1"
host = "localhost"
pos = 1
mapc = None

for i in range(1, len(sys.argv), 2):
    if (sys.argv[i] == "--host" or sys.argv[i]
            == "-h") and i != len(sys.argv) - 1:
        host = sys.argv[i + 1]
    elif (sys.argv[i] == "--pos" or sys.argv[i] == "-p") and i != len(sys.argv) - 1:
        pos = int(sys.argv[i + 1])
    elif (sys.argv[i] == "--robname" or sys.argv[i] == "-r") and i != len(sys.argv) - 1:
        rob_name = sys.argv[i + 1]
    elif (sys.argv[i] == "--map" or sys.argv[i] == "-m") and i != len(sys.argv) - 1:
        mapc = Map(sys.argv[i + 1])
    else:
        print("Unkown argument", sys.argv[i])
        quit()

if __name__ == '__main__':
    rob = MyRob(rob_name, pos, [0.0, 60.0, -60.0, 180.0], host)
    if mapc is not None:
        rob.setMap(mapc.labMap)
        rob.printMap()

    rob.run()
