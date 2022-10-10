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
############

vertices = []
motorStrengthMap = {
    "front": (0.15,0.15),
    "frontslow": (0.05, 0.05),
    "backward": (-0.15,-0.15),
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
    

lastdecision = "stop"

class vertex():
    def __init__(self):
        self.explored = False
        self.x = -1.0
        self.y = -1.0
        # 0 unknown; 1 exists but unexplred ; 2 -Exists and explored ; 3- Unexistant;
        self.up = 0
        self.right = 0
        self.down = 0
        self.left = 0
        


    


class MyRob(CRobLinkAngs):
    def __init__(self, rob_name, rob_id, angles, host):
        CRobLinkAngs.__init__(self, rob_name, rob_id, angles, host)
        
        self.previouspowerLR = (0,0)
       
        self.decidedWay= None
        self.prev_vertex = None
        
        
        self.direction = "right"
        
        
        self.detecting_vertex = False
        self.nearvertex = 0
        self.vertexList=[]
        self.finished_turning = True
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

        state = 'stop'
        stopped_state = 'run'

        while True:
            self.readSensors()

            if self.measures.endLed:
                print(self.rob_name + " exiting")
                quit()

            if state == 'stop' and self.measures.start:
                state = stopped_state

            if state != 'stop' and self.measures.stop:
                stopped_state = state
                state = 'stop'

            if state == 'run':
                if self.measures.visitingLed==True:
                    state='wait'
                if self.measures.ground==0:
                    self.setVisitingLed(True);
                self.wander()            
            elif state=='wait':
                self.setReturningLed(True)
                if self.measures.visitingLed==True:
                    self.setVisitingLed(False)
                if self.measures.returningLed==True:
                    state='return'
                self.driveMotors(0.0,0.0)
            elif state=='return':
                if self.measures.visitingLed==True:
                    self.setVisitingLed(False)
                if self.measures.returningLed==True:
                    self.setReturningLed(False)
                self.wander()
            

    def move(self, direction):
        global lastdecision
        self.driveMotors(motorStrengthMap[direction][0], motorStrengthMap[direction][1])
        lastdecision = direction

    
    
        # lastLineSensors=self.measures.lineSensor
        # lastdecision=direction
        # self.driveMotors(motorStrengthMap[direction][0], motorStrengthMap[direction][1])

    def orient(self, direction):
        global directionMap
        degrees = directionMap[direction]
        #align to this number
        degrees = 142
        
        
        #angle difference between target and now
        remaining = min(degrees-self.measures.compass, degrees-self.measures.compass+360, degrees-self.measures.compass-360, key=abs)
        print("remaining: ", remaining, end = " ")
        
        #acceptable in this range
        if abs(remaining) < 0.5:
            return 1
        
    
        #calculate power to give to motors, we'll give power to one motor and the symmetric to the other, depending on the angle
        power = math.radians(remaining) -  (0.5 * self.previouspowerLR[1]) + (0.5 * self.previouspowerLR[0])
        print("power: ", power, end = " ")
        
        #low max power to avoid overshooting by noise
        if power > 0.07:
            power = 0.07
        elif power < -0.07:
            power = -0.07
        
        # print("power: ", power, end = " ")
        print("previouspowerLR: ", self.previouspowerLR)
        
        self.previouspowerLR = (-power, power)
        self.driveMotors(-power, power)
        
        return 0

            
        
    
    def checkNearVertex(self):
    #if any vertice is within 0.5m of the current position, return that vertex
        for vertex in vertices:
            if (vertex.x - self.measures.x)**2 + (vertex.y - self.measures.y)**2 < 0.25:
                return vertex
        return None
    
    def DetectVertex(self): # check if the rebot is near a vertex(not created yet)
        
        global determined_vertex # check if done orienting
        determined_vertex = self.orient(self.direction)
        
        if determined_vertex==0:
            #Continue deciding
            self.edges[1]=1 #(example)
            return 0
        
        elif determined_vertex==1:
            self.CreateVertex(self.measures.x,self.measures.y, self.edges)
            self.detecting_vertex = False # this is to escape the loop
            return 1
        
        elif determined_vertex==2:
            self.detecting_vertex = False # this is to escape the loop
            return
    
    def CreateVertex(self,x,y,edges):
        
        v1 = vertex()
        v1.x = x
        v1.y=y
        v1.up = edges[0]
        v1.right = edges[1]
        v1.down = edges[2]
        v1.left = edges[3]
        
        self.vertexList.append(v1)
        return 
    
    def Decide(v1,direction):
        
        if v1.up == 1 and direction != "up" and direction != "down":
            return "up"
        elif v1.right == 1 and direction != "right" and direction != "left":
            return "right"
        elif v1.down == 1 and direction != "down" and direction != "up":
            return "down"
        elif v1.left == 1 and direction != "left" and direction != "right":
            return "left"
    
        elif v1.up == 2  and direction != "up" and direction != "down":
            return "up"
        elif v1.right == 2 and direction != "right" and direction != "left":
            return "right"
        elif v1.down == 2 and direction != "down" and direction != "up":
            return "down"
        elif v1.left == 2 and direction != "left" and direction != "right":
            return "left"
        
        else:
            return direction
        
    
    def Turn(self,direction):
    
        
        #when done
        
        self.finished_turning = True
        return False
    
    
    
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
