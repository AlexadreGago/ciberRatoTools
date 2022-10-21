import itertools
import pickle


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
    
    global data 
    
    createMap()
    outMap = open("map.txt" ,"r+")
    data = outMap.readlines()
    outMap.close()

    # insertEdges()
    InsertEdges2()
    

main()