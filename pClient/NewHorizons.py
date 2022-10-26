import sys

import math
from croblink import *
from math import *
import xml.etree.ElementTree as ET

import itertools

import CreateMap
import search
CELLROWS=7
CELLCOLS=14

#GLOBAL VARS ########
once =0
distance = 5


motorStrengthMap = {
    "front": (0.12,0.12),
    "frontslow": (0.05, 0.05),
    "backward": (-0.05,-0.05),
    "left": (-0.15,0.15),
    "right": (0.15,-0.15),
    "slightLeft": (0.08,0.12),
    "slightRight": (0.12,0.08),
    "stop": (0,0)
}

directionMap = {
    "right": 0,
    "up": 90,
    "left": -180,
    "down": -90
}

inversedirectionMap = {
    "right": "left",
    "up": "down",
    "left": "right",
    "down": "up"
}
############

#round to nearest multiple of 2
def roundcoord(x):
    """round to nearest multiple of 2

    Args:
        x (float): the number to round

    Returns:
        int: the rounded number
    """
    return int(round(x / 2.0)) * 2

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
        self.edges = {"up" : 0, 
                 "down" : 0, 
                 "left" : 0, 
                 "right" : 0}
        self.connects = {}
        self.id = next(Vertex.id_iter)
        self.isDeadEnd = False
    def __repr__(self) -> str:
        return f"Vertex {self.id} at ({self.x},{self.y}), edges: {self.edges}, connects: {self.connects} \n"

class MyRob(CRobLinkAngs):
    """The robot class

    Attributes:
        rob_name (str): the name of the robot
        detectedsensors (list): line sensor readings when the robot detected a vertex
        previouspowerLR (tuple): the previous power sent to the left and right motors
        turnpoint (list): the point where the robot will turn
        currentVertex (Vertex): the vertex the robot is currently at
        prevVertex (Vertex): the previous vertex the robot was at
        targetVertex (Vertex): the vertex the robot is trying to reach
        queue (list): the queue of directions to follow to reach the target vertex
        direction (str): the direction the robot is facing
        state (str): the state of the robot
        vertexList (list): the list of vertices the robot has visited
        initialPos (list): the initial position of the robot
    """	
    def __init__(self, rob_name, rob_id, angles, host):
        CRobLinkAngs.__init__(self, rob_name, rob_id, angles, host)
        
        #!!!!---------------
        self.rob_name = "New Horizons"
        self.detectedsensors = []
        self.previouspowerLR = (0,0)
        self.turnpoint = None
        self.currentVertex = None
        self.prevVertex = Vertex(0,0)
        self.targetVertex = None
        self.queue = []
        self.direction = "right"
        self.state = 'stop'
        self.vertexList=[self.prevVertex]
        self.initialPos = [0,0]
        

    def gps(self, dir):
        """offset gps with initial position

        Args:
            dir (str): x or y
        
        Returns:
            int: the position of the robot offset by the initial position

        """
        return round(self.measures.x - self.initialPos[0],2) if dir == "x" else round(self.measures.y - self.initialPos[1],2)
    

    def move(self, direction):
        """move the robot in a direction

        Args:
            direction (str): the direction to move (front, backward, left, right, slightLeft, slightRight)
        
        Returns:
            None
            
        """

        self.driveMotors(motorStrengthMap[direction][0], motorStrengthMap[direction][1])
    
    def setMap(self, labMap):
        """set the map

        Args:
            labMap (_type_): the labmap to change to
        """        
        self.labMap = labMap

    def printMap(self):
        """
        print the map
        """        
        for l in reversed(self.labMap):
            print(''.join([str(l) for l in l]))

    def run(self):
        """the main loop of the robot
        This function contains the main logic of the robot, represented by its state.
        it has 4 new states: "orient", "vertexDiscovery", "pathfinding" and "decision"
        
        orient: the robot is orienting itself to the right direction
        vertexDiscovery: the robot is discovering what vertex it is at
        pathfinding: the robot is deciding what is the next target vertex and what path to take
        decision: the robot is deciding what direction to move next

        Args:
            None

        Returns:
            None
        """
        if self.status != 0:
            print("Connection refused or error")
            quit()

        
        stopped_state = 'run'
        self.readSensors()
        self.initialPos = [self.measures.x, self.measures.y]
        print("Initial position: ", self.initialPos)
        
        
        while True:
            self.readSensors()

            if self.measures.endLed:
                print(self.rob_name + " exiting")
                quit()

            if self.state == 'stop' and self.measures.start:
                self.state = stopped_state

            if self.state != 'stop' and self.measures.stop:
                stopped_state = self.state
                self.state = 'stop'
            
            if self.state == 'run':
                if self.measures.visitingLed==True:
                    self.state='wait'
                if self.measures.ground==0:
                    self.setVisitingLed(True)
                self.wander()
                
            elif self.state == "orient":
                self.compensate = 0
                if self.orient(self.direction) == 1:
                    self.state = "return"
                
            elif self.state == "vertexDiscovery":
                self.vertexDiscovery()
            elif self.state == "pathfinding":
                self.pathfinding()
            
            elif self.state=='wait':
                self.setReturningLed(True)
                if self.measures.visitingLed==True:
                    self.setVisitingLed(False)
                if self.measures.returningLed==True:
                    self.state='return'
                self.driveMotors(0.0,0.0)
            elif self.state == 'decision':
                self.Decide()
            elif self.state=='return':
                if self.measures.visitingLed==True:
                    self.setVisitingLed(False)
                if self.measures.returningLed==True:
                    self.setReturningLed(False)
                self.wander()
    

    def vertexDiscovery(self):
        """Function to discover what vertex the robot is at

        It first orients the robot to the right direction, then it checks if the robot is at a vertex.
        If it is, it changes the state to "decision" and sets internal variables accordingly.

        Args:
            None

        Returns:
            None
        """    
        #*used in adjustForward
        global prevDistance
        prevDistance = 5
        #-----------------------------
        isoriented = self.orient(self.direction)
        if isoriented == 1:

            #check if the vertex already exists, if it doesn´t, detect it and create it, if None is returned must have been a mistake
            vertex = self.checkNearVertex()
            if vertex:
                self.state = "decision"
                self.currentVertex = vertex
                self.turnpoint= [(vertex.x), (vertex.y)] 
                self.detectedsensors = []
            else :# IF NO VERTEX IS DETECTED
                #a mistake was made
                self.state = "return"

    def checkNearVertex(self):
        """ Function to check if the robot is near a previously discovered vertex

        It check the already created vertexes and if near one it returns it.
        If no near vertex is found detectVertex() is called to create a new vertex. 

        Args:
            None
        Returns:
            vertex: vertex object
        """
        #if any vertice is within 0.5m of the current position, return that vertex
        for vertex in self.vertexList:

            if vertex.x == round(self.gps("x"))and vertex.y == round(self.gps("y")):
                vertex.edges[inversedirectionMap[self.direction]] = 2
                return vertex
        
        #if vertex is not found nearby, must be a new one
        return self.detectVertex()
            
    def detectVertex(self):
        """
        Function that creates a new vertex rounded to the nearest power of 2, reading the robot sensors and putting the correct values in its edges.
        If inside a Beacon no vertex will be created because it wal already created in another function, it will only update it with the correct values.
        If the seasons don't detect anything, it means the robot is near a dead end and it will create a vertex signalizing that he is a dead end.

        Returns: vertex object
        """
        #print("detectVertex")
        global inversedirectionMap
        #!using detect sensors
        if self.detectedsensors[0] == "1" or self.detectedsensors[6] == "1":
            vertex = Vertex()

            vertex.x = roundcoord(self.gps("x"))
            vertex.y = roundcoord(self.gps("y"))
            
            if self.direction == "right":
                if self.detectedsensors[0] == "1":
                    vertex.edges["up"] = 1
                if self.detectedsensors[6] == "1":
                    vertex.edges["down"] = 1
                
                #explored we just came from there
                vertex.edges["left"] = 2
                
            elif self.direction == "left":
                if self.detectedsensors[0] == "1":
                    vertex.edges["down"] = 1    
                if self.detectedsensors[6] == "1":
                    vertex.edges["up"] = 1
                
                #explored we just came from there    
                vertex.edges["right"] = 2
    
            
            elif self.direction == "up":
                
                if self.detectedsensors[0] == "1":
                    vertex.edges["left"] = 1
                if self.detectedsensors[6] == "1":
                    vertex.edges["right"] = 1
                    
                #explored we just came from there
                vertex.edges["down"] = 2
            
            elif self.direction == "down":
                if self.detectedsensors[0] == "1":
                    vertex.edges["right"] = 1
                if self.detectedsensors[6] == "1":
                    vertex.edges["left"] = 1
                
                #explored we just came from there         
                vertex.edges["up"] = 2
                
            self.vertexList.append(vertex)

            
            return vertex
        else:
            vertex= Vertex()
            vertex.x = roundcoord(self.gps("x"))
            vertex.y = roundcoord(self.gps("y"))
            vertex.edges= {direction:0 for direction in directionMap}
            print(vertex.edges)
            vertex.edges[inversedirectionMap[self.direction]] = 2
            vertex.isDeadEnd = True
            self.vertexList.append(vertex)
        return vertex
    
    def Decide(self):
        """
        Service used to decide the next direction to take when nearing a vertex and turning the robot in that direction.
        """
        global once
        global inversedirectionMap
        bol = self.adjustForward()
        once = 1
        if bol == 1 :
            once = 0
            self.state = "orient"
            print(f"Decide {self.currentVertex.id}: {self.currentVertex.edges} ")
            
            decision = ""
    
            if len(self.queue) > 0:
                decision = self.queue.pop(0)
                print("queue", self.queue)
                self.direction = decision
                self.prevVertex = self.currentVertex
                self.currentVertex = None
                return
            
            else:
                self.targetVertex = None
                if self.currentVertex.edges["down"] == 1:
                    self.currentVertex.edges["down"] = 2
                    decision="down"
                
                elif self.currentVertex.edges["right"]== 1:
                    self.currentVertex.edges["right"] = 2
                    decision="right"
                
                
                elif self.currentVertex.edges["up"]== 1:
                    self.currentVertex.edges["up"] = 2
                    decision="up"

                elif self.currentVertex.edges["left"] == 1:
                    self.currentVertex.edges["left"] = 2
                    decision="left"

                else:
                    self.state="pathfinding"
                    
                    self.prevVertex.connects[self.direction] = self.currentVertex.id
                    self.currentVertex.connects[inversedirectionMap[self.direction]] = self.prevVertex.id
                    
                    if self.currentVertex not in self.vertexList:
                        self.vertexList.append(self.currentVertex)
                    else:
                        self.vertexList[self.vertexList.index(self.currentVertex)] = self.currentVertex
                
                    self.move("stop")
                    return
            
            #append current vertex to self.vertexlist else update it  
            self.prevVertex.connects[self.direction] = self.currentVertex.id
            self.currentVertex.connects[inversedirectionMap[self.direction]] = self.prevVertex.id

            
            if self.currentVertex not in self.vertexList:
                self.vertexList.append(self.currentVertex)
            else:
                self.vertexList[self.vertexList.index(self.currentVertex)] = self.currentVertex
                

            self.direction = decision
            self.prevVertex = self.currentVertex
            self.currentVertex = None

    
    def pathfinding(self):
        """
        when the robot is near a vertex with every edge explored, this function is called to search a path that leads to a vertex that has unexplored edges.
        If there isn't a unexplored edge, the robot stops moving,ends and generates the optimal path that connects all beacons.
        """
        #!find a vertex that has not been explored
        global inversedirectionMap
        shortestpath = 100
        if self.targetVertex == None:

            if self.currentVertex.isDeadEnd:
                print("dead end")
                self.targetVertex = self.prevVertex
                
                #!remove this after prints are gone
                queue=[inversedirectionMap[self.direction]]
                
                
                self.queue=[inversedirectionMap[self.direction]]
            else:
                for vertex in self.vertexList:
                    if 1 in vertex.edges.values():
                        self.targetVertex = vertex
                        queue = search.directionqueue(self.vertexList, self.currentVertex.id, self.targetVertex.id)
                        if len(queue) < shortestpath:
                            shortestpath = len(queue)
                            self.queue = queue

        if len(self.queue)>0:
            print(f"Pathfinding to {self.targetVertex.id}, Movements : ")  
            print(self.queue)      
            self.direction = self.queue.pop(0)
            self.state="orient"
        else:
            print("Im done")
            self.prevVertex = self.currentVertex
            self.currentVertex = None
            
            CreateMap.generate(self.vertexList)
            
            self.finish()
        self.prevVertex = self.currentVertex
        self.currentVertex = None
        
    def adjustForward(self):
        """
            Function that adjust the robot position to be near the exact verter of a vertex.

            Return: integer (0 - unfinished or 1 - finished)
        """
        global distance
        global once
        
        if once==0:
            distance = round(math.sqrt((self.turnpoint[0] - self.gps("x"))**2 + (self.turnpoint[1] - self.gps("y"))**2),2)
        if distance >=0.1:
            distance = round(math.sqrt((self.turnpoint[0] - self.gps("x"))**2 + (self.turnpoint[1] - self.gps("y"))**2),2)
        if distance < 0.05:
            self.readSensors()
            #check if has path forward of the vertex, update the vertex 
            if (self.measures.lineSensor[3] == "1" or self.measures.lineSensor[4] == "1" or self.measures.lineSensor[2] == "1"):
                self.currentVertex.edges[self.direction] = 1 if self.currentVertex.edges[self.direction] == 0 else self.currentVertex.edges[self.direction]

            return 1
        
        walk = distance
        if once == 0:
            walk = 0.15
        else:
            if distance > 0.1:
                walk = 0.05
            else:
                walk = 0.01


        distance = distance - walk

        if distance <=0:
            return 1
        self.driveMotors(walk,walk)
        return 0
    def orient(self, direction):
        """
            Function used to turn the robot to the desired direction.

            Returns integer (0-unfinished or 1-finished)
        """
        global directionMap
        degrees = directionMap[direction]
        #align to this number
        
        
        #angle difference between target and now
        remaining = min(degrees-self.measures.compass, degrees-self.measures.compass+360, degrees-self.measures.compass-360, key=abs)
        
        #acceptable in this range
        if abs(remaining) <= 1:
            self.move("frontslow")
            return 1
        
        #calculate power to give to motors, we'll give power to one motor and the symmetric to the other, depending on the angle
        power = round(math.radians(remaining) -  (0.5 * self.previouspowerLR[1]) + (0.5 * self.previouspowerLR[0]), 2)
        
        #low max power to avoid overshooting by noise
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
        
        self.previouspowerLR = (-power, power)
        self.driveMotors(-power, power)
        
        return 0


    
    def wander(self):
        """
            Function used in the return state that handles the default movement of the robot ad well as handling beacons and altering states.
        """
        global inversedirectionMap
            
        #check if collision against wall
        center_id = 0
        left_id   = 1
        right_id  = 2
        back_id   = 3
        if    self.measures.irSensor[center_id] > 5.0\
           or self.measures.irSensor[left_id]   > 5.0\
           or self.measures.irSensor[right_id]  > 5.0\
           or self.measures.irSensor[back_id]   > 5.0:
            print('Rotate left')
            self.driveMotors(-0.1,+0.1)
        elif self.measures.irSensor[left_id]> 2.7:
            print('Rotate slowly right')
            self.driveMotors(0.1,0.0)
        elif self.measures.irSensor[right_id]> 2.7:
            print('Rotate slowly left')
            self.driveMotors(0.0,0.1)
        #########################################
        else:
            #locked in turn
            #if all 7 sensors report "1"
            #go back if no line detected
            #if one of these sensors is "1" check if we´re near vertex
            if((self.measures.lineSensor[:2].count("1") >= 2) or self.measures.lineSensor[5:7].count("1") >=2):
                #print("near vertex ", self.measures.lineSensor)
                self.state="vertexDiscovery"
                self.detectedsensors = self.measures.lineSensor
             
                self.move("stop")
           
        
            elif(self.measures.lineSensor[5]=="1"):
                self.move("slightRight")

            #turn slightly left if right edge detected
            elif(self.measures.lineSensor[1]=="1"):
                self.move("slightLeft")
                
            #go front if 3 middle sensors detect line
            elif (self.measures.lineSensor[3]=="1") :
                self.move("front")
                
            elif self.measures.lineSensor == ["0","0","0","0","0","0","0"]:
                #print("near vertex ", self.measures.lineSensor)
            
                self.state="vertexDiscovery"
                self.detectedsensors = self.measures.lineSensor
                self.move("stop")
            
            else:
                self.move("front")
class Map():
    def __init__(self, filename):
        tree = ET.parse(filename)
        root = tree.getroot()
        
        self.labMap = [[' '] * (CELLCOLS*2-1) for i in range(CELLROWS*2-1) ]
        i=1
        for child in root.iter('Row'):
           line=child.attrib['Pattern']
           row =int(child.attrib['Pos'])
           if row % 2 == 0:  # this line defines vertical lines
               for c in range(len(line)):
                   if (c+1) % 3 == 0:
                       if line[c] == '|':
                           self.labMap[row][(c+1)//3*2-1]='|'
                       else:
                           None
           else:  # this line defines horizontal lines
               for c in range(len(line)):
                   if c % 3 == 0:
                       if line[c] == '-':
                           self.labMap[row][c//3*2]='-'
                       else:
                           None
               
           i=i+1


rob_name = "pClient1"
host = "localhost"
pos = 1
mapc = None

for i in range(1, len(sys.argv),2):
    if (sys.argv[i] == "--host" or sys.argv[i] == "-h") and i != len(sys.argv) - 1:
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
    rob=MyRob(rob_name,pos,[0.0,60.0,-60.0,180.0],host)
    if mapc != None:
        rob.setMap(mapc.labMap)
        rob.printMap()
    
    rob.run()