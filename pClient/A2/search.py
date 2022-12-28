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
        graph[vertex.id]={ id : hammond_distance( vertexlist, vertex.id , id  ) for id in vertex.connects.values() }
    return graph


def hammond_distance(vertexlist, id1, id2):
    return abs(vertexlist[ id1 ].x - vertexlist[id2].x) + abs(vertexlist[id1].y - vertexlist[id2].y)

def dijkstra(graph, start, end):
    shortest_distance = {}
    predecessor = {}
    unseenNodes = graph
    infinity = 9999999
    path = []
    for node in unseenNodes:
        shortest_distance[node] = infinity
    shortest_distance[start] = 0

    while unseenNodes:
        minNode = None
        for node in unseenNodes:
            if minNode is None:
                minNode = node
            elif shortest_distance[node] < shortest_distance[minNode]:
                minNode = node

        for childNode, weight in graph[minNode].items():
            if weight + shortest_distance[minNode] < shortest_distance[childNode]:
                shortest_distance[childNode] = weight + shortest_distance[minNode]
                predecessor[childNode] = minNode
        unseenNodes.pop(minNode)

    currentNode = end

    while currentNode != start:
        try:
       
            path.insert(0,currentNode)
            currentNode = predecessor[currentNode]
        except KeyError:
            print('Path not reachable')
            break
    path.insert(0,start)
   
    if shortest_distance[end] != infinity:
        return path
      
def directionqueue(vertexlist, start, end):
    graph=build_graph(vertexlist)

    shortest=dijkstra(graph, start, end)
    #print(shortest)
    if shortest is None:
        return []
    directions = []
    for i in range(len(shortest)-1):
        for key, value in vertexlist[shortest[i]].connects.items():
            if value == shortest[i+1]:
                directions.append(key)
    return directions

def pairwise(iterable):
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)

def get_path(vertexList, beaconlist):
    beacon_ids = [beacon.id for beacon in beaconlist if beacon.id != 0]
    print(beacon_ids)
    permutations = itertools.permutations(beacon_ids)
    optimal=[]
    min = 9999999
    for permutation in list(permutations):
        distance=0
        permutation = list(permutation)
        path = [0]
        permutation.insert(0, beaconlist[ [beaconlist.index(beacon) for beacon in beaconlist if beacon.id == 0][0] ].vertex.id)
        permutation.append(beaconlist[ [beaconlist.index(beacon) for beacon in beaconlist if beacon.id == 0][0] ].vertex.id)


        for pair in pairwise(permutation):
            graph=build_graph(vertexList)
            start = beaconlist[ [beaconlist.index(beacon) for beacon in beaconlist if beacon.id == pair[0]][0] ].vertex.id
            end = beaconlist[ [beaconlist.index(beacon) for beacon in beaconlist if beacon.id == pair[1]][0] ].vertex.id
            path.extend(dijkstra(graph, start, end)[1:])
       
        for vertex_a, vertex_b in pairwise(path):
            distance += hammond_distance(vertexList, vertex_a, vertex_b)
        print(permutation, distance)
        if distance < min:
            min = distance
            optimal = permutation
    return optimal, min


if __name__ == "__main__":
    with open('beaconvertex.pkl', 'rb') as inp:
        vertexlist = pickle.load(inp)
        
    graph= build_graph(vertexlist)
    print(directionqueue(vertexlist, 1, 15))