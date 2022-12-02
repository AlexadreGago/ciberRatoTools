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
    "right": "left",
    "up": "down",
    "down": "up"
}

lastdecision = "stop"


class MyRob(CRobLinkAngs):
    """The robot class

    """

    def __init__(self, rob_name, rob_id, angles, host):
        CRobLinkAngs.__init__(self, rob_name, rob_id, angles, host)
        self.x = 0
        self.y = 0
        self.prevVertex = (0,0)
        
        LastRPower = 0
        LastLPower = 0
        lastoutR = 0
        lastoutL = 0
        lastx = 0
        lasty = 0
        
        self.blockTurns = 0

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

        while True:

            if self.measures.stop:
                self.readSensors()
            if self.measures.start:
                if self.state == "vertexDiscovery":
                    self.vertexDiscovery()
                else:
                    self.wander()
    
    def roundPowerOf2(x):
        """round to nearest multiple of 2

        Args:
            x (float): the number to round

        Returns:
            int: the rounded number
        """
        return int(round(x / 2.0)) * 2
    
    def updateGPS(self,direction):
        inLPower, inRPower = motorStrengthMap[direction]
        outL = (inLPower + self.lastoutL)/2 #we dont have noise value
        outR = (inRPower + self.lastoutR)/2
        lin = (outL + outR)/2
        
        if self.direction in {"right", "left"}:
            self.x = self.lastx + (lin * cos((self.measures.compass)))
            y = self.lasty + (lin * sin(directionMap[self.direction]))
            self.y = self.roundPowerOf2(y)
        
        if self.direction in {"up", "down"}:
            self.y = self.lasty + (lin * sin(directionMap[self.direction]))
            x = self.lastx + (lin * cos(directionMap[self.direction]))
            self.x = self.roundPowerOf2(x)
        
        self.lastoutL = outL
        self.lastoutR = outR
        self.lastx = self.x
        self.lasty = self.y
        return
        
    def move(self, direction):
        self.driveMotors(0.15, 0.15)
        
        self.updateGPS(direction)
        print("x: " + str(self.x) + " y: " + str(self.y))
        self.readSensors()
        
    def vertexDiscovery(self):
        rightsensor = []
        leftsensor = []
        adjustDistanceForward = 0.438
        while self.adjustForward(adjustDistanceForward):
            if self.measures.lineSensor[6] == "1":
                rightsensor.append("1")
            if self.measures.lineSensor[0] == "1":
                leftsensor.append("1")
            print("adjustingForward")
        while self.decideTurn():
            self.move("stop")
            print("decidingTurn")
        while self.turn():
            print("turning")
        return 0
    
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
        # self.allowTurns()
        # if these sensors are "1" check if we´re near vertex
        # if (((self.measures.lineSensor[:2].count("1") >= 2)
        #         or self.measures.lineSensor[5:7].count("1") >= 2 )
        #         and not self.blockTurns):
            
        #     # self.state="vertexDiscovery"
        #     #self.detectedsensors = self.measures.lineSensor
        #     print(self.x)
        #     print(self.y)
        #     self.blockTurns = 1
        #     # self.move("stop")
            
        if (int(self.measures.lineSensor[5]) + int(self.measures.lineSensor[6])>= 1):
            self.move("slightRight")
            
        # turn slightly left if right edge detected
        elif (int(self.measures.lineSensor[0]) + int(self.measures.lineSensor[1])>= 1):
            self.move("slightLeft")
            
        # go front if 3 middle sensors detect line
        elif (int(self.measures.lineSensor[3])+int(self.measures.lineSensor[2]+ int(self.measures.linesensor(4))) >= 1 ):
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
