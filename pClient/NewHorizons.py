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
############

motorStrengthMap = {
    "front": (0.1,0.1),
    "frontslow": (0.05, 0.05),
    "backward": (-0.05,-0.05),
    "left": (-0.15,0.15),
    "right": (0.15,-0.15),
    "slightLeft": (0.13,0.15),
    "slightRight": (0.15,0.13),
    "stop": (0,0)
}

directionMap = {
    "right": 0,
    "up": 90,
    "left": -180,
    "down": -90
}
    
vertices = []
lastdecision = "stop"

class Vertex():
    def __init__(self):
        self.explored = False
        self.x = -1
        self.y = -1
        # 0 unknown; 1 exists but unexplred ; 2 -Exists and explored ; 3- Unexistant;
        self.up = 0
        self.right = 0
        self.down = 0
        self.left = 0
        


    


class MyRob(CRobLinkAngs):
    def __init__(self, rob_name, rob_id, angles, host):
        CRobLinkAngs.__init__(self, rob_name, rob_id, angles, host)
        
        self.previouspowerLR = (0,0)
        self.turnpoint = None
        self.decidedWay= None
        self.prev_vertex = None
        
        self.direction = "right"
        self.state = 'stop'
        self.detecting_vertex = False
        self.nearvertex = 0
        self.vertexList=[]

        self.edges=[0,0,0,0]


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
            elif self.state=='return':
                if self.measures.visitingLed==True:
                    self.setVisitingLed(False)
                if self.measures.returningLed==True:
                    self.setReturningLed(False)
                self.wander()
            
    def vertexDiscovery(self):
        #print("VertexDicovery")
        if self.orient(self.direction) == 1:

            vertex = self.checkNearVertex()
            self.vertexList.append(vertex) if vertex not in self.vertexList else None
            
            if vertex != None:
                self.direction = self.Decide(vertex)
               
                self.turnpoint= [self.measures.x + 0.438 * math.cos(math.radians(self.measures.compass)), self.measures.y + 0.438 * math.sin(math.radians(self.measures.compass))]
                self.state = "orient"
                
                
            else :# IF NO VERTEX IS DETECTED
                self.state = "return"

    
    def checkNearVertex(self):
        #if any vertice is within 0.5m of the current position, return that vertex
        #print("checkNearVertex")
        for vertex in vertices:
            if (vertex.x - self.measures.x)**2 + (vertex.y - self.measures.y)**2 < 0.25:
                print("Found vertex")
                return vertex
        return self.detectVertex()
            
    def detectVertex(self):
        #print("detectVertex")
        vertex = Vertex()
        
        if self.measures.lineSensor[0] == "1" or self.measures.lineSensor[6] == "1":
            vertex.x= self.measures.x
            vertex.y= self.measures.y
            
            if self.direction == "right":
                if self.measures.lineSensor[0] == "1":
                    vertex.up = 1
                if self.measures.lineSensor[6] == "1":
                    vertex.down = 1
                
                #TODO change passinho a frente passinho atras
                vertex.right = 2
                #explored we just came from there
                vertex.left = 2
                
            elif self.direction == "left":
                if self.measures.lineSensor[0] == "1":
                    vertex.down = 1    
                if self.measures.lineSensor[6] == "1":
                    vertex.up = 1
                    
                vertex.right = 2
                vertex.left = 2
            
            elif self.direction == "up":
                
                if self.measures.lineSensor[0] == "1":
                    vertex.left = 1
                if self.measures.lineSensor[6] == "1":
                    vertex.right = 1
                    
                vertex.up = 2
                vertex.down = 2
            
            elif self.direction == "down":
                if self.measures.lineSensor[0] == "1":
                    vertex.right = 1
                if self.measures.lineSensor[6] == "1":
                    vertex.left = 1
                    
                vertex.up = 2
                vertex.down = 2
                
            return vertex
        return None



    def move(self, direction, compensate = None):
        global lastdecision
        self.driveMotors(motorStrengthMap[direction][0], motorStrengthMap[direction][1])
        
    def adjustForward(self):
        if self.turnpoint:
            distance = math.sqrt((self.turnpoint[0] - self.measures.x)**2 + (self.turnpoint[1] - self.measures.y)**2)
            #print(distance)
            if distance < 0.2:
                self.turnpoint = None

                return 1
            if distance > 0.05:
                distance = 0.05
            self.driveMotors(distance, distance)
            return 0
        return 1
    
    def orient(self, direction):
        print("orient ", direction)
        #TODO think about this
        bol = self.adjustForward() 
        if bol:
            
            global directionMap
            degrees = directionMap[direction]
            #align to this number
            
            
            #angle difference between target and now
            remaining = min(degrees-self.measures.compass, degrees-self.measures.compass+360, degrees-self.measures.compass-360, key=abs)
            #print("remaining: ", remaining, end = " ")
            
            #acceptable in this range
            if abs(remaining) < 2:
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
    
    def Decide(self,v1):
        print("Decide")
        print("v1: ", v1.up, v1.right, v1.down, v1.left)
        if v1.down == 1:
            v1.down = 2
            return "down"
        elif v1.right == 1:
            v1.right = 2
            return "right"
        elif v1.up == 1:
            v1.up = 2
            return "up"
        elif v1.left == 1:
            v1.left = 2
            return "left"
        
        else:
            #!default if all explored
            return "right"
        
    
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
            if self.measures.lineSensor == ["1","1","1","1","1","1","1"]:
                self.move("front")
                
            #go back if no line detected

            #if one of these sensors is "1" check if we´re near vertex  
            elif(self.measures.lineSensor[0] == "1") or (self.measures.lineSensor[6] == "1") :
                print("near vertex")
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
            else:
                self.move("front")
            # v1 = self.checkNearVertex()
            
            # if v1 == None: # we are not near a vertex
            #     if (self.measures.lineSensor[0]==1 or self.measures.lineSensor[6]==1) and self.finished_turning == True and not self.detecting_vertex: # if we detect a 1 in the first or last sensor,
            #         self.edges=[0,0,0,0]                                              # we check if we are near a vertex or if it is a line
            #         self.DetectVertex(self.measures.x,self.measures.y) # Find if it is near a vertex, if so create it in order to decice the way
            #         self.detecting_vertex = True
                        
            #     elif self.detecting_vertex: # stay here until vertex is detected or rejected
            #         self.nearvertex = self.DetectVertex(self.measures.x,self.measures.y)
                    
            #     else:# in case we are not near a vertex and no right or left sensor is at 1
            #         self.normalMove()
                    
            # else: # In case the vertex is already created/exists
                
            #     if v1 != self.prev_vertex: # check if we are in a new vertex in order to make a decision and turn
                    
            #         if self.decidedWay ==None: # We first decide the way to take and then we move
            #             self.decidedWay = self.Decide(v1,self.direction) # decidir o caminho a seguir tendo em conta a direçao atual
            #             self.finished_turning=False
                        
            #         else:
            #             self.finished_turning = self.Turn(self.decidedWay,self.direction)
            #             if self.finished_turning :
            #                 self.prev_vertex=v1 # para parar de virar e continuar a andar
            #                 self.decidedWay == None
                            
            #     else: # if we still are near the same vertex (v1!=prev_vertex)
            #         #FAZER O MESMO QUE O C1
            #         self.normalMove()
            
                    
                
          

                
                


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
