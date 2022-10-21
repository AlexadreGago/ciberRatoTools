import json

def build_graph(vertexlist):
    graph = {}
    for vertex in vertexlist:
        graph[vertex.id] = [id for id in vertex.connects.values()]
    return graph


#find shortest path
def BFS_SP(graph, start, end):
    queue = [(start, [start])]
    while queue:
        (vertex, path) = queue.pop(0)
        for next in set(graph[vertex]) - set(path):
            if next == end:
                return path + [next]
            else:
                queue.append((next, path + [next]))


      
def directionqueue(vertexlist, start, end):
    #write vertexlist to file
    graph=build_graph(vertexlist)
    print(graph[19])
    print(graph[20])
    print(20 in vertexlist[19].connects)
    print(19 in vertexlist[20].connects)
    shortest=BFS_SP(graph, start, end)
    print(shortest)
    # directions = []
    # for i in range(len(shortest)):
    #     for key, value in vertexlist[shortest[i]].connects.items():
    #         if value == shortest[i+1]:
    #             directions.append(key)
    # #print(directions)
    # return directions

