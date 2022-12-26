import itertools
class Beacon():
    """ A beacon in the map """    
    def __init__(self,x=-1,y=-1,vertexList=[],id=-1):
        self.x = x
        self.y = y
        self.id = id
        if (x,y) in vertexList:
            self.isVertex = True
            self.vertex = vertexList[vertexList.index((x,y))]
        else:
            self.isVertex = False
            self.vertex = None
        self.connects = {}
        
    def update(self, vertexList: list) -> None:
        """fucking nigger"""
        print("at beacon update")
        for vertex in vertexList:
            if vertex == [self.x, self.y]:
                self.isVertex = True
                self.vertex = vertexList[vertexList.index((self.x,self.y))]
            
    def __repr__(self) -> str:
        return f"Beacon at ({self.x},{self.y}, id: {self.id}, isVertex: {self.isVertex}, vertex: {self.vertex})"
    
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
        if connects is not None:
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

    
v0 = Vertex(0,0)
v1 = Vertex(1,0)

vlist = [v0,v1]

b0 = Beacon(0,0, id=0)
b1 = Beacon(1,0, id=1)
b2 = Beacon(2,0, id=2)


print(b0)
print(v0)
b0.update(vlist)
print(b0)

