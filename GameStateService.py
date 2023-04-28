class GameStateService:
    def __init__(self, pacManLives:int):
        self.powerPellet = False
        self.score = 0
        self.powerCounter = 0
        self.counter = 0
        self.startupCounter = 0
        self.gameStart = False
        self.gameOver = False
        self.gameWon = False
        self.lives = pacManLives
        self.isScatterMode = True
        self.scatterCounter = 0
        self.attackCounter = 0
        self.runGame = True

    def isInTheBox(self, xPosition:int, yPosition:int) -> bool:
        return 345 < xPosition < 565 and 380 < yPosition < 490
    
    def isInReviveZone(self, xPosition:int, yPosition:int) -> bool:
        return 350 <= xPosition < 550 and 440 <= yPosition < 480
    
