import pygame as pg
from GameStateService import GameStateService
from Ghosts.Ghost import Ghost

from direction import Directions
from utilities.TurnManager import TurnManager

class PacMan:
    def __init__(self, gameStateService:GameStateService, screen:pg.Surface, board:list[list[int]], startX:int, startY:int):
        self.pacManImages = []
        self.pacManImages.append(pg.transform.scale(pg.image.load(f'assets/PacManClose.png'),(45,45)))
        self.pacManImages.append(pg.transform.scale(pg.image.load(f'assets/PacManMid.png'),(45,45)))
        self.pacManImages.append(pg.transform.scale(pg.image.load(f'assets/PacManOpen.png'),(45,45)))
        self.xPos = startX
        self.yPos = startY
        self.dirRequest = Directions.RIGHT
        self.direction = Directions.RIGHT
        self.curVelocity = 2
        self.gameStateService = gameStateService
        self.screen = screen
        self.board = board
        self.turnManager = TurnManager()
        self.hitbox = pg.draw.circle(self.screen, 'black', (self.getPacManCenterX(), self.getPacManCenterY()), 20, 2)

    def setNewBoard(self, board:list[list[int]]):
        self.board = board

    def getPacManCenterX(self):
        return self.xPos + 22

    def getPacManCenterY(self):
        return self.yPos + 23
    
    def isInMiddleOfTileX(self):
        tile_width = self.screen.get_width() // 30 #30 horizontal tiles
        if 12 <= self.getPacManCenterX() % tile_width <= 18:
            return True
        return False

    def isInMiddleOfTileY(self):
        tile_height = (self.screen.get_height() - 50) // 32 #32 vertical tiles
        if 12 <= self.getPacManCenterY() % tile_height <= 18:
            return True
        return False


    def draw(self,gameStateService: GameStateService):
        self.hitbox = pg.draw.circle(self.screen, 'black', (self.getPacManCenterX(), self.getPacManCenterY()), 20, 2)
        if self.direction == Directions.RIGHT: 
            self.screen.blit(self.pacManImages[gameStateService.counter // 9], (self.xPos,self.yPos))
        elif self.direction == Directions.LEFT: 
            self.screen.blit(pg.transform.flip(self.pacManImages[gameStateService.counter // 9],True,False), (self.xPos,self.yPos))
        elif self.direction == Directions.UP: 
            self.screen.blit(pg.transform.rotate(self.pacManImages[gameStateService.counter // 9],90), (self.xPos,self.yPos))
        elif self.direction == Directions.DOWN: 
            self.screen.blit(pg.transform.rotate(self.pacManImages[gameStateService.counter // 9],-90), (self.xPos,self.yPos)) 
    

    #ghosts doesn't have to be returned as a shallow copy will do, but I will for now
    def checkCollisions(self,curScore, power, powerCount, ghosts: list[Ghost]):
        tile_height = (self.screen.get_height() - 50) // 32 #32 vertical tiles
        tile_width = self.screen.get_width() // 30 #30 horizontal tiles
        if 0 < self.xPos < 870:
            if self.board[self.getPacManCenterY() // tile_height][self.getPacManCenterX() // tile_width] == 1:
                self.board[self.getPacManCenterY() // tile_height][self.getPacManCenterX() // tile_width] = 0 #eat the pellet
                curScore += 10
            if self.board[self.getPacManCenterY() // tile_height][self.getPacManCenterX() // tile_width] == 2:
                self.board[self.getPacManCenterY() // tile_height][self.getPacManCenterX() // tile_width] = 0 #eat the pellet
                curScore += 50
                power = True
                print("Power pellet Eaten")
                powerCount = 0
                for g in ghosts: #maybe not pac man's job to toggle the ghosts, just report if it ate a power pellet
                    g.isEaten = False
        return curScore, power, powerCount 

    ## More likely I want to make a velocity system -> see if position + velocity is valid, then decide to move or not.
    def __updateValidTurns(self):
        self.turnManager.resetTurns()

        self.turnManager.down = False
        self.turnManager.up = False
        self.turnManager.left = False
        self.turnManager.right = False
        tile_height = (self.screen.get_height() - 50) // 32 #32 vertical tiles, leave 50 px for UI elements at bottom (may remove)
        tile_width = self.screen.get_width() // 30 #30 horizontal tiles
        fudgeFactor = 17 
        # check collision based on xPos and yPos of player +/- fudgeFactor 
        if self.xPos //30 < 28 and self.xPos //30 > 0:
            #Can I reverse Direction?
            if self.direction == Directions.RIGHT: # <3 because board values 0,1,2 can be moved into, rest are walls
                if self.board[self.getPacManCenterY() // tile_height][(self.getPacManCenterX() - fudgeFactor) // tile_width] < 3:
                    self.turnManager.left = True
            if self.direction == Directions.LEFT:
                if self.board[self.getPacManCenterY() // tile_height][(self.getPacManCenterX() + fudgeFactor) // tile_width] < 3:
                    self.turnManager.right = True
            if self.direction == Directions.UP:
                if self.board[(self.getPacManCenterY() + fudgeFactor) // tile_height][self.getPacManCenterX() // tile_width] < 3:
                    self.turnManager.down = True
            if self.direction == Directions.DOWN:
                if self.board[(self.getPacManCenterY() - fudgeFactor) // tile_height][self.getPacManCenterX() // tile_width] < 3:
                    self.turnManager.up = True

            #Can I turn up or down?
            if self.direction == Directions.UP or self.direction == Directions.DOWN:
                if(self.isInMiddleOfTileX()): #IF pac man is approximately horiztonatally in middle of tile
                    if self.board[(self.getPacManCenterY() + fudgeFactor) // tile_height][self.getPacManCenterX() // tile_width] < 3:
                        self.turnManager.down = True
                    if self.board[(self.getPacManCenterY() - fudgeFactor) // tile_height][self.getPacManCenterX() // tile_width] < 3:
                        self.turnManager.up = True
                if(self.isInMiddleOfTileY()): #IF pac man is approximately horiztonatally in middle of tile
                    if self.board[self.getPacManCenterY() // tile_height][(self.getPacManCenterX() - tile_width) // tile_width] < 3:
                        self.turnManager.left = True
                    if self.board[self.getPacManCenterY() // tile_height][(self.getPacManCenterX() + tile_width) // tile_width] < 3:
                        self.turnManager.right = True
            #Can I turn left or right?
            if self.direction == Directions.RIGHT or self.direction == Directions.LEFT:
                if(self.isInMiddleOfTileX()): #IF pac man is approximately horiztonatally in middle of tile
                    if self.board[(self.getPacManCenterY() + fudgeFactor) // tile_height][self.getPacManCenterX() // tile_width] < 3:
                        self.turnManager.down = True
                    if self.board[(self.getPacManCenterY() - fudgeFactor) // tile_height][self.getPacManCenterX() // tile_width] < 3:
                        self.turnManager.up = True
                if(self.isInMiddleOfTileY()): #IF pac man is approximately vertically in middle of tile
                    if self.board[self.getPacManCenterY() // tile_height][(self.getPacManCenterX() - fudgeFactor) // tile_width] < 3:
                        self.turnManager.left = True
                    if self.board[self.getPacManCenterY() // tile_height][(self.getPacManCenterX() + fudgeFactor) // tile_width] < 3:
                        self.turnManager.right = True
        else: #This is for wrapping around the board horizontally. If you want to wrap vertically, this code must change
            self.turnManager.right = True
            self.turnManager.left = True
        #print(f"right:{self.turnManager.right} left:{self.turnManager.left} up:{self.turnManager.up} down:{self.turnManager.down}")
    
    def movePacMan(self):
        if self.xPos > 900: #wrap pac man if he moves off screen, magic numbers are for visuals
            self.xPos = -47
        elif self.xPos < -50:
            self.xPos = 897
        self.__updateValidTurns()
        if self.direction == Directions.RIGHT and self.turnManager.right:
            self.xPos += self.curVelocity
        elif self.direction == Directions.LEFT and self.turnManager.left:
            self.xPos -= self.curVelocity
        elif self.direction == Directions.UP and self.turnManager.up:
            self.yPos -= self.curVelocity
        elif self.direction == Directions.DOWN and self.turnManager.down:
            self.yPos += self.curVelocity
            
