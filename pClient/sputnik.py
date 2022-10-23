from operator import index
import sys
import math
from croblink import *
from math import *
import xml.etree.ElementTree as ET
from pprint import pprint
import itertools
from collections import Counter
import CreateMap
import pickle
import search
CELLROWS=7
CELLCOLS=14

#GLOBAL VARS ########
determined_vertex = 0
aligning = True
count=0
prevDistance=5
once =0
distance = 5

corrected = 1
############

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

lastdecision = "stop"


#round to nearest multiple of 2
def roundcoord(x):
    return int(round(x / 2.0)) * 2

class Vertex():
    id_iter = itertools.count()
    def __init__(self, x=-1, y=-1):
        self.x = x
        self.y = y
        # 0 unknown; 1 exists but unexplred ; 2 -Exists and explored ;
        self.edges = {"up" : 0, 
                 "down" : 0, 
                 "left" : 0, 
                 "right" : 0}
        self.connects = {}
        self.id = next(Vertex.id_iter)
        self.isDeadEnd = False
        self.beacon = -1

    def __repr__(self) -> str:
        return f"Vertex {self.id} at ({self.x},{self.y}), edges: {self.edges}, connects: {self.connects} \n"


class MyRob(CRobLinkAngs):
    def __init__(self, rob_name, rob_id, angles, host):
        CRobLinkAngs.__init__(self, rob_name, rob_id, angles, host)
        
        #!!!!---------------
        self.rob_name = "Sputnik"
        self.detectedsensors = []
        self.previouspowerLR = (0,0)
        self.turnpoint = None
        self.currentVertex = None
        
        self.targetVertex = None
        self.queue = []
        
        self.direction = "right"
        self.state = 'stop'

        self.prevVertex = Vertex(0,0)
        self.prevVertex.beacon = 0
        self.vertexList=[self.prevVertex]
        self.initialPos = [0,0]

        self.inBeacon = -1

    #offset gps with initialpos
    def gps(self, dir):
        return self.measures.x - self.initialPos[0] if dir == "x" else self.measures.y - self.initialPos[1]
    
    def realposition(self):
    #   return [ self.gps("x") + (0.5 * math.cos(math.radians(self.measures.compass))), self.gps("y") + (0.5 * math.sin(math.radians(self.measures.compass)))]
        return [ roundcoord(self.gps("x")), roundcoord(self.gps("y"))]
    
    def move(self, direction, compensate = None):
        global lastdecision
        self.driveMotors(motorStrengthMap[direction][0], motorStrengthMap[direction][1])
    
    # In this map the center of cell (i,j), (i in 0..6, j in 0..13) is mapped to labMap[i*2][j*2].
    # to know if there is a wall on top of cell(i,j) (i in 0..5), check if the value of labMap[i*2+1][j*2] is space or not
    def setMap(self, labMap):
        self.labMap = labMap

    def printMap(self):
        for l in reversed(self.labMap):
            print(''.join([str(l) for l in l]))

    def run(self):
        if self.status != 0:
            print("Connection refused or error")
            quit()

        
        stopped_state = 'run'
        self.readSensors()
        self.initialPos = [self.measures.x, self.measures.y]
        print("Initial position: ", self.initialPos)
        
        
        while True:
            self.readSensors()
            self.inBeacon =  self.measures.ground

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
        global prevDistance
        prevDistance = 5
        #-----------------------------
        #if it isnt oriented, it will orient itself each call as the state isn´t changed
        isoriented = self.orient(self.direction)
        if isoriented == 1:

            #check if the vertex already exists, if it doesn´t, detect it and create it, if None is returned must have been a mistake
            vertex = self.checkNearVertex()
            if vertex:
                print("MOTHERFUCKING BEACON", vertex) if vertex.beacon >= 0 else None
                print(f"CURRENTE VERTEX {self.currentVertex}")
                self.state = "decision"
                #!shenanigans for beacons in straight line currentvertex should always be None unless it was a straight line beacon
                if self.currentVertex and self.currentVertex.beacon >= 0 and not vertex.beacon>=0:
                    # print("straing line currentVertex",self.currentVertex)
                    # print("stright line beacon",self.currentVertex.beacon)
                    print("previous vertex was straight line beacon")
                    self.prevVertex = self.currentVertex
                    
                self.currentVertex = vertex
                
                #self.turnpoint= [self.measures.x + 0.438 * math.cos(math.radians(self.measures.compass)), self.measures.y + 0.438 * math.sin(math.radians(self.measures.compass))]
                self.turnpoint= [(vertex.x), (vertex.y)]
                
                self.detectedsensors = []
                
            else :# IF NO VERTEX IS DETECTED
                print("must have been the wind ", self.measures.lineSensor)
                self.state = "return"

    def checkNearVertex(self):
        for vertex in self.vertexList:
            if vertex.x == round(self.gps("x"))and vertex.y == round(self.gps("y")):
                
                if vertex.beacon>=0 and vertex.edges == {"up" : 0,"down" : 0, "left" : 0,"right" : 0}:

                    return self.detectVertex(Beacon=True,vertex=vertex)
                vertex.edges[inversedirectionMap[self.direction]] = 2         
                return vertex
        #if vertex is not found nearby, must be a new one
        return self.detectVertex()
            
    def detectVertex(self,Beacon=False,vertex=None):
        global inversedirectionMap
        #!using detect sensors
        if self.detectedsensors[0] == "1" or self.detectedsensors[6] == "1":
            if not Beacon:
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


            #vertex.beacon = self.inBeacon
            
            if not Beacon:
                self.vertexList.append(vertex)
            else:
                self.vertexList[self.vertexList.index(vertex)] = vertex
                

            return vertex

        else:
            if self.inBeacon <= 0:
                vertex= Vertex()
                vertex.x = roundcoord(self.gps("x"))
                vertex.y = roundcoord(self.gps("y"))
                vertex.edges= {direction:0 for direction in directionMap}
                
                vertex.edges[inversedirectionMap[self.direction]] = 2
                vertex.isDeadEnd = True

                vertex.beacon = self.inBeacon
                self.vertexList.append(vertex)
        return vertex
    
    def Decide(self):
        global once, corrected
        global inversedirectionMap
        bol = self.adjustForward()
        once = 1

        # if self.currentVertex.beacon >=0:
        #     self.prevVertex = self.currentVertex
            
        if bol == 1 :
            once = 0
            self.state = "orient"
            #print(f"Decide {self.currentVertex.id}: {self.currentVertex.edges} ")
            
            decision = ""


            if len(self.queue) > 0:

                if self.prevVertex.beacon >=0:
                    if all(direction in self.prevVertex.connects.keys() for direction in ["right","left"]) ^ all(direction in self.prevVertex.connects.keys() for direction in ["up","down"]):
                        #!remove extra direction in pathfinding 
                        print("Popped extra")
                        self.queue.pop(0)
                
                
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
        #!find a vertex that has not been explored
        global inversedirectionMap
        shortestpath = 100
        if self.targetVertex == None:

            if self.currentVertex.isDeadEnd:
                print("dead end")
                self.targetVertex = self.prevVertex
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
            print(f"Pathfinding to {self.targetVertex.id} {self.targetVertex.edges}")  
            print(self.queue)      
            self.direction = self.queue.pop(0)
            self.state="orient"
        else:
            print("Im done")
            self.prevVertex = self.currentVertex
            self.currentVertex = None
            with open("beaconvertex.pkl", "wb") as f:
                pickle.dump(self.vertexList, f, pickle.HIGHEST_PROTOCOL)
            CreateMap.generate(self.vertexList)
            print(f"BEACON {[vertex for vertex in self.vertexList if vertex.beacon >= 0]}")
            self.finish()
        self.prevVertex = self.currentVertex
        self.currentVertex = None
        
    def adjustForward(self):

        global distance
        global once

        if once==0:
            distance = math.sqrt((self.turnpoint[0] - self.gps("x"))**2 + (self.turnpoint[1] - self.gps("y"))**2)
            #print(distance)
        if distance >=0.12:
            distance = math.sqrt((self.turnpoint[0] - self.gps("x"))**2 + (self.turnpoint[1] - self.gps("y"))**2)
        if distance < 0.1:
            self.readSensors()
            #check if has path forward of the vertex, update the vertex 
            if (self.measures.lineSensor[3] == "1" or self.measures.lineSensor[4] == "1" or self.measures.lineSensor[2] == "1"):
                self.currentVertex.edges[self.direction] = 1 if self.currentVertex.edges[self.direction] == 0 else self.currentVertex.edges[self.direction]
                return 1
            return 1
        
        # prevDistance = distance
        walk = distance
        if walk > 0.03:
            walk = 0.03
            
        distance -= walk
        #print(distance)
        if distance <=0:
            return 1
        self.driveMotors(walk,walk)
        return 0
    
    def orient(self, direction):
        
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
        if power > 0.07:
            power = 0.07
        elif power < -0.07:
            power = -0.07
        
        self.previouspowerLR = (-power, power)
        self.driveMotors(-power, power)
        
        return 0

    
    def wander(self):
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
            #!change if beacon radius is not 2
            
            if self.inBeacon > 0:
                
                if self.inBeacon not in [vertex.beacon for vertex in self.vertexList]:
                    beaconVertex= Vertex()
                    beaconVertex.x = roundcoord(self.gps("x")+ cos(directionMap[self.direction]))
                    beaconVertex.y = roundcoord(self.gps("y")+ sin(directionMap[self.direction]))
                    beaconVertex.beacon = self.inBeacon
                    print("CREATED BEACON")
                    
                    beaconVertex.connects[inversedirectionMap[self.direction]] = self.prevVertex.id
                    
                    #! update connection of previous vertex to this vertex, if its a "normal vertex" it will be overwritten
                    self.prevVertex.connects[self.direction] = beaconVertex.id
                    self.vertexList[self.vertexList.index(self.prevVertex)] = self.prevVertex
                    
                    self.vertexList.append(beaconVertex)
                    
                    #!this is possible
                    self.currentVertex = beaconVertex
                
                    
                
                    
                    
            
            if((self.measures.lineSensor[:2].count("1") >= 2) or self.measures.lineSensor[5:7].count("1") >=2):
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