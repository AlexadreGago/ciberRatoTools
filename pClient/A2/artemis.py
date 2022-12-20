import math
import sys
from croblink import *
from math import *
import xml.etree.ElementTree as ET
import itertools


class bcolors:
    """class for colors in the terminal
    """
    BOLD = '\033[1m'
    DARK = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    INVERT = '\033[7m'
    HIDDEN = '\033[8m'

    GREY = '\033[90m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'

    RESET = '\033[0m'


CELLROWS = 7
CELLCOLS = 14
MOTORSTRENGTHMAP = {
    "front": (0.12, 0.12),
    "frontslow": (0.03, 0.03),
    "backward": (-0.12, -0.12),
    "left": (-0.12, 0.12),
    "right": (0.12, -0.12),
    "slightLeft": (0.10, 0.12),
    "slightRight": (0.12, 0.10),
    "stop": (0, 0)
}
SLOWMOTORSTRENGTHMAP = {
    "front": (0.06, 0.06),
    "frontslow": (0.02, 0.02),
    "backward": (-0.06, -0.06),
    "left": (-0.06, 0.06),
    "right": (0.06, -0.06),
    "slightLeft": (0.03, 0.06),
    "slightRight": (0.06, 0.03),
    "stop": (0, 0)
}
DIRECTIONMAP = {
    "right": 0,
    "up": 90,
    "left": -180,
    "down": -90
}

INVERSEDIRECTIONMAP = {
    "left": "right",
    "right": "left",  # {"left": "up", "right": "down"},
    "up": "down",
    "down": "up"
}

TURNSMAP = {
    "right": {"right": "down", "left": "up", "front": "right", "back": "left"},
    "left": {"right": "up", "left": "down", "front": "left", "back": "right"},
    "up": {"right": "right", "left": "left", "front": "up", "back": "down"},
    "down": {"right": "left", "left": "right", "front": "down", "back": "up"}
}

PRIORITY = ["down", "right", "up", "left"]


class Vertex():
    """A vertex in the graph

    Attributes:
        x (int): x coordinate
        y (int): y coordinate
        edges (dict): a dictionary of edges, keys are directions, values are 0 for nonexistant, 1 for exists but unexplored, 2 for exists and explored
        connects (dict): a dictionary of vertices that this vertex connects to, keys are directions, values are the vertex
        id (int): the id of the vertex
        isDeadEnd (bool): whether this vertex is a dead end

    Methods:
        __init__(x,y): initializes the vertex
        __repr__(): returns a string representation of the vertex

    """
    id_iter = itertools.count()

    def __init__(self, x=-1, y=-1):
        self.x = x
        self.y = y
        # 0 unknown; 1 exists but unexplred ; 2 -Exists and explored ;
        self.edges = {"up": 0,
                      "down": 0,
                      "left": 0,
                      "right": 0}
        self.connects = {}
        self.id = next(Vertex.id_iter)
        self.isDeadEnd = False

    def __repr__(self) -> str:
        return f"Vertex {self.id} at ({self.x},{self.y}), edges: {self.edges}, connects: {self.connects} \n"

    def __eq__(self, o: list) -> bool:
        # get coordinates and check if equal to list of coordinates
        return (self.x, self.y) == (o[0], o[1])

    def update(self, robot_dir, turns):
        """updates the possible turns of this vertex
        #! in the future, update the connects as well
        #! also estamos a deixar dar overwrite sempre que passa por um vertice, nao sei se e bom

        Args:
            robot_dir (str): the direction the robot is facing
            turns (dict): the turns list

        Returns:
            None
        """
        # # update the edges
        # print(f"updating vertex {self.id} {self.edges}")
        # print(f"robot_dir: {robot_dir}")
        # print(f"turns: {turns}")

        for turn in turns:
            edge = TURNSMAP[robot_dir][turn]
            if self.edges[edge] == 0:
                self.edges[edge] = 1

    def getDirections(self):
        """returns the possible turns from this vertex

        Args:
            robot_dir (str): the direction the robot is facing

        Returns:
            list: the possible turns
        """
        return [
            direction for direction in self.edges
            if self.edges[direction] == 1
        ]


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
        self.prevVertex = (0, 0)
        self.state = "wander"
        self.direction = "right"

        self.LastLPower = 0
        self.LastRPower = 0
        self. lastoutR = 0
        self.lastoutL = 0
        self.lastx = 0
        self.lasty = 0

        self.initialx = 0
        self.initialy = 0

        self.turnDirection = ""

        self.vertexList = []

        self.detectedSensorsCount = [0, 0, 0, 0, 0, 0, 0, 0]

    # In this map the center of cell (i,j), (i in 0..6, j in 0..13) is mapped to labMap[i*2][j*2].
    # to know if there is a wall on top of cell(i,j) (i in 0..5), check if the
    # value of labMap[i*2+1][j*2] is space or not

    def setMap(self, labMap):
        self.labMap = labMap

    def printMap(self):
        for l in reversed(self.labMap):
            print(''.join([str(l) for l in l]))

    def lineSensorsZero(self):
        """returns whether all the line sensors are '0'

        Args:
            None

        Returns:
            bool: whether all the line sensors are '0'
        """
        # ?------------------------------LOGGING----------------------------
        # print(f"lineSensorsZero: {self.measures.lineSensor.count('0') == 7}")
        # ?-----------------------------------------------------------------
        return self.measures.lineSensor.count("0") == 7

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
        id_iter = itertools.count()
        while True:
            print(next(id_iter))
            if self.measures.stop:
                self.readSensors()
            if self.measures.start:
                if self.state == "vertexDiscovery":
                    self.vertexDiscovery()
                elif self.state == "turning":
                    self.turning()
                elif self.state == "decide":
                    self.decide()
                elif self.state == "adjustForward":
                    self.adjustForward()
                else:
                    self.wander()

    def updateGPS(self, inLPower, inRPower, correction=False):
        """update the GPS coordinates of the robot

        Args:
            direction (str): the direction of the robot
            correction (bool, optional): if the update is a correction. Defaults to False.

        Returns:
            None
        """
        outL = (inLPower + self.lastoutL) / 2  # we dont have noise value
        outR = (inRPower + self.lastoutR) / 2
        lin = (outL + outR) / 2

        if correction:
            # snap to grid coordinates, sensors are 0.438m in front of the
            # center of the robot
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
                # * cos(radians(self.measures.compass)
                self.x = self.lastx + (lin)
                y = self.lasty + (lin * sin(radians(self.measures.compass)))
                self.y = roundPowerOf2(y)

            if self.direction in {"up", "down"}:
                self.y = self.lasty + \
                    (lin * sin(radians(self.measures.compass)))
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
            return TURNSMAP[self.direction]["right"]
        else:
            return TURNSMAP[self.direction]["left"]

    def getVertex(self):
        """create a vertex in the current position of the robot or return the existing one

        Args:
            None

        Returns:
            Vertex: the vertex created or updated
        """
        roundedcoords = (roundPowerOf2(self.x), roundPowerOf2(self.y))

        # go read __eq__ method in Vertex class
        vertex = [vertex for vertex in self.vertexList if vertex == roundedcoords]
        if vertex:
            vertex = vertex[0]
            #!neste momento so curvas, dps tem de ter connects

        else:
            vertex = Vertex(*roundedcoords)
            #!do this now? or after turning?
            self.vertexList.append(vertex)
        return vertex

    def move(self, direction="", override=False, leftPower: float = 0, rightPower: float = 0):
        # ?------------------------------LOGGING----------------------------
        print(f"{bcolors.PURPLE}move{bcolors.RESET}")
        print(f"\tdirection: {direction}")
        print(f"\tself.direction: {self.direction}")
        # ?-----------------------------------------------------------------
        if not override:
            if self.direction in {"right", "left"}:

                if self.x % 2 < 0.5 or self.x % 2 > 1.5:
                    # SLOW EVERYTHING DOWN
                    print("\t Motors strength:", *SLOWMOTORSTRENGTHMAP[direction])          
                    self.driveMotors(*SLOWMOTORSTRENGTHMAP[direction])
                    self.updateGPS(*SLOWMOTORSTRENGTHMAP[direction])
                else:
                    # GO FAST
                    print("\t Motors strength:", *SLOWMOTORSTRENGTHMAP[direction])          
                    
                    self.driveMotors(*MOTORSTRENGTHMAP[direction])
                    self.updateGPS(*MOTORSTRENGTHMAP[direction])
            else:
                if self.y % 2 < 0.5 or self.y % 2 > 1.3:
                    # SLOW EVERYTHING DOWN
                    print("\t Motors strength:", *SLOWMOTORSTRENGTHMAP[direction])          
                    
                    self.driveMotors(*SLOWMOTORSTRENGTHMAP[direction])
                    self.updateGPS(*SLOWMOTORSTRENGTHMAP[direction])
                else:
                    # GO FAST
                    print("\t Motors strength:", *SLOWMOTORSTRENGTHMAP[direction])          
                    
                    self.driveMotors(*MOTORSTRENGTHMAP[direction])
                    self.updateGPS(*MOTORSTRENGTHMAP[direction])
        else:
            print("\t Motors strength:",leftPower,rightPower )          
            self.driveMotors(leftPower, rightPower)
            self.updateGPS(leftPower, rightPower)
        self.readSensors()

    def vertexDiscovery(self):
        """checks if a vertex exists in front of the robot and its turns"""
        # print(self.measures.lineSensor)
        # ?------------------------------LOGGING----------------------------
        print(f"{bcolors.PURPLE}vertexDiscovery{bcolors.RESET}")
        # ?-----------------------------------------------------------------
        rightCounter = {"lado": 0, "ponta": 0}
        leftCounter = {"lado": 0, "ponta": 0}
        turns = []
        for i in range(2):
            if i == 0:
                rightCounter["lado"] += int(self.measures.lineSensor[5])
                rightCounter["ponta"] += int(self.measures.lineSensor[6])

                leftCounter["ponta"] += int(self.measures.lineSensor[0])
                leftCounter["lado"] += int(self.measures.lineSensor[1])
                # ?------------------------------LOGGING----------------------------
                print(
                    f"\t{bcolors.PURPLE}first call{bcolors.RESET} {self.measures.lineSensor}")
                print(
                    f"\t\t{bcolors.CYAN}rightCounter: {rightCounter}{bcolors.RESET}")
                print(
                    f"\t\t{bcolors.CYAN}leftCounter: {leftCounter}{bcolors.RESET}")
                # ?-----------------------------------------------------------------
                self.move("stop")

            elif i == 1:
                rightCounter["lado"] += int(self.measures.lineSensor[4])
                rightCounter["ponta"] += int(self.measures.lineSensor[5])

                leftCounter["ponta"] += int(self.measures.lineSensor[1])
                leftCounter["lado"] += int(self.measures.lineSensor[2])
                # ?------------------------------LOGGING----------------------------
                print(
                    f"\t{bcolors.PURPLE}second call{bcolors.RESET} {self.measures.lineSensor}")
                print(
                    f"\t\t{bcolors.CYAN}rightCounter: {rightCounter}{bcolors.RESET}")
                print(
                    f"\t\t{bcolors.CYAN}leftCounter: {leftCounter}{bcolors.RESET}")

                if sum(rightCounter.values()) > 2 and rightCounter["ponta"] >= 1:
                    print(f"\t{bcolors.GREEN}right turn{bcolors.RESET}")
                    turns.append("right")
                if sum(leftCounter.values()) > 2 and leftCounter["ponta"] >= 1:
                    print(f"\t{bcolors.GREEN}left turn{bcolors.RESET}")
                    turns.append("left")

                if turns:
                    self.getVertex().update(self.direction, turns=turns)
                    self.state = "decide"
                    return

                # check if == 2 make a move to make a third reading and determine if it is a turn
                if sum(rightCounter.values()) == 2 or sum(leftCounter.values()) == 2:
                    self.move("stop")

                    rightCounter["lado"] += int(self.measures.lineSensor[5])
                    rightCounter["ponta"] += int(self.measures.lineSensor[6])

                    leftCounter["ponta"] += int(self.measures.lineSensor[0])
                    leftCounter["lado"] += int(self.measures.lineSensor[1])
                    # ?------------------------------LOGGING----------------------------
                    print(f"\t{bcolors.GREEN}third call{bcolors.RESET}")
                    print(
                        f"\t\t{bcolors.CYAN}rightCounter: {rightCounter}{bcolors.RESET}")
                    print(
                        f"\t\t{bcolors.CYAN}leftCounter: {leftCounter}{bcolors.RESET}")
                    # ?-----------------------------------------------------------------
                    if sum(rightCounter.values()) > 2 and rightCounter["ponta"] >= 1:
                        print(f"\t{bcolors.GREEN}right turn{bcolors.RESET}")
                        turns.append("right")
                    if sum(leftCounter.values()) > 2 and leftCounter["ponta"] >= 1:
                        print(f"\t{bcolors.GREEN}left turn{bcolors.RESET}")
                        turns.append("left")

                    if turns:
                        self.getVertex().update(self.direction, turns=turns)
                        self.state = "decide"
                        return
        # nothing found
        # ?------------------------------LOGGING----------------------------
        print(f"{bcolors.YELLOW}Noise{bcolors.RESET}")
        self.state = "wander"

    def turning(self):
        """turns the robot"""
        print(f"{bcolors.PURPLE}turning{bcolors.RESET}")
        print(self.measures.lineSensor)
        if self.turnDirection == "right":
            if self.measures.lineSensor[5] == 1 and self.measures.lineSensor[6] == 1:
                self.move("right")
                return
            elif self.measures.lineSensor[5] == 1:
                self.move("slightRight")
                return
            elif self.measures.lineSensor[2:5].count("1") >= 2:
                self.turnDirection = ""
                self.state = "wander"
                self.move("front")
                return

         # ------------------------------------
    def decide(self):
        """decides which way to go"""
        vertex = self.getVertex()
        # ?------------------------------LOGGING----------------------------
        print(f"{bcolors.PURPLE}decide{bcolors.RESET}")
        print(vertex)
        # ?-----------------------------------------------------------------

        # first position the robot in the center of the vertex
        self.detectedSensorsCount = [0, 0, 0, 0, 0, 0, 0, 0]
        while not self.adjustForward():
            pass

        # priority is down, right, up, left
        availableTurns = vertex.getDirections()
        if availableTurns:
            chosenDirection = [
                direction for direction in PRIORITY
                if direction in availableTurns
            ][0]

            print(f"{bcolors.CYAN}chosenDirection{bcolors.RESET} {chosenDirection}")

            while not self.orient(chosenDirection):
                pass

            print(f"{bcolors.CYAN}Estou orientado{bcolors.RESET} {chosenDirection}")
            self.direction = chosenDirection
            self.state = "wander"

    # ------------------------------------
    def adjustForward(self):
        """
           Positions the robot in the center of the vertex using our GPS (self.x,self.y)
           It records all the sensors captured in self.detectedSensorsCount

        return: Boolean True if the robot is in the center of the vertex else False

        """
        # ? ------------------------------LOGGING----------------------------
        if self.direction in ["right", "left"]:
            print(
                f"\t{bcolors.WHITE}{bcolors.UNDERLINE}Distance Left to center:{bcolors.RESET} {2* round(self.x/2) - self.x}")
        if self.direction in ["up", "down"]:
            print(
                f"\t{bcolors.WHITE}{bcolors.UNDERLINE}Distance Left to center:{bcolors.RESET} {2* round(self.y/2) - self.y}")
        # ?-----------------------------------------------------------------

        while not self.orient(self.direction):
            pass

        for i in range(7):
            self.detectedSensorsCount[i] += int(self.measures.lineSensor[i])
        self.detectedSensorsCount[7] += 1

        rem_distance = 0

        if self.direction == "right":
            rem_distance = roundPowerOf2(self.x) - self.x
        elif self.direction == "left":
            rem_distance = self.x - roundPowerOf2(self.x)
        elif self.direction == "up":
            rem_distance = roundPowerOf2(self.y) - self.y
        elif self.direction == "down":
            rem_distance = self.y - roundPowerOf2(self.y)

        if rem_distance > 0:
            if rem_distance > 0.1:
                self.move(override=True, leftPower=0.05, rightPower=0.05)
            else:
                self.move(override=True, leftPower=0.01, rightPower=0.01)
            return False
        else:
            #! WE CAN TAKE MORE CONCLUSION WITH THESE SENSORS
            # ? ------------------------------LOGGING----------------------------
            print("-----------------END ADJUST FORWARD-------------------")
            print(
                f"\t{bcolors.WHITE}{bcolors.UNDERLINE}Detected Sensors in Adjust Forward{bcolors.RESET} {self.detectedSensorsCount} \n")
            for i in range(7):
                print(self.detectedSensorsCount[i] /
                      self.detectedSensorsCount[7], '\n')
            print("Detected front?:", self.detectedSensorsCount[2] + self.detectedSensorsCount[3] +
                  self.detectedSensorsCount[4] / self.detectedSensorsCount[7]*3 > 0.6)
            print("Detected Right?(sensor6+7/total):",
                  self.detectedSensorsCount[6]+self.detectedSensorsCount[5] / 2*self.detectedSensorsCount[7])
            print("Detected Left?(sensor0+1/total):",
                  self.detectedSensorsCount[0]+self.detectedSensorsCount[1] / 2*self.detectedSensorsCount[7])
            print("------------------------------------")
            # ?-----------------------------------------------------------------
            if self.detectedSensorsCount[2] + self.detectedSensorsCount[3] + self.detectedSensorsCount[4] / self.detectedSensorsCount[7]*3 > 0.6:
                self.getVertex().update(self.direction, ["front"])
            self.state = "decide"
            return True

    def orient(self, dir):
        """Orients the robot in the given direction"""

        # ? ------------------------------LOGGING----------------------------
        print("------------------------------------")
        print(f"{bcolors.PURPLE}orient{bcolors.RESET}")
        print("direction ", dir)
        # print(self.measures.compass > DIRECTIONMAP[dir] + 5 and self.measures.compass < DIRECTIONMAP[dir ] + 89)
        # print(self.measures.compass > DIRECTIONMAP[dir] -175 and self.measures.compass < DIRECTIONMAP[dir] -91)
        # if self.measures.compass > DIRECTIONMAP[dir] + 5 and self.measures.compass < DIRECTIONMAP[dir ] + 89:
        #     print(f"\t{bcolors.GREEN}turning right{bcolors.RESET}")
        # elif self.measures.compass > DIRECTIONMAP[dir] -175 and self.measures.compass < DIRECTIONMAP[dir] -91:
        #     print(f"\t{bcolors.GREEN}turning right{bcolors.RESET}")
        # ?-----------------------------------------------------------------

        degrees = DIRECTIONMAP[dir]
        remaining = min(degrees-self.measures.compass, degrees -
                        self.measures.compass+360, degrees-self.measures.compass-360, key=abs)

        print(f"\t{bcolors.CYAN}remaining{bcolors.RESET} {remaining}")
        print("------------------------------------")

        if abs(remaining) <= 2:
            print("REMAINING <=2 TRUE")
            return True
        else:
            power = round(math.radians(remaining) -
                          (0.5 * self.lastoutR) + (0.5 * self.lastoutL), 2)

            # low max power to avoid overshooting by noise
            if abs(remaining) > 45:
                if power > 0.15:
                    power = 0.15
                elif power < -0.15:
                    power = -0.15
            else:
                if power > 0.07:
                    power = 0.07
                elif power < -0.07:
                    power = -0.07

            self.move(override=True, leftPower=-power, rightPower=power)
            print(f"\t{bcolors.CYAN}power{bcolors.RESET} {power}")
            return False

    def realOrientation(self):
        if (self.measures.compass <= 0 and self.measures.compass >= 45) or (self.measures.compass >= -180 and self.measures.compass <= -135):  # right
            return "right"
        elif (self.measures.compass <= -45 and self.measures.compass >= -135) or (self.measures.compass >= 135 and self.measures.compass <= 180):  # left
            return "left"
        elif (self.measures.compass <= 135 and self.measures.compass >= 45):  # up
            return "up"
        elif (self.measures.compass <= -45 and self.measures.compass >= -135):  # down
            return "down"
        else:
            return ""

    def wander(self):
        # ? ------------------------------LOGGING----------------------------
        print(f"{bcolors.PURPLE}Wander{bcolors.RESET}")
        print(f"\t{bcolors.CYAN}{self.x}{bcolors.RESET}")
        print(f"\t{bcolors.CYAN}{self.y}{bcolors.RESET}")
        print(f"\t{bcolors.GREEN}{self.initialx - self.measures.x}{bcolors.RESET}")
        print(f"\t{bcolors.GREEN}{self.initialy - self.measures.y}{bcolors.RESET}")

        # ?-----------------------------------------------------------------

        if (int(self.measures.lineSensor[5]) + int(self.measures.lineSensor[6])):
            if self.direction in {"right", "left"}:
                if self.x % 2 < 0.5 or self.x % 2 > 1.5:
                    self.state = "vertexDiscovery"

                else:
                    print(f"\t{bcolors.YELLOW}anti fuck up{bcolors.RESET}")

                    self.move("slightRight")
            else:
                if self.y % 2 < 0.5 or self.y % 2 > 1.5:
                    self.state = "vertexDiscovery"
                else:

                    print(f"\t{bcolors.YELLOW}anti fuck up{bcolors.RESET}")

                    self.move("slightRight")

        # turn slightly left if right edge detected
        elif (int(self.measures.lineSensor[0]) + int(self.measures.lineSensor[1])):
            if self.direction in {"right", "left"}:
                if self.x % 2 < 0.5 or self.x % 2 > 1.5:
                    self.state = "vertexDiscovery"
                else:

                    print(f"\t{bcolors.YELLOW}anti fuck up{bcolors.RESET}")

                    self.move("slightLeft")
            else:
                if self.y % 2 < 0.5 or self.y % 2 > 1.5:
                    self.state = "vertexDiscovery"
                else:
                    print(f"\t{bcolors.YELLOW}anti fuck up{bcolors.RESET}")

                    self.move("slightLeft")

        # go front if 3 middle sensors detect line
        elif (int(self.measures.lineSensor[3]) + int(self.measures.lineSensor[2]) + int(self.measures.lineSensor[4])) >= 1:
            self.move("front")

        elif self.lineSensorsZero():
            if self.direction != self.realOrientation():
                self.direction = self.realOrientation()
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
