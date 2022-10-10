
import sys
from croblink import *
from math import *
import xml.etree.ElementTree as ET

CELLROWS=7
CELLCOLS=14

motorStrengthMap = {
    "front": (0.15,0.15),
    "frontslow": (0.03, 0.03),
    "backward": (-0.15,-0.15),
    "left": (-0.15,0.15),
    "right": (0.15,-0.15),
    "slightLeft": (0.13,0.15),
    "slightRight": (0.15,0.13),
    "stop": (0,0)
}
lastdecision = "stop"
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
            #print("State: ", state)
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
        print(self.measures.compass)
        #try to prevent looping between front and back
        if lastdecision == "backward" and direction == "front":
            self.driveMotors(motorStrengthMap["frontslow"][0],motorStrengthMap["frontslow"][1])
            lastdecision = "front"
            
            print("%20s" % ("Anti front/back loop"), self.measures.lineSensor)
            return
        elif lastdecision == "backward" and (direction == "left" or direction == "right"):
            self.driveMotors(motorStrengthMap[direction][0],motorStrengthMap[direction][1])
            lastdecision = direction
            print("%20s" % ("Anti front/back loop"), self.measures.lineSensor)
            return
            
            
        
        #when stuck in a turn turning left and right, go a bit forward
        if  (direction == "left" or direction == "right"):
            if lastdecision == "left" or lastdecision == "right":
                if direction != lastdecision:
                    self.driveMotors(motorStrengthMap["frontslow"][0], motorStrengthMap["frontslow"][1])
                    lastdecision = "front"
                   
                    print("%20s" % ("Anti left/right loop"), self.measures.lineSensor)
                    
                
                #after noise prevention, turn left or right
                else:
                    self.driveMotors(motorStrengthMap[direction][0], motorStrengthMap[direction][1])
                    lastdecision = direction
                    
                    print("%20s" % ("Turn "+ direction +" no noise"), self.measures.lineSensor)
                    
            else:
                #try to detect certain intersection, else assume its noise
                if  ( direction == "left" and (self.measures.lineSensor[:2].count("1") == 2) ) or ( direction == "right" and (self.measures.lineSensor[5:].count("1") == 2) ):
                    self.driveMotors(motorStrengthMap[direction][0], motorStrengthMap[direction][1])
                    lastdecision = direction
                    
                    print("%20s" % ("Turn "+ direction + " certain"), self.measures.lineSensor)
                   
                else:
                #noise prevention
                    if lastdecision == "backward" :
                        self.driveMotors(motorStrengthMap["frontslow"][0], motorStrengthMap["frontslow"][1])
                        print("%20s" % ("Back/Noise loop Prevention"), self.measures.lineSensor)
                    else:
                        print("%20s" % ("Noise Prevention"), self.measures.lineSensor)
                        self.driveMotors(motorStrengthMap["front"][0], motorStrengthMap["front"][1])
                        lastdecision = direction
    
        
        else:
            print("%20s" % ("Turn "+ direction), self.measures.lineSensor)
            self.driveMotors(motorStrengthMap[direction][0], motorStrengthMap[direction][1])
            lastdecision = direction
    
        
        
        # lastLineSensors=self.measures.lineSensor
        # lastdecision=direction
        # self.driveMotors(motorStrengthMap[direction][0], motorStrengthMap[direction][1])
        

    def wander(self):
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
            
            #locked in turn
            #if all 7 sensors report "1"
            if self.measures.lineSensor == ["1","1","1","1","1","1","1"]:
                
                self.move("front")
                
            #go back if no line detected
            elif self.measures.lineSensor == ["0","0","0","0","0","0","0"]:
               
                self.move("backward")
            
            #turn left if the leftmost sensor detects a line
            # (self.measures.lineSensor[:3].count("1") >= 2) and 
            
            elif(self.measures.lineSensor[0] == "1") :
                
                self.move("left")
                
            #turn right if the rightmost sensor detects a line
            elif(self.measures.lineSensor[6] == "1"):
                
                self.move("right")
        
            
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
