class TurnManager:
    def __init__(self):
        self.up = False
        self.down = False
        self.left = False
        self.right = False
    
    def resetTurns(self):
        self.up = False
        self.down = False
        self.left = False
        self.right = False