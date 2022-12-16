import sys
from croblink import *
from math import *
import xml.etree.ElementTree as ET


class bcolors:
    """class for colors in the terminal

    """
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


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
    "stoppedRight": (0.15, -0.15),
    "stoppedLeft": (-0.15, 0.15),
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
                    self.vertexDiscovery()
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

    
    def vertexDiscovery(self):
        """checks if a vertex exists in front of the robot"""
        # print(self.measures.lineSensor)
        print(f"{bcolors.HEADER}vertexDiscovery{bcolors.ENDC}")
        if self.calls == 0:

            self.rightCounter += int(self.measures.lineSensor[5])
            self.rightCounter += int(self.measures.lineSensor[6])
            
            self.leftCounter += int(self.measures.lineSensor[0])
            self.leftCounter += int(self.measures.lineSensor[1])

            self.move("frontslow")
            self.calls += 1 
            
            print(f"\t{bcolors.HEADER}first call{bcolors.ENDC}")
            print(f"\t\t{bcolors.OKBLUE}rightCounter: {self.rightCounter}{bcolors.ENDC}")
            print(f"\t\t{bcolors.OKBLUE}leftCounter: {self.leftCounter}{bcolors.ENDC}")

        elif self.calls == 1:
            
            
            self.rightCounter += int(self.measures.lineSensor[5])
            self.rightCounter += int(self.measures.lineSensor[6])
            
            self.leftCounter += int(self.measures.lineSensor[0])
            self.leftCounter += int(self.measures.lineSensor[1])

            print(f"\t{bcolors.HEADER}second call{bcolors.ENDC}")
            print(f"\t\t{bcolors.OKBLUE}rightCounter:{bcolors.ENDC} {bcolors.OKGREEN} {self.rightCounter}{bcolors.ENDC}")
            print(f"\t\t{bcolors.OKBLUE}leftCounter:{bcolors.ENDC} {bcolors.OKGREEN} {self.leftCounter}{bcolors.ENDC}")

            self.calls += 1 

            if self.rightCounter > 2:
                print(f"\t{bcolors.OKGREEN}certain right turn{bcolors.ENDC}")
                self.turnDirection = "right"
                self.direction = self.nextDirection("right")
                self.move("front")

                self.state = "wander"
                return
                
            # if self.leftCounter > 2:
            #     print("certain left turn")
            #     self.turnDirection = "left"
            #     self.move("front")

            #     self.direction = self.nextDirection("left")

            #     self.state = "turning"
            #     slight = False

            print(f"\t{bcolors.WARNING}Noise{bcolors.ENDC}")
            if self.rightCounter < self.leftCounter:
                
                self.move("slightLeft")
            elif self.rightCounter > self.leftCounter:
                self.move("slightRight")
            else:
                if self.measures.compass < directionMap[self.direction]:
                    self.move("slightLeft") 
                else:
                    self.move("slightRight") 


        else:
            print(f"\t{bcolors.OKBLUE}third call{bcolors.ENDC}")
            self.calls = 0
            self.rightCounter = 0
            self.leftCounter = 0
            self.state = "wander"
            
                
            # else: self.state = "wander"   
    def turning(self):
        return
      
            
            
    def move(self, direction):
        print(f"{bcolors.FAIL}move{bcolors.ENDC}")
        
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

        
    def wander(self):
        print(f"{bcolors.HEADER}wander{bcolors.ENDC}")
        if (int(self.measures.lineSensor[5]) + int(self.measures.lineSensor[6])):
            if self.direction in {"right", "left"}:
                if self.x % 2 < 0.5 or self.x % 2 > 1.5:
                    self.state="vertexDiscovery"
                    self.rightCounter = 0
                    self.leftCounter = 0
                else:
                    print(f"\t{bcolors.WARNING}anti fuck up{bcolors.ENDC}")
                    self.move("slightRight")
            else:
                if self.y % 2 < 0.5 or self.y % 2 > 1.5:
                    self.state="vertexDiscovery"
                    self.rightCounter = 0
                    self.leftCounter = 0
                else:
                    print(f"\t{bcolors.WARNING}anti fuck up{bcolors.ENDC}")
                    self.move("slightRight")
    
        # turn slightly left if right edge detected
        elif (int(self.measures.lineSensor[0]) + int(self.measures.lineSensor[1])):
            if self.direction in {"right", "left"}:
                if self.x % 2 < 0.5 or self.x % 2 > 1.5:
                    self.state="vertexDiscovery"
                    self.rightCounter = 0
                    self.leftCounter = 0
                else:
                    print(f"\t{bcolors.WARNING}anti fuck up{bcolors.ENDC}")
                    self.move("slightLeft")
            else:
                if self.y % 2 < 0.5 or self.y % 2 > 1.5:
                    self.state="vertexDiscovery"
                    self.rightCounter = 0
                    self.leftCounter = 0
                else:
                    print(f"\t{bcolors.WARNING}anti fuck up{bcolors.ENDC}")
                    self.move("slightLeft")
            
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
