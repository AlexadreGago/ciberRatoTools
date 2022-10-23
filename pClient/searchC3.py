import pickle
import itertools


class Vertex():
    id_iter = itertools.count()
    def __init__(self, x=-1, y=-1):
        self.x = x
        self.y = y
        # 0 unknown; 1 exists but unexplred ; 2 -Exists and explored ;
        self.edges = {"up" : 0, 
                 "down" : 0, 
                 "left" : 0, 
                 "right" : 0}
        self.connects = {}
        self.id = next(Vertex.id_iter)
        self.isDeadEnd = False
        self.beacon = -1

    def __repr__(self) -> str:
        return f"Vertex {self.id} at ({self.x},{self.y}), edges: {self.edges}, connects: {self.connects} \n"


with open('beaconvertex.pkl', 'rb') as inp:
    vertexlist = pickle.load(inp)


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


def hammond_distance(vertexlist, id1, id2):
    return abs(vertexlist[ id1 ].x - vertexlist[id2].x) + abs(vertexlist[id1].y - vertexlist[id2].y)


def build_graph(vertexlist):
    graph = {}
    for vertex in vertexlist:
        graph[vertex.id]={ id : (weight := hammond_distance( vertexlist, vertex.id , id  ) ) for id in vertex.connects.values() }
    return graph

def pairwise(iterable):
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)



beacon_ids = [vertex.id for vertex in vertexlist if vertex.beacon != -1]
beacon_ids.append(0)

path=[]
for beacon_a, beacon_b in pairwise(beacon_ids):
    graph= build_graph(vertexlist)
    print(beacon_a, beacon_b)
    path.extend(dijkstra(graph, beacon_a, beacon_b))


print(path)
