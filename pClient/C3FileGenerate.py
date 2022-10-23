import pickle
import itertools

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
        #return f"{self.id}:{self.edges}" if not self.deadEnd else f"{self.id} is deadEnd, connects to {self.connects}"
        
def VertexPathToFile(vertexlist):
    
    prevVertex = None
    vertices=[0, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 39, 38, 38, 39, 42, 43, 44, 6, 5, 4, 1, 0]   
    vertexlist2 = []
    for v in vertices:
        vertexlist2.append(vertexlist[v])
    print(vertexlist2)
    for vertex in vertexlist2:
        print(vertex.x, vertex.y)
      
        
        if prevVertex is not None and vertex.x == prevVertex.x :
            #print(prevVertex.x, prevVertex.y,"\n", vertex.x, vertex.y)
            
            if prevVertex is None:
                continue  
            if prevVertex.y < vertex.y:
                for i in range (vertex.y - prevVertex.y):
                    if i % 2 == 0:
                        with open ("path.txt","a") as file:
                            
                            file.write(str(prevVertex.x)+" "+str(prevVertex.y+i)+"\n")
            #prev:10
            #vertex:0
            else:
                for i in range(prevVertex.y - vertex.y):
                    if i % 2 == 0:
                        with open ("path.txt","a") as file:
                            file.write(str(prevVertex.x)+" "+str(prevVertex.y-i)+"\n")
            
        
        elif prevVertex is not None and  vertex.y == prevVertex.y and prevVertex is not None:
            #print(prevVertex.x, prevVertex.y,"\n", vertex.x, vertex.y)
            
            if prevVertex is None:
                continue

            if prevVertex.x < vertex.x:
                for i in range (vertex.x - prevVertex.x):
                    if i %2 == 0:
                        with open ("path.txt","a") as file:
                            file.write(str(prevVertex.x+i)+" "+str(prevVertex.y)+"\n")
            else:
                for i in range (prevVertex.x - vertex.x):
                    if i %2 == 0:
                        with open ("path.txt","a") as file:
                            file.write(str(prevVertex.x-i)+" "+str(prevVertex.y)+"\n")
                            
        prevVertex = vertex
    with open ("path.txt","a") as file:
        file.write(str(vertexlist2[-1].x)+" "+str(vertexlist2[-1].y)+"\n")



def main():
    with open('beaconvertex.pkl', 'rb') as inp:
        vertexlist = pickle.load(inp)
        
    outMap = open("path.txt" ,"w")
    outMap.close()
    
    VertexPathToFile(vertexlist)
   
main()