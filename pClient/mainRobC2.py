

from pickle import TRUE
import sys
import time
from croblink import *
from math import *
import xml.etree.ElementTree as ET

CELLROWS=7
CELLCOLS=14

#GLOBAL VARS ########

vCount = 0
vertices = []
turnLeft=0
turnRight=0
direction = "right"
i =0
count =0

############


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
        

def checkNearVertex(x,y):
    return None
    


class MyRob(CRobLinkAngs):
    def __init__(self, rob_name, rob_id, angles, host):
        CRobLinkAngs.__init__(self, rob_name, rob_id, angles, host)

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
        

    def wander(self):
        
        global turnRight
        global turnLeft
        global count
        global direction
        
        global i
        #print("LAST",lastLineSensors)
        
        #check if collision against wall
        center_id = 0
        left_id = 1
        right_id = 2
        back_id = 3
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
        else:
        #########################################
            
            if turnRight and turnLeft:  
                #TODO Decide
                turnLeft=False
                
            elif turnRight :
                print("TURN RIGHT")
                print(self.measures.compass)
                if direction == "left":          
                    if not(self.measures.compass > 80 and self.measures.compass < 100):
                        self.move("right")
                    else:
                        direction = "up"
                        turnRight=False
                        
                elif direction == "right":
                    print("pila")
                    if not(self.measures.compass < -80 and self.measures.compass > -100):
                        self.move("right")
                        print("pila2")
                        
                    else:
                        direction = "down"
                        print("pila3")
                        if count < 3:
                            self.move("front")                      
                            count+=1
                        else:
                            turnRight=False

                        
                elif direction == "down":
                    if not(self.measures.compass > 170 and self.measures.compass < -170):
                        self.move("right")
                    else:
                        direction = "left"
                        turnRight=False
                        
                elif direction == "up":
                    
                    if not(self.measures.compass < 10 and self.measures.compass > -10):
                        self.move("right")
                    else:
                        direction = "right"
                        turnRight=False

            elif turnLeft:
                print("TURN left")
                
                if direction == "left":
                         
                    if not(self.measures.compass < -80 and self.measures.compass > -100):
                        self.move("left")
                    else:
                        direction = "down"
                        turnLeft=False
                        
                elif direction == "right":
                    if not(self.measures.compass > 80 and self.measures.compass < 100):
                        self.move("left")
                    else:
                        direction = "up"
                        turnLeft=False
                        
                elif direction == "down":
                    if not(self.measures.compass < 10 and self.measures.compass > -10):
                        self.move("left")
                    else:
                        direction = "right"
                        turnLeft=False
                        
                elif direction == "up":
                    if not(self.measures.compass > 170 and self.measures.compass < -170):
                        self.move("left")
                    else:
                        direction = "left"
                        turnLeft=False


            elif(self.measures.lineSensor[0]=="1"or self.measures.lineSensor[6]=="1") and (not turnRight or not turnLeft):
                v1 = checkNearVertex(self.measures.x,self.measures.y)
                print(turnLeft)
                print(turnRight)

                if v1==None:  
                    #TODO ESTABILIZAR     
                    if(self.measures.lineSensor[0]=="1"):
                        turnLeft=True
                    if(self.measures.lineSensor[6]=="1"):
                        turnRight=True
                    print(turnLeft)
                    print(turnRight)
                    print("--------------------")
                    count=0
                    v1 = vertex()
                    v1.x = self.measures.x
                    v1.y = self.measures.y
                    vertices.append(v1)    

                
            elif self.measures.lineSensor == ["0","0","0","0","0","0","0"]:
                #print("%20s" % ("Line lost go back"), self.measures.lineSensor)
                self.move("backward")
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
