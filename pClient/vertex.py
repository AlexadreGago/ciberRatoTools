class vertex():
    def __init__(self):
        self.explored = False
        # 0 unknown; 1 exists but unexplred ; 2 -Exists and explored ; 3- Unexistant;
        self.up = 0
        self.right = 0
        self.down = 0
        self.left = 0
        