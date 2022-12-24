import itertools

class bcolors:
    """class for colors in the terminal
    """
    BOLD = '\033[1m'
    DARK = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    INVERT = '\033[7m'
    HIDDEN = '\033[8m'

    GREY = '\033[90m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'

    RESET = '\033[0m'
    
class Beacon():
    """ A beacon in the map """
    id_iter = itertools.count()
    
    def __init__(self,x=-1,y=-1,vertexList=[]):
        self.x = x
        self.y = y
        self.id = next(Beacon.id_iter)
        if (x,y) in vertexList:
            self.isVertex = True
            self.vertex = vertexList[vertexList.index((x,y))]
        else:
            self.isVertex = False
            self.vertex = None
        self.connects = {}
        
    def __repr__(self) -> str:
        return f"Beacon at ({self.x},{self.y}, id: {self.id}, isVertex: {self.isVertex}, vertex: {self.vertex})"
    
    def __eq__(self, o: list) -> bool:
        # get coordinates and check if equal to list of coordinates
        return (self.x, self.y) == (o[0], o[1])
    
    def update(self,connections = None):
        self.connects = connections
        
    
class Vertex():
    """A vertex in the graph

    Attributes:
        x (int): x coordinate
        y (int): y coordinate
        edges (dict): a dictionary of edges, keys are directions, values are 0 for nonexistant, 1 for exists but unexplored, 2 for exists and explored
        connects (dict): a dictionary of vertices that this vertex connects to, keys are directions, values are the vertex
        id (int): the id of the vertex
        isDeadEnd (bool): whether this vertex is a dead end

    Methods:
        __init__(x,y): initializes the vertex
        __repr__(): returns a string representation of the vertex

    """
    id_iter = itertools.count()

    def __init__(self, x=-1, y=-1):
        self.x = x
        self.y = y
        # 0 unknown; 1 exists but unexplred ; 2 -Exists and explored ;
        self.edges = {"up": 0,
                      "down": 0,
                      "left": 0,
                      "right": 0}
        self.connects = {}
        self.id = next(Vertex.id_iter)
        self.isDeadEnd = False
        self.isBeacon = False

    def __repr__(self) -> str:
        return f"Vertex {self.id} at ({self.x},{self.y}), edges: {self.edges}, connects: {self.connects}, isBeacon: {self.isBeacon} \n"

    def __eq__(self, o: list) -> bool:
        # get coordinates and check if equal to list of coordinates
        return (self.x, self.y) == (o[0], o[1])

    def update(self, robot_dir, turns=[], visited=False, connects = None):
        """updates the possible turns of this vertex
        #! in the future, update the connects as well
        #! also estamos a deixar dar overwrite sempre que passa por um vertice, nao sei se e bom

        Args:
            robot_dir (str): the direction the robot is facing
            turns (dict): the turns list

        Returns:
            None
        """
        # # update the edges
        # print(f"updating vertex {self.id} {self.edges}")
        # print(f"robot_dir: {robot_dir}")
        # print(f"turns: {turns}")

        if visited:
            self.edges[INVERSEDIRECTIONMAP[robot_dir]] = 2
        
        if turns:
            for turn in turns:
                edge = TURNSMAP[robot_dir][turn]
                if self.edges[edge] == 0:
                    self.edges[edge] = 1
        if connects:
            self.connects[INVERSEDIRECTIONMAP[robot_dir]] = connects
            return
    def updateEdges(self, edges):
        for edge in edges:
            self.edges[edge] = 1
        # self.edges = {}
        
    def getDirections(self):
        """returns the possible turns from this vertex

        Args:
            robot_dir (str): the direction the robot is facing

        Returns:
            list: the possible turns
        """
        return [
            direction 
            for direction in self.edges
            if self.edges[direction] == 1
        ]


def roundPowerOf2(x):
    """round to nearest multiple of 2

    Args:
        x (float): the number to round

    Returns:
        int: the rounded number
    """
    return int(round(x / 2.0)) * 2

vertexList = []
#create a list of vertices with the vertex class
v0 = Vertex(0,0) 
v1 = Vertex(2,0) 
v2 = Vertex(4,0) 
v3 = Vertex(4,4) 
v4 = Vertex(6,4) 
# X--* --X
#    |   |
#        X
#        |
#        *--*
v0.edges["right"] = 1
v1.edges["left"] = 1
v1.edges["right"] = 1
v2.edges["left"] = 1
v2.edges["down"] = 1
v3.edges["up"] = 1
v3.edges["right"] = 1
v4.edges["up"] = 1

v0.connects["right"] = v1.id
v1.connects["left"] = v0.id
v1.connects["right"] = v2.id
v2.connects["left"] = v1.id
v2.connects["down"] = v3.id
v3.connects["up"] = v2.id
v3.connects["right"] = v4.id
v4.connects["left"] = v3.id

vertexList.append(v0)
vertexList.append(v1)
vertexList.append(v2)
vertexList.append(v3)
vertexList.append(v4)
print(vertexList)

#---------------------------------------------

beaconList = []

b0 = Beacon(0,0,vertexList)
b1 = Beacon(4,0,vertexList)
b2 = Beacon(4,2,vertexList)
# X--* --X
#    |   |
#        X
#        |
#        *--*

b0.connects["right"] = v1.id#! DE ALGUMA MANEIRA TEMOS DE TER AS CONNECTIOND DO BEACON SENAO NAO SEI RESOLVER
b1.connects["left"] = v1.id
b1.connects["down"] = v3.id
b2.connects["up"] = v2.id
b2.connects["down"] = v3.id

beaconList.append(b0)
beaconList.append(b1)
beaconList.append(b2)
print(beaconList)

for beacon in beaconList:
    if beacon.isVertex:#* Se o beacon for um vertece nao se passa nada
        print("------------------")
        print(f"{bcolors.GREEN}Beacon {beacon.id} is a vertex{bcolors.RESET}")
        #print(f"Vertex id: {beacon.vertex}")
        print(f"Connects: {beacon.connects}")
    else:#* Se for temos de criar um vertice e adicionar as connections e alterar as connections dos outros vertices
        print("------------------")
        print(f"{bcolors.RED}Beacon {beacon.id} is not a vertex{bcolors.RESET}")
        print(f"Connects: {beacon.connects}")
        print("correction connections")
        
        vertex_beacon = Vertex(beacon.x,beacon.y) #* criacao do vertice novo
        vertex_beacon.isBeacon = True
        v_ids = []
        for connection in beacon.connects:#* meter as edges e connects do vertice novo
            v_ids.append(beacon.connects[connection])#* isto é para meter os ids dos vertices que o beacon conecta depois
            if connection == "up":
                vertex_beacon.edges["up"] = 1
                vertex_beacon.connects["up"] = beacon.connects[connection]
                print(f"up: {beacon.connects[connection]}")
                
            if connection == "down":
                vertex_beacon.edges["down"] = 1
                vertex_beacon.connects["down"] = beacon.connects[connection]
                print(f"down: {beacon.connects[connection]}")
                
            if connection == "left":
                vertex_beacon.edges["left"] = 1
                vertex_beacon.connects["left"] = beacon.connects[connection]
                print(f"left: {beacon.connects[connection]}")
                
            if connection == "right":
                vertex_beacon.edges["right"] = 1
                vertex_beacon.connects["right"] = beacon.connects[connection]
                print(f"right: {beacon.connects[connection]}")
                
        print(v_ids)
        for vertex in vertexList:#* alterar as connections dos outros vertices deve haver uma maneira mais facil de fazer isto  mas ja esta
            if vertex.id in v_ids:
                for connection in vertex.connects:
                    if vertex.connects[connection] in v_ids:
                        vertex.connects[connection] = vertex_beacon.id
                        print("altered: ",vertex)
                vertex.connects = vertex_beacon.connects
                #! FALTA ATUALIZAR OS VERTICES ANTIGOS NA VERTEXLIST
                #!...............
        
        print("New Vertex ",vertex_beacon)
        vertexList.append(vertex_beacon)
        print(vertexList)

        
