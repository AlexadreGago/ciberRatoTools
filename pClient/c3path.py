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


def VertexPathToFile(vertexlist, path):
    with open('pathh.txt', 'w') as f:
        for vertex in path:
            f.write(f" {vertexlist[vertex].x},{vertexlist[vertex].y}")
        
    
    
    
    
    
with open('beaconvertex.pkl', 'rb') as inp:
        vertexlist = pickle.load(inp)
path=[0, 1, 4, 5, 6, 7, 8, 43, 42, 39, 32, 31, 30, 29, 28, 27, 26, 25, 24, 23, 22, 21, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 39, 38, 38, 39, 42, 43, 44, 6, 5, 4, 1, 0]    
        
