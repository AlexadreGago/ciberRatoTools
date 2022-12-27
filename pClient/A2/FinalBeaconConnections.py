import itertools
import search
from EndConnections import appendBeacons
import time

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
    
TURNSMAP = {
    "right": {"right": "down", "left": "up", "front": "right", "back": "left"},
    "left": {"right": "up", "left": "down", "front": "left", "back": "right"},
    "up": {"right": "right", "left": "left", "front": "up", "back": "down"},
    "down": {"right": "left", "left": "right", "front": "down", "back": "up"}
}

INVERSEDIRECTIONMAP = {
    "left": "right",
    "right": "left",  # {"left": "up", "right": "down"},
    "up": "down",
    "down": "up"
} 

class Beacon():
    """ A beacon in the map """    
    def __init__(self,x=-1,y=-1,vertexList=[],id=-1,direction = None):
        self.x = x
        self.y = y
        self.id = id
        self.direction = direction
        if (x,y) in vertexList:
            self.isVertex = True
            self.vertex = vertexList[vertexList.index((x,y))]
        else:
            self.isVertex = False
            self.vertex = None
        self.connects = {}
        
    def update(self, vertexList: list) -> None:
        """fucking """
        print("at beacon update")
        for vertex in vertexList:
            if vertex == [self.x, self.y]:
                self.isVertex = True
                self.vertex = vertexList[vertexList.index((self.x,self.y))]
            
    def __repr__(self) -> str:
        return f"Beacon at ({self.x},{self.y}, id: {self.id}, isVertex: {self.isVertex}, vertex: {self.vertex}),  connects: {self.connects},  direction: {self.direction}\n"
    
    def __eq__(self, o) -> bool:
        return (self.x, self.y) == (o.x, o.y)
        
    
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

    def __init__(self, x=-1, y=-1, isDeadEnd=False):
        self.x = x
        self.y = y
        # 0 unknown; 1 exists but unexplred ; 2 -Exists and explored ;
        self.edges = {"up": 0,
                      "down": 0,
                      "left": 0,
                      "right": 0}
        self.connects = {}
        self.id = next(Vertex.id_iter)
        self.isDeadEnd = isDeadEnd

    def __repr__(self) -> str:
        return f"Vertex {self.id} at ({self.x},{self.y}), edges: {self.edges}, connects: {self.connects} \n"

    def __eq__(self, o: list) -> bool:
        # get coordinates and check if equal to list of coordinates
        if type(o) == Vertex:
            return (self.x, self.y) == (o.x, o.y)
        else:
            return (self.x, self.y) == (o[0], o[1])

    def update(self, robot_dir,turns=[], visited=False, connects = None, vlist = []):
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
        if connects is not None:
            self.connects[INVERSEDIRECTIONMAP[robot_dir]] = connects.id
            connects.connects[robot_dir] = self.id
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
def InsertBeaconsInVertexList(vertexList, beaconList):
    beacon: Beacon
    for beacon in beaconList:
        print(beacon)
        beacon.update(vertexList)
    vertexList = appendBeacons(vertexList, beaconList,len(vertexList))


    print(beaconList)
    print(vertexList)
    for vertex in vertexList:
        if vertex.connects == {}:
            x = vertex.x
            y = vertex.y
            dir = [beacon.direction for beacon in beaconList if (beacon.x,beacon.y) == (x,y)][0]

            if dir == "up" or dir == "down":
                vertex.edges["up"] = 1
                vertex.edges["down"] = 1
                
                while vertex.connects == {}:
                    print("Searching for up")
                    y = y+2
                    for vertex2 in vertexList:
                        if (vertex2.x,vertex2.y) == (x,y):
                            vertex.connects["up"] = vertex2.id
                            vertex2.connects["down"] = vertex.id
                            break
                x = vertex.x
                y = vertex.y
                while len(vertex.connects) == 1:
                    print("Searching for down")
                    y = y-2
                    for vertex2 in vertexList:
                        if (vertex2.x,vertex2.y) == (x,y):
                            vertex.connects["down"] = vertex2.id
                            vertex2.connects["up"] = vertex.id
                            break
                
            else:
                vertex.edges["left"] = 1
                vertex.edges["right"] = 1
                
                while vertex.connects == {}:
                    print("Searching for left")
                    x = x-2
                    for vertex2 in vertexList:
                        if (vertex2.x,vertex2.y) == (x,y):
                            vertex.connects["left"] = vertex2.id
                            vertex2.connects["right"] = vertex.id
                            break
                x = vertex.x
                y = vertex.y
                while len(vertex.connects) == 1:
                    print("Searching for right")
                    x = x+2
                    for vertex2 in vertexList:
                        if (vertex2.x,vertex2.y) == (x,y):
                            vertex.connects["right"] = vertex2.id
                            vertex2.connects["left"] = vertex.id
                            break
    return vertexList