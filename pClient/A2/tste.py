
        print("PUTA",self.direction,self.measures.lineSensor)

        if self.turnDirection =="":
            self.state="wander"
        if self.turnDirection == "right":
            
            if self.measures.compass > directionMap[self.direction] -8 and self.measures.compass < directionMap[self.direction]+8:
                # if int(self.measures.lineSensor[0])+int(self.measures.lineSensor[1])+int(self.measures.lineSensor[5])+int(self.measures.lineSensor[6])+int(self.measures.lineSensor[4])+int(self.measures.lineSensor[2]) ==0:
                #     #FUCKUP GO BACK
                #     print("fuckup")
                    
                #     self.state = "vertexDiscovery"
                #     self.turnDirection = ""
                #     self.calls = 0
                #     self.rightCounter = 0
                #     self.leftCounter = 0
                #     self.direction = self.nextDirection("left")
                    
                #     self.move("left")
                # else:
                print("im aligned")
                self.state="wander"
                self.turnDirection=""
                
            elif(self.measures.lineSensor[6] == "1"):
                self.move("right")
            elif(self.measures.lineSensor[5]=="1"):
                self.move("slightRight")
            elif self.measures.compass < directionMap[self.direction] - 8:
                if int(self.measures.lineSensor[0])+int(self.measures.lineSensor[1])+int(self.measures.lineSensor[2])+int(self.measures.lineSensor[3])+int(self.measures.lineSensor[4])+int(self.measures.lineSensor[5])+int(self.measures.lineSensor[6])==0:
                    self.move("stoppedLeft")
                else:
                    self.move("slightLeft")
            elif self.measures.compass > directionMap[self.direction] + 8 :
                if int(self.measures.lineSensor[0])+int(self.measures.lineSensor[1])+int(self.measures.lineSensor[2])+int(self.measures.lineSensor[3])+int(self.measures.lineSensor[4])+int(self.measures.lineSensor[5])+int(self.measures.lineSensor[6])==0:
                    self.move("stoppedRight")
                else:
                    self.move("slightRight")

                
            # elif(self.measures.lineSensor[6] == "1"):
            #     self.move("right")
            # elif(self.measures.lineSensor[5]=="1"):
            #     self.move("slightRight")
            # else:
            #     self.move("frontslow")
                
        if self.turnDirection == "left":
            if self.measures.compass > directionMap[self.direction] -8 and self.measures.compass < directionMap[self.direction]+8:
                # if int(self.measures.lineSensor[0])+int(self.measures.lineSensor[1])+int(self.measures.lineSensor[5])+int(self.measures.lineSensor[6]) ==0:
                #     #FUCKUP GO BACK
                #     print("fuckup")
                #     self.state = "vertexDiscovery"
                #     self.turnDirection = ""
                #     self.calls = 0
                #     self.rightCounter = 0
                #     self.leftCounter = 0
                #     self.direction = self.nextDirection("right")
                # else:
                self.move("right")
                print("im aligned")
                self.state="wander"
                self.turnDirection=""
                
            elif(self.measures.lineSensor[0] == "1"):
                self.move("left")
            elif(self.measures.lineSensor[1]=="1"):
                self.move("slightLeft")
            elif self.measures.compass < directionMap[self.direction] - 8:
                if int(self.measures.lineSensor[0])+int(self.measures.lineSensor[1])+int(self.measures.lineSensor[2])+int(self.measures.lineSensor[3])+int(self.measures.lineSensor[4])+int(self.measures.lineSensor[5])+int(self.measures.lineSensor[6])==0:
                    self.move("stoppedLeft")
                else:
                    self.move("slightLeft")
            elif self.measures.compass > directionMap[self.direction] + 8 :
                if int(self.measures.lineSensor[0])+int(self.measures.lineSensor[1])+int(self.measures.lineSensor[2])+int(self.measures.lineSensor[3])+int(self.measures.lineSensor[4])+int(self.measures.lineSensor[5])+int(self.measures.lineSensor[6])==0:
                    self.move("stoppedRight")
                else:
                    self.move("slightRight")
                