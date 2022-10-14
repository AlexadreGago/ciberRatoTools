import sys
import time
import math
from croblink import *
from math import *
import xml.etree.ElementTree as ET

CELLROWS=7
CELLCOLS=14

#GLOBAL VARS ########
determined_vertex = 0
aligning = True
count=0
prevDistance=5
############

motorStrengthMap = {
    "front": (0.1,0.1),
    "frontslow": (0.05, 0.05),
    "backward": (-0.05,-0.05),
    "left": (-0.15,0.15),
    "right": (0.15,-0.15),
    "slightLeft": (0.08,0.1),
    "slightRight": (0.1,0.08),
    "stop": (0,0)
}

directionMap = {
    "right": 0,
    "up": 90,
    "left": -180,
    "down": -90
}

lastdecision = "stop"


#round to nearest multiple of 2
def roundcoord(x):
    return int(round(x / 2.0)) * 2

class Vertex():
    def __init__(self):
        self.explored = False
        self.x = -1
        self.y = -1
        # 0 unknown; 1 exists but unexplred ; 2 -Exists and explored ; 3- Unexistant;
        self.edges = {"up" : 0, 
                 "down" : 0, 
                 "left" : 0, 
                 "right" : 0}
        self.connects = {}
        
        


    


class MyRob(CRobLinkAngs):
    def __init__(self, rob_name, rob_id, angles, host):
        CRobLinkAngs.__init__(self, rob_name, rob_id, angles, host)
        
        self.previouspowerLR = (0,0)
        self.turnpoint = None
        self.currentVertex = None
        
        self.direction = "right"
        self.state = 'stop'

        self.vertexList=[]
        
        self.prevVertex = [0, 0]

        self.initialPos = [0,0]
        


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
            #print(self.direction)
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
    
    #offset gps with initialpos
    def gps(self, dir):
        return self.measures.x - self.initialPos[0] if dir == "x" else self.measures.y - self.initialPos[1]
   
    def vertexDiscovery(self):
        #print("VertexDicovery")
        #-----------------------------
        #Unrelated used in adjustForward
        global prevDistance
        prevDistance = 5
        #-----------------------------
        #if it isnt oriented, it will orient itself each call as the state isn´t changed
        isoriented = self.orient(self.direction)
        if isoriented == 1:

            #check if the vertex already exists, if it doesn´t, detect it and create it, if None is returned must have been a mistake
            vertex = self.checkNearVertex()
            if vertex:

                self.state = "decision"
                self.currentVertex = vertex
                #self.turnpoint= [self.measures.x + 0.438 * math.cos(math.radians(self.measures.compass)), self.measures.y + 0.438 * math.sin(math.radians(self.measures.compass))]
                self.turnpoint= [vertex.x, vertex.y]
                
                
            else :# IF NO VERTEX IS DETECTED
                print("must have been the wind ", self.measures.lineSensor)
                self.state = "return"

    def realposition(self):
        #return [ self.gps("x") + (0.5 * math.cos(math.radians(self.measures.compass))), self.gps("y") + (0.5 * math.sin(math.radians(self.measures.compass)))]
        return [ roundcoord(self.gps("x")), roundcoord(self.gps("y"))]
    def checkNearVertex(self):
        #if any vertice is within 0.5m of the current position, return that vertex
        for vertex in self.vertexList:
            #if distance of vertex to current position is less than 0.5m
            realposition = self.realposition()
            if sqrt((vertex.x - realposition[0])**2 + (vertex.y - realposition[1])**2) < 0.5:
                print("Found vertex",vertex.x, vertex.y, "at", realposition[0], realposition[1])
                return vertex
        #if vertex is not found nearby, must be a new one
        return self.detectVertex()
            
    def detectVertex(self):
        #print("detectVertex")
       
        if self.measures.lineSensor[0] == "1" or self.measures.lineSensor[6] == "1":
            vertex = Vertex()
            #offset vertex position because of the center of the robot
            vertex.x= self.gps("x") + (0.438 * math.cos(math.radians(self.measures.compass)))
            vertex.y= self.gps("y") + (0.438 * math.sin(math.radians(self.measures.compass)))
            
            if self.direction == "right":
                if self.measures.lineSensor[0] == "1":
                    vertex.edges["up"] = 1
                if self.measures.lineSensor[6] == "1":
                    vertex.edges["down"] = 1
                
                #explored we just came from there
                vertex.edges["left"] = 2
                
            elif self.direction == "left":
                if self.measures.lineSensor[0] == "1":
                    vertex.edges["down"] = 1    
                if self.measures.lineSensor[6] == "1":
                    vertex.edges["up"] = 1
                
                #explored we just came from there    
                vertex.edges["right"] = 2
    
            
            elif self.direction == "up":
                
                if self.measures.lineSensor[0] == "1":
                    vertex.edges["left"] = 1
                if self.measures.lineSensor[6] == "1":
                    vertex.edges["right"] = 1
                    
                #explored we just came from there
                vertex.edges["down"] = 2
            
            elif self.direction == "down":
                if self.measures.lineSensor[0] == "1":
                    vertex.edges["right"] = 1
                if self.measures.lineSensor[6] == "1":
                    vertex.edges["left"] = 1
                
                #explored we just came from there         
                vertex.edges["up"] = 2
    
            return vertex
        return None

    def move(self, direction, compensate = None):
        global lastdecision
        self.driveMotors(motorStrengthMap[direction][0], motorStrengthMap[direction][1])
        
    def adjustForward(self):
        global prevDistance
        distance = math.sqrt((self.turnpoint[0] - self.gps("x"))**2 + (self.turnpoint[1] - self.gps("y"))**2)
        dir = 0
        #prevent overshooting turnpoint
        #print("AdjustForward",prevDistance, distance)
        if prevDistance < distance:
            self.turnpoint = None
            #check if has path forward of the vertex, update the vertex 
            if (self.measures.lineSensor[3] == "1"):
                self.currentVertex.edges[self.direction] = 1
            print("Go back")
            self.driveMotors(-distance,-distance)
            return 1
        
        if distance < 0.0000008:
            self.turnpoint = None
            
            #check if has path forward of the vertex, update the vertex 
            if (self.measures.lineSensor[3] == "1"):
                self.currentVertex.edges[self.direction] = 1
            return 1
        
        prevDistance = distance
        
        if distance > 0.03:
            distance = 0.03
        self.driveMotors(distance,distance)
        return 0

    
    def orient(self, direction):
        #print("orient ", direction, " ", self.measures.compass)
        #TODO think about this
        
        global directionMap
        degrees = directionMap[direction]
        #align to this number
        
        
        #angle difference between target and now
        remaining = min(degrees-self.measures.compass, degrees-self.measures.compass+360, degrees-self.measures.compass-360, key=abs)
        #print("remaining: ", remaining, end = " ")
        
        #acceptable in this range
        if abs(remaining) <= 1:
            self.move("front")
            return 1
        
        #calculate power to give to motors, we'll give power to one motor and the symmetric to the other, depending on the angle
        power = math.radians(remaining) -  (0.5 * self.previouspowerLR[1]) + (0.5 * self.previouspowerLR[0])
        #print("power: ", power, end = " ")
        
        #low max power to avoid overshooting by noise
        if power > 0.07:
            power = 0.07
        elif power < -0.07:
            power = -0.07
        
        # print("power: ", power, end = " ")
        #print("previouspowerLR: ", self.previouspowerLR)
        
        self.previouspowerLR = (-power, power)
        self.driveMotors(-power, power)
        
        return 0
    
    def CreateVertex(self,x,y,edges):
        
        v1 = Vertex()
        v1.x = x
        v1.y=y
        v1.up = edges[0]
        v1.right = edges[1]
        v1.down = edges[2]
        v1.left = edges[3]
        
        self.vertexList.append(v1)
        return v1
    
    def Decide(self):
       
        bol = self.adjustForward()
        if bol == 1 :
            
            self.state = "orient"
            print("Decide")
            print("v1: ", self.currentVertex.edges,)
            
            decision = ""
            
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
                self.currentVertex.edges["left "] = 2
                decision="left"

            else:
                #!default if all explored
                print("default")
                decision = "right"
            
            self.vertexList.append(self.currentVertex) if self.currentVertex not in self.vertexList else None
            #update vertex in the list
            self.vertexList = [self.currentVertex if v.x == self.currentVertex.x and v.y == self.currentVertex.y else v for v in self.vertexList]

            self.direction = decision
            self.prevVertex = self.currentVertex
            self.currentVertex = None
            #replace on the vertex list the vertex

    
    def wander(self):
    
            
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
                print("near vertex ", self.measures.lineSensor)
                self.state="vertexDiscovery"
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
                print("near vertex ", self.measures.lineSensor)
                #TODO turn back
                self.direction = "down"
                self.state="orient"
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
