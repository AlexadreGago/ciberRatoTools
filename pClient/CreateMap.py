import itertools
import linecache
import time
import pickle
# global startx = round(49/2)
# global starty = round(21/2)
global data
def createMap():
    
    outMap = open("map.txt", "w+")

    #Create a 2D board
    for i in range(21):
        for j in range(49):
            outMap.write(" ")
        outMap.write('\n')
    outMap.close()
    
    
class Vertex():
    id_iter = itertools.count()
    def __init__(self, x=-1, y=-1):
        self.x = x
        self.y = y
        # 0 unknown; 1 exists but unexplred ; 2 -Exists and explored ; 3- Unexistant;
        self.edges = {"up" : 0, 
                 "down" : 0, 
                 "left" : 0, 
                 "right" : 0}
        self.connects = {}
        self.id = next(Vertex.id_iter)
        self.isDeadEnd = False
    def __repr__(self) -> str:
        return f"Vertex {self.id} at ({self.x},{self.y}), edges: {self.edges}, connects: {self.connects} \n"
    
def alterMap(posx,line,newData):
    global data
    startx = round(49/2)
    starty = round(21/2)
    #change data
    dataChars = list(data[line+starty])
        
    newDataList = list(newData)
    
    #Put data in specific position
    for i in range(len(newDataList)):

        dataChars[startx + i +posx] = str(newDataList[i])
            
    data[line+starty] = "".join(dataChars)
    


def insertVertex():
    
    global data
    
    vList = open("vertexList2.txt","r+")
    vertexList = vList.readlines()
    vList.close()
    
    for vertex in vertexList:
        #x of the vertex
        start = '('
        end = ','
        x = (vertex[vertex.find(start)+len(start):vertex.find(end)])
        start = ','
        end = ')'
        y = (vertex[vertex.find(start)+len(start):vertex.find(end)])
        alterMap(int(x),-int(y)," ")
        
    alterMap(0,0,"I")
    with open ("map.txt","w") as file:
        file.writelines(data)

def insertEdges():
    global data
    vList = open("vertexList2.txt","r+")
    vertexList = vList.readlines()
    vList.close()
    prevX = None
    prevY = None
    for vertex in vertexList:
         #x of the vertex
        start = '{'
        end = '}'
        edges = (vertex[vertex.find(start)+len(start):vertex.find(end)])
        start = '('
        end = ','
        
        x = int((vertex[vertex.find(start)+len(start):vertex.find(end)]))
        start = ','
        end = ')'
        y = int((vertex[vertex.find(start)+len(start):vertex.find(end)]))

    
        

        if prevX != None:
            if prevX == x:
                print("filling y axis")
                startx = round(49/2)
                starty = round(21/2)
            for j in range (max(y,prevY)-min(y,prevY)-1):
                # print("j",j)
                # print(max(y,prevY)+starty+j+1)
                
                dataChars = list(data[min(-y,-prevY)+starty+j+1])
                
                dataChars[x+startx] = "|"
                data[min(-y,-prevY)+starty+j+1] = "".join(dataChars)
                
                with open ("map.txt","r+") as file:
                    file.writelines(data)      

                
            if prevY == y:
                print("filling x axis")
                startx = round(49/2)
                starty = round(21/2)
                #change data

                dataChars = list(data[-y+starty])
                
                #Put data in specific position
                for j in range ((max(x,prevX)-min(x,prevX))-1):
                    if j %2 == 0:
                        dataChars[startx +min(x,prevX)+j+1] = "-"

                data[-y+starty] = "".join(dataChars)
                
            prevX = x
            prevY = y
        else:
            prevX = x
            prevY = y
        print("------")
            
        # time.sleep(3)
        
    alterMap(0,0,"I")
    with open ("map.txt","w") as file:
        file.writelines(data)

def InsertEdges2():
    vertexList = None
    inp = open("vertexlist.pkl","rb")
    vertexList = pickle.load(inp)
    
    for vertex in vertexList:
        print("-----------------")
        print("vertex",vertex)
        
        x = vertex.x
        y = vertex.y
        
        for connect in vertex.connects:
            conX = vertexList[vertex.connects[connect]].x
            conY = vertexList[vertex.connects[connect]].y
            
            print("Connect",conX,conY)
            print("Real",x,y)
            if conX == x:
                print("filling y axis")
                startx = round(49/2)
                starty = round(21/2)
            for j in range (max(y,conY)-min(y,conY)-1):
                # print("j",j)
                # print(max(y,prevY)+starty+j+1)
                if j %2 == 0:
                
                    dataChars = list(data[min(-y,-conY)+starty+j+1])
                    
                    dataChars[x+startx] = "|"
                    data[min(-y,-conY)+starty+j+1] = "".join(dataChars)
                    
                    with open ("map.txt","r+") as file:
                        file.writelines(data)      

                
            if conY == y:
                print("filling x axis")
                startx = round(49/2)
                starty = round(21/2)
                #change data

                dataChars = list(data[-y+starty])
                
                #Put data in specific position
                for j in range ((max(x,conX)-min(x,conX))-1):
                    if j %2 == 0:
                        dataChars[startx +min(x,conX)+j+1] = "-"

                data[-y+starty] = "".join(dataChars)
    
def main():
    createMap()
    global data 
    outMap = open("map.txt" ,"r+")
    data = outMap.readlines()
    outMap.close()
    insertVertex()

    # insertEdges()
    InsertEdges2()
    

main()