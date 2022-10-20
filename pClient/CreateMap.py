import linecache
import time
    
# global startx = round(49/2)
# global starty = round(21/2)
global data
def createMap():
    
    outMap = open("map.txt", "w+")

    #Create a 2D board
    for i in range(21):
        for j in range(49):
            outMap.write(" ")
        outMap.write('a\n')
    outMap.close()
    
    

    
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
        alterMap(int(x),-int(y),"*")
    alterMap(0,0,"X")
    with open ("map.txt","w") as file:
        file.writelines(data)

def insertEdges():
    global data
    vList = open("vertexList2.txt","r+")
    vertexList = vList.readlines()
    vList.close()
    
    for vertex in vertexList:
        #x of the vertex
        start = '{'
        end = '}'
        edges = (vertex[vertex.find(start)+len(start):vertex.find(end)])

        print(edges)

    
    
def main():
    createMap()
    global data 
    outMap = open("map.txt" ,"r+")
    data = outMap.readlines()
    outMap.close()
    insertVertex()
    
    insertEdges()

    
main()