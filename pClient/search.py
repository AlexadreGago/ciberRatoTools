def build_graph(vertexlist):
    graph = {}
    for vertex in vertexlist:
        graph[vertex.id] = [id for id in vertex.connects.values()]
    return graph


#find shortest path
def find_shortest_path(graph, start, end, path=[]):
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
    print(shortest)
    directions = []
    for i in range(len(shortest)-1):
        for key, value in vertexlist[shortest[i]].connects.items():
            if value == shortest[i+1]:
                directions.append(key)
    return directions
