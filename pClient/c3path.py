#import pickle
import itertools

from searchC3 import get_path

# class Vertex():
#     id_iter = itertools.count()
#     def __init__(self, x=-1, y=-1):
#         self.x = x
#         self.y = y
#         # 0 unknown; 1 exists but unexplred ; 2 -Exists and explored ;
#         self.edges = {"up" : 0, 
#                  "down" : 0, 
#                  "left" : 0, 
#                  "right" : 0}
#         self.connects = {}
#         self.id = next(Vertex.id_iter)
#         self.isDeadEnd = False
#         self.beacon = -1

#     def __repr__(self) -> str:
#         return f"{self.id}:{self.edges}" if not self.deadEnd else f"{self.id} is deadEnd, connects to {self.connects}"

def hammond_distance(vertexlist, id1, id2):
    return abs(vertexlist[ id1 ].x - vertexlist[id2].x) + abs(vertexlist[id1].y - vertexlist[id2].y)

def Generate_path_file(vertexlist):
    path=get_path(vertexlist)
    prev=0
    with open('myrob.path', 'w') as f:
        for vertex in path:
            
            if hammond_distance(vertexlist, vertex, prev) <= 2 :  
                f.write(f"{vertexlist[vertex].x} {vertexlist[vertex].y}\n")
            else:
                if vertexlist[vertex].x == vertexlist[prev].x:
                    diff = vertexlist[vertex].y - vertexlist[prev].y
                    if diff > 0:
                        for i in range(2, abs(diff)+1, 2):
                            f.write(f"{vertexlist[vertex].x} {vertexlist[prev].y + i}\n")
                    else:
                        for i in range(2, abs(diff)+1, 2):
                            f.write(f"{vertexlist[vertex].x} {vertexlist[prev].y - i}\n")
                else:
                    diff = vertexlist[vertex].x - vertexlist[prev].x
                    if diff>0:
                        for i in range(2, abs(diff)+1, 2):
                            f.write(f"{vertexlist[prev].x + i} {vertexlist[vertex].y}\n")
                    else:
                        for i in range(2, abs(diff)+1, 2):
                            f.write(f"{vertexlist[prev].x - i} {vertexlist[vertex].y}\n")
     
            prev = vertex
    print("Path file generated")

    
    
    
    


if __name__ == "__main__":
    with open('beaconvertex.pkl', 'rb') as inp:
        #vertexlist = pickle.load(inp)
        path=[0, 59, 58, 57, 16, 17, 18, 19, 20, 19, 21, 22, 24, 26, 28, 29, 30, 31, 32, 51, 50, 49, 46, 45, 44, 43, 36, 37, 38, 14, 41, 7, 6, 5, 4, 3, 2, 1, 0]
        #Generate_path_file(vertexlist)
    print("This is a module, not a program")