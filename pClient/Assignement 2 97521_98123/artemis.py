import math
import sys
from croblink import *
from math import *
import xml.etree.ElementTree as ET
import itertools
import search
import c3path
import CreateMap
import FinalBeaconConnections


import pickle
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
    "slightLeft": (0.08, 0.12),
    "slightRight": (0.12, 0.08),
    "stop": (0, 0),
    "slowbackward": (-0.06, -0.06)
    
}
SLOWMOTORSTRENGTHMAP = {
    "front": (0.03, 0.03),
    "frontslow": (0.01, 0.01),
    "backward": (-0.03, -0.03),
    "left": (-0.03, 0.03),
    "right": (0.03, -0.03),
    "slightLeft": (0.01, 0.03),
    "slightRight": (0.03, 0.01),
    "stop": (0, 0),
    "slowbackward": (-0.01, -0.01)
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

RIGHTHANDRULE = {
    "right": ["down", "right", "up", "left"],
    "up": ["right", "up", "left", "down"],
    "left": ["up", "left", "down", "right"],
    "down": ["left", "down", "right", "up"]
}
class Beacon():
    """ A beacon in the map """    
    def __init__(self,x=-1,y=-1,vertexList=[],id=-1,direction = None):
        self.x = x
        self.y = y
        self.id = id
        self.direction = direction
        if (x,y) in vertexList:
            self.isVertex = True
            self.vertex = vertexList[vertexList.index((x,y))]
        else:
            self.isVertex = False
            self.vertex = None
        self.connects = {}
        
    def update(self, vertexList: list) -> None:
     
        for vertex in vertexList:
            if vertex == [self.x, self.y]:
                self.isVertex = True
                self.vertex = vertexList[vertexList.index((self.x,self.y))]

            
    def __repr__(self) -> str:
        return f"Beacon at ({self.x},{self.y}, id: {self.id}, isVertex: {self.isVertex}, vertex: {self.vertex}),  connects: {self.connects},  direction: {self.direction}\n"
    
    def __eq__(self, o) -> bool:
        return (self.x, self.y) == (o.x, o.y)
    
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

    def __init__(self, x=-1, y=-1, isDeadEnd=False):
        self.x = x
        self.y = y
        # 0 unknown; 1 exists but unexplred ; 2 -Exists and explored ;
        self.edges = {"up": 0,
                      "down": 0,
                      "left": 0,
                      "right": 0}
        self.connects = {}
        self.id = next(Vertex.id_iter)
        self.isDeadEnd = isDeadEnd

    def __repr__(self) -> str:
        return f"Vertex {self.id} at ({self.x},{self.y}), edges: {self.edges}, connects: {self.connects} \n"

    def __eq__(self, o: list) -> bool:
        # get coordinates and check if equal to list of coordinates
        if type(o) == Vertex:
            return (self.x, self.y) == (o.x, o.y)
        else:
            return (self.x, self.y) == (o[0], o[1])

    def update(self, robot_dir,turns=[], visited=False, connects = None, vlist = [], force = False):
        """updates the possible turns of this vertex
        #! in the future, update the connects as well
        #! also estamos a deixar dar overwrite sempre que passa por um vertice, nao sei se e bom

        Args:
            robot_dir (str): the direction the robot is facing
            turns (dict): the turns list

        Returns:
            None
        """
        if visited:
            self.edges[INVERSEDIRECTIONMAP[robot_dir]] = 2
        
        if turns:
            for turn in turns:
                edge = TURNSMAP[robot_dir][turn]
                if force:
                    self.edges[edge] = 1
                else:
                    if self.edges[edge] == 0:
                        self.edges[edge] = 1
                        
        if connects is not None:
            self.connects[INVERSEDIRECTIONMAP[robot_dir]] = connects.id
            connects.connects[robot_dir] = self.id
        


        return
    def updateEdges(self, edges):
        for edge in edges:
            self.edges[edge] = 1
        # self.edges = {}
        
    def getDirections(self):
        """returns the possible turns from this vertex

        Args:
            robot_dir (str): the direction the robot is facing

        Returns:
            list: the possible turns
        """
        return [
            direction 
            for direction in self.edges
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
        self.state = "initial"
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

        self.vertexList= []
        
        self.pathfindingMovements = []
        self.finishing = False
        self.prevVertex = None
        
        self.prevBeacon = -1
        self.beaconList = []
        
        self.detectedSensorsCount = [0, 0, 0, 0, 0, 0, 0, 0]

        self.initialLine = False
        
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
                elif self.state == "decide":
                    self.decide()
                elif self.state == "adjustForward":
                    self.adjustForward()
                elif self.state == "initial":
                    self.beginning()
                else:
                    self.wander()
                    
    def beginning(self):
        """the beginning state of the robot
        This function contains the logic of the robot when it is in the beginning state.
        It does a 360 to see the possible moves

        Args:
            None

        Returns:
            None
        """
        directions = ["right","up","left","down"]
        detectedDirections = []
        for dir in directions:
            detectedSensons = [0, 0, 0, 0, 0, 0, 0]
            
            while not self.orient(dir):
                pass

            self.readSensors()
            for idx, sensor in enumerate(self.measures.lineSensor):
                if sensor == "1":
                    detectedSensons[idx] += 1
                    
            self.readSensors()
            for idx,sensor in enumerate(self.measures.lineSensor):
                if sensor == "1":
                    detectedSensons[idx] += 1
                    
            if detectedSensons[3]+ detectedSensons[2]+detectedSensons[4] >= 2:
                detectedDirections.append(dir)

            
        if not detectedDirections:
            self.end()
        else:
            if detectedDirections == ["right","left"] or detectedDirections == ["up","down"]:
                chosenDirection = [
                    direction for direction in PRIORITY
                    if direction in detectedDirections
                ][0]

                while not self.orient(chosenDirection):
                    pass
                
                self.initialLine = True
                self.direction = chosenDirection
                    
                self.state= "wander"

            else:

                self.prevVertex = self.getVertex()
                self.prevVertex.updateEdges(detectedDirections)
                
                chosenDirection = [
                            direction for direction in PRIORITY
                            if direction in detectedDirections
                        ][0]

                while not self.orient(chosenDirection):
                    pass
                
                self.direction = chosenDirection
                self.state= "wander"
        
    def updateGPS(self, inLPower : float, inRPower : float, correction : bool = False) -> None:
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

        else:
            if self.direction == "right":
                self.x = self.lastx + (lin)
                y = self.lasty + (lin * sin(radians(self.measures.compass)))
                self.y = roundPowerOf2(y)
            elif self.direction == "left":
                self.x = self.lastx - (lin)
                y = self.lasty + (lin * sin(radians(self.measures.compass)))
                self.y = roundPowerOf2(y)
            elif self.direction == "up":
                self.y = self.lasty + (lin)
                x = self.lastx + (lin * cos(radians(self.measures.compass)))
                self.x = roundPowerOf2(x)
            elif self.direction == "down":
                self.y = self.lasty - (lin)
                x = self.lastx + (lin * cos(radians(self.measures.compass)))
                self.x = roundPowerOf2(x)

        self.lastoutL = outL
        self.lastoutR = outR
        self.lastx = self.x
        self.lasty = self.y
        return

    def nextDirection(self, turn : str) -> str:
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


    def findPath(self, currVertex : Vertex, targetVertex : int = None) -> None:
        """find the path to the goal

        Args:
            None

        Returns:
            None
        """
        id = currVertex.id
        if targetVertex == None:

            unexploredvertexes = [ 
                    vertex 
                    for vertex in self.vertexList 
                    if any(edge == 1 for edge in vertex.edges.values()) 
                    and vertex.id != id
            ]

            directionqueue = min ( 
                map ( lambda vertex: search.directionqueue(self.vertexList, id, vertex.id), unexploredvertexes ),
                key = lambda x: len(x),
                default=[]
            )

            self.pathfindingMovements = directionqueue
        else:
            directionqueue = search.directionqueue(self.vertexList, id, targetVertex)
            self.pathfindingMovements = directionqueue
    
    def getVertex(self, id : int = None) -> Vertex:
        """create a vertex in the current position of the robot or return the existing one

        Args:
            None

        Returns:
            Vertex: the vertex created or updated
        """
        roundedcoords = (roundPowerOf2(self.x), roundPowerOf2(self.y))

        if id:
            
            return [
                vertex 
                for vertex in self.vertexList 
                if vertex.id == id
            ][0]
        else:
        # go read __eq__ method in Vertex class
            vertex = [
                vertex 
                for vertex in self.vertexList 
                if vertex == roundedcoords
            ]
            if vertex:
                vertex = vertex[0]
                #!neste momento so curvas, dps tem de ter connects

            else:
                vertex = Vertex(*roundedcoords)
                #!do this now? or after turning?
                self.vertexList.append(vertex)
            return vertex

    def move(self, direction : str = "", override : bool = False, leftPower: float = 0, rightPower: float = 0) -> None:
        if not override:
            speed=True
            #! xaneco nao esquecer self.x % 2 < 0.1 REVER
            if self.direction == "right" and((self.x % 2) > 1.4):
                speed=False
            elif self.direction == "left" and( self.x % 2 < 0.6 ):
                speed=False
            elif self.direction == "up" and( self.y % 2 > 1.4):
                speed=False
            elif self.direction == "down" and( self.y % 2 < 0.6):
                speed=False
            if speed:
                self.updateGPS(*MOTORSTRENGTHMAP[direction])
                self.driveMotors(*MOTORSTRENGTHMAP[direction])
            else:
                self.updateGPS(*SLOWMOTORSTRENGTHMAP[direction])
                self.driveMotors(*SLOWMOTORSTRENGTHMAP[direction])
        else:
            self.driveMotors(leftPower, rightPower)
            self.updateGPS(leftPower, rightPower)
        self.readSensors()

    def vertexDiscovery(self):
        """checks if a vertex exists in front of the robot and its turns"""
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
                # ?-----------------------------------------------------------------
                self.move("stop")

            elif i == 1:
                rightCounter["lado"] += int(self.measures.lineSensor[5])
                rightCounter["ponta"] += int(self.measures.lineSensor[6])

                leftCounter["ponta"] += int(self.measures.lineSensor[0])
                leftCounter["lado"] += int(self.measures.lineSensor[1])
                # ?------------------------------LOGGING----------------------------
                if sum(rightCounter.values()) > 2 and rightCounter["ponta"] >= 1:
                    turns.append("right")
                if sum(leftCounter.values()) > 2 and leftCounter["ponta"] >= 1:
                    turns.append("left")

                if len(turns) == 2:
                    self.getVertex().update(self.direction, turns=turns)
                    self.state = "decide"
                    return

                
                if self.lineSensorsZero():
                    self.move("backward")
                else:
                    self.move("frontslow")

                rightCounter["lado"] += int(self.measures.lineSensor[5])
                rightCounter["ponta"] += int(self.measures.lineSensor[6])

                leftCounter["ponta"] += int(self.measures.lineSensor[0])
                leftCounter["lado"] += int(self.measures.lineSensor[1])

                if sum(rightCounter.values()) > 2 and rightCounter["ponta"] >= 1:
                    turns.append("right")
                if sum(leftCounter.values()) > 2 and leftCounter["ponta"] >= 1:
                    turns.append("left")

                if turns:
                    self.getVertex().update(self.direction, turns=turns)
                    self.state = "decide"
                    return

        self.state = "wander"
        
    def decide(self):
        """decides which way to go"""
        vertex = self.getVertex()
        availableTurns = None

        # first position the robot in the center of the vertex
        self.detectedSensorsCount = [0, 0, 0, 0, 0, 0, 0, 0] 
        while not self.adjustForward(): #!eventually reqwrite this
            pass

        if self.prevVertex:
            vertex.update( self.direction, visited=True, connects=(self.prevVertex) )    
            self.prevVertex.update( INVERSEDIRECTIONMAP[self.direction], connects=(vertex),visited=True)
        else:
            vertex.update( self.direction, visited=True )
            
        if self.pathfindingMovements:
            chosenDirection = self.pathfindingMovements.pop(0)
        else:
            if self.initialLine:
                self.initialLine = False
                vertex = self.getVertex()
                vertex.update(self.direction, turns=["back"], force=True)
            
            availableTurns = vertex.getDirections()
            # priority is down, right, up, left
            if availableTurns:
                chosenDirection = [
                    direction for direction in PRIORITY
                    if direction in availableTurns
                ][0]

            else:

                                    
                self.findPath(vertex)
                if self.pathfindingMovements:
                    chosenDirection = self.pathfindingMovements.pop(0)
                else:
                    #!try fix corrupt vertexlist
                    for vertex_iter in self.vertexList:
                        if vertex_iter.id in vertex_iter.connects.values():
                            
                            vertex_iter.connects = {k : v for k, v in vertex_iter.connects.items() if v != vertex_iter.id}
                            for vertex2 in self.vertexList:
                                for connect in vertex2.connects:
                                    if vertex2.connects[connect] == vertex_iter.id:
                                        vertex_iter.connects[INVERSEDIRECTIONMAP[connect]] = vertex2.id
                    self.findPath(vertex)
                    if self.pathfindingMovements:
                        chosenDirection = self.pathfindingMovements.pop(0)
                    else:
                    
                        vertexend = self.getVertex()
                        if vertexend.id == 0:
                            if vertexend.x == 0:
                                if vertexend.y > 0:
                                    chosenDirection = "down"
                                else:
                                    chosenDirection = "up"
                            elif vertexend.y == 0:
                                if vertexend.x > 0:
                                    chosenDirection = "left"
                                else:
                                    chosenDirection = "right"
                        else:
                            self.findPath(vertex, targetVertex=0)
                            self.finishing = True

                            #save vertex list to pickle

                            
                            # if self.pathfindingMovements:
                            chosenDirection = self.pathfindingMovements.pop(0)

            
        while not self.orient(chosenDirection): #!eventually reqwrite this
            pass
        

        

        self.direction = chosenDirection
        self.prevVertex = vertex      
        self.state = "wander"
                
    def end(self):
        """ends the program"""

        self.vertexList = FinalBeaconConnections.InsertBeaconsInVertexList(self.vertexList, self.beaconList)

        CreateMap.generate(self.vertexList,self.beaconList)
        c3path.Generate_path_file(self.vertexList,self.beaconList)
        self.finish()
        sys.exit()
    
    # ------------------------------------
    def adjustForward(self):
        """
           Positions the robot in the center of the vertex using our GPS (self.x,self.y)
           It records all the sensors captured in self.detectedSensorsCount

        return: Boolean True if the robot is in the center of the vertex else False

        """

        for i in range(7):
            self.detectedSensorsCount[i] += int(self.measures.lineSensor[i])
        self.detectedSensorsCount[7] += 1

        rem_distance = 0

        if self.direction == "right":
            rem_distance = roundPowerOf2(self.x) - self.x
        elif self.direction == "left":
            rem_distance = self.x - roundPowerOf2(self.x)
        elif self.direction == "up":
            rem_distance =  roundPowerOf2(self.y) - self.y
        elif self.direction == "down":
            rem_distance = self.y -roundPowerOf2(self.y)
        
        if rem_distance > 0:
            if rem_distance > 0.1:
                self.move(override=True, leftPower=0.05, rightPower=0.05)
            else:
                self.move(override=True, leftPower=0.01, rightPower=0.01)
            return False
        else:

            if not self.finishing:
                if (self.detectedSensorsCount[2] + self.detectedSensorsCount[3] + self.detectedSensorsCount[4]) / (self.detectedSensorsCount[7]*3 )> 0.5:
                    self.getVertex().update(self.direction, turns=["front"])
            self.state = "decide"
            return True

    def orient(self, dir:str) -> bool:
        """Orients the robot in the given direction"""

        degrees = DIRECTIONMAP[dir]
        remaining = min(degrees-self.measures.compass, degrees -
                        self.measures.compass+360, degrees-self.measures.compass-360, key=abs)


        if abs(remaining) <= 2:
            return True
        else:
            power = round(math.radians(remaining) -
                          (0.5 * self.lastoutR) + (0.5 * self.lastoutL), 2)

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

        if self.measures.ground >= 0:
            beacon = (Beacon(x = roundPowerOf2(self.x),y =  roundPowerOf2(self.y), vertexList = self.vertexList ,id= self.measures.ground,direction=self.direction))
            if not beacon in self.beaconList:
            
                self.beaconList.append(beacon)

        if roundPowerOf2(self.x) == 0 and roundPowerOf2(self.y) == 0:
            if self.finishing:
                while not self.adjustForward():
                    pass
                self.end()
            
        if (int(self.measures.lineSensor[6])):
            if (
                (self.direction == "right" and (self.x+100) % 2 >= 1.3)
                or (self.direction == "left" and (self.x+100) % 2 <= 0.7)
                or (self.direction == "up" and (self.y+100) % 2 >= 1.3)
                or (self.direction == "down" and (self.y+100) % 2 <= 0.7)
            ):
                self.state = "vertexDiscovery"
            else:
                self.move("slightRight")
                    
        # turn slightly left if right edge detected
        elif (int(self.measures.lineSensor[0])):
            if (
                (self.direction == "right" and (self.x+100) % 2 >= 1.3)
                or (self.direction == "left" and (self.x+100) % 2 <= 0.7)
                or (self.direction == "up" and (self.y+100) % 2 >= 1.3)
                or (self.direction == "down" and (self.y+100) % 2 <= 0.7)
            ):
                self.state = "vertexDiscovery"
            else:
                self.move("slightLeft")


        elif int(self.measures.lineSensor[1]):
            self.move("slightLeft")
        elif int(self.measures.lineSensor[5]):
            self.move("slightRight")

        # go front if 3 middle sensors detect line
        elif (int(self.measures.lineSensor[3]) + int(self.measures.lineSensor[2]) + int(self.measures.lineSensor[4])) >= 3:
            self.move("front")
            
        elif self.lineSensorsZero():
            self.state = "decide"
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
    elif (sys.argv[i] == "--file" or sys.argv[i] == "-f") and i != len(sys.argv) - 1:
        print()
    else:
        print("Unkown argument", sys.argv[i])
        quit()

if __name__ == '__main__':
    rob = MyRob(rob_name, pos, [0.0, 60.0, -60.0, 180.0], host)
    if mapc is not None:
        rob.setMap(mapc.labMap)
        rob.printMap()

    rob.run()
