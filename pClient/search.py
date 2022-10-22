from unicodedata import name
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

def build_graph(vertexlist):
    graph = {}
    for vertex in vertexlist:
        if vertex.isDeadEnd:
            continue
        graph[vertex.id] = sorted([id for id in vertex.connects.values() if not vertexlist[id].isDeadEnd])
    return graph


#find shortest path
def find_shortest_path(graph, start, end, path=[]):
    #print(path)
    path = path + [start]
    if start == end:
        return path
    if start not in graph:
        return None
    shortest = None
    for node in graph[start]:
        if node not in path:
            newpath = find_shortest_path(graph, node, end, path)
            if newpath:
                if not shortest or len(newpath) < len(shortest):
                    shortest = newpath
    return shortest


      
def directionqueue(vertexlist, start, end):
    graph=build_graph(vertexlist)

    shortest=find_shortest_path(graph, start, end)
    #print(shortest)
    if shortest is None:
        print(f"No path found {start} to {end}")
        return []
    directions = []
    for i in range(len(shortest)-1):
        for key, value in vertexlist[shortest[i]].connects.items():
            if value == shortest[i+1]:
                directions.append(key)
    return directions

def beaconpath(vertexlist):
    graph=build_graph(vertexlist)

    


if __name__ == "__main__":
    with open('vertexlist.pkl', 'rb') as inp:
        vertexlist = pickle.load(inp)
    print(vertexlist)
    print(directionqueue(vertexlist, 1, 15))