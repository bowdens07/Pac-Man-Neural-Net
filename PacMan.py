import math
import pygame as pg
from GameStateService import GameStateService
from board import findNearestPellet, getValidAdjacentPositions, isAWall, isInBox, isValidPosition

from direction import Directions
from utilities.PathingNode import PathingNode, PathingNodes
from utilities.PriorityQueue import PriorityQueue
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
        self.lastPathingNodePosition = (0,0)
        self.curVelocity = 2
        self.gameStateService = gameStateService
        self.screen = screen
        self.board = board
        self.turnManager = TurnManager()
        self.hitbox =  (self.getCenterX(), self.getCenterY(), 20, 2)

    def setNewBoard(self, board:list[list[int]]):
        self.board = board

    def getCenterX(self):
        return self.xPos + 22

    def getCenterY(self):
        return self.yPos + 23
    
    def isInMiddleOfTileX(self):
        tile_width = self.screen.get_width() // 30 #30 horizontal tiles
        if 12 <= self.getCenterX() % tile_width <= 18:
            return True
        return False

    def isInMiddleOfTileY(self):
        tile_height = (self.screen.get_height() - 50) // 32 #32 vertical tiles
        if 12 <= self.getCenterY() % tile_height <= 18:
            return True
        return False

    def getCurrentTile(self) -> tuple[int,int]:
        tileHeight = (self.screen.get_height() - 50) // 32
        tileWidth = self.screen.get_width() // 30
        col = self.getCenterX() // tileWidth
        row = self.getCenterY() // tileHeight
        return (row,col)
    
    #Gets four tiles ahead of pac-Man's current direction. If a wall is four tiles out, gets the next nearest position, stopping on pacMan - used for Pinky chasing
    def getXTilesAhead(self, tilesAhead:int) -> tuple[int,int]:
        (pacManRow, pacManColumn) = self.getCurrentTile()
        if self.direction == Directions.RIGHT:
            pacManColumn += tilesAhead
            while(not isValidPosition((pacManRow,pacManColumn)) or isAWall(((pacManRow,pacManColumn)))):
                pacManColumn -= 1
        if self.direction == Directions.LEFT:
            pacManColumn -= tilesAhead
            while(not isValidPosition((pacManRow,pacManColumn)) or isAWall(((pacManRow,pacManColumn)))):
                pacManColumn += 1
        if self.direction == Directions.UP:
            pacManRow -= tilesAhead
            while(not isValidPosition((pacManRow,pacManColumn)) or isAWall(((pacManRow,pacManColumn)))):
                pacManRow += 1
        if self.direction == Directions.DOWN:
            pacManRow += tilesAhead
            while(not isValidPosition((pacManRow,pacManColumn)) or isAWall(((pacManRow,pacManColumn)))):
                pacManRow -= 1

        if(isInBox((pacManRow, pacManColumn))): #If pac man is aiming into the box, just use Pac Man's position
            return self.getCurrentTile()
        
        return (pacManRow,pacManColumn)
           

    def draw(self,gameStateService: GameStateService, drawGraphics:bool):
        self.hitbox = pg.draw.circle(self.screen, 'black', (self.getCenterX(), self.getCenterY()), 20, 2)
        if drawGraphics:
            if self.direction == Directions.RIGHT: 
                self.screen.blit(self.pacManImages[gameStateService.counter // 9], (self.xPos,self.yPos))
            elif self.direction == Directions.LEFT: 
                self.screen.blit(pg.transform.flip(self.pacManImages[gameStateService.counter // 9],True,False), (self.xPos,self.yPos))
            elif self.direction == Directions.UP: 
                self.screen.blit(pg.transform.rotate(self.pacManImages[gameStateService.counter // 9],90), (self.xPos,self.yPos))
            elif self.direction == Directions.DOWN: 
                self.screen.blit(pg.transform.rotate(self.pacManImages[gameStateService.counter // 9],-90), (self.xPos,self.yPos)) 
        

    def checkCollisions(self,curScore, power, powerCount):
        tilePosition = self.getCurrentTile()
        if tilePosition[0] < 32 and tilePosition[1] < 30:
            boardContent = self.board[tilePosition[0]][tilePosition[1]]
            if 0 < self.xPos < 870:
                if boardContent == 1:
                    self.board[tilePosition[0]][tilePosition[1]] = 0 #eat the pellet
                    curScore += 10
                    self.gameStateService.pelletCounter = 0
                if boardContent == 2:
                    self.board[tilePosition[0]][tilePosition[1]] = 0 #eat the pellet
                    curScore += 50
                    power = True
                    self.gameStateService.pelletCounter = 0
                    #print("Power pellet Eaten")
                    powerCount = 0
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
                if self.board[self.getCenterY() // tile_height][(self.getCenterX() - fudgeFactor) // tile_width] < 3:
                    self.turnManager.left = True
            if self.direction == Directions.LEFT:
                if self.board[self.getCenterY() // tile_height][(self.getCenterX() + fudgeFactor) // tile_width] < 3:
                    self.turnManager.right = True
            if self.direction == Directions.UP:
                if self.board[(self.getCenterY() + fudgeFactor) // tile_height][self.getCenterX() // tile_width] < 3:
                    self.turnManager.down = True
            if self.direction == Directions.DOWN:
                if self.board[(self.getCenterY() - fudgeFactor) // tile_height][self.getCenterX() // tile_width] < 3:
                    self.turnManager.up = True

            #Can I turn up or down?
            if self.direction == Directions.UP or self.direction == Directions.DOWN:
                if(self.isInMiddleOfTileX()): #IF pac man is approximately horiztonatally in middle of tile
                    if self.board[(self.getCenterY() + fudgeFactor) // tile_height][self.getCenterX() // tile_width] < 3:
                        self.turnManager.down = True
                    if self.board[(self.getCenterY() - fudgeFactor) // tile_height][self.getCenterX() // tile_width] < 3:
                        self.turnManager.up = True
                if(self.isInMiddleOfTileY()): #IF pac man is approximately horiztonatally in middle of tile
                    if self.board[self.getCenterY() // tile_height][(self.getCenterX() - tile_width) // tile_width] < 3:
                        self.turnManager.left = True
                    if self.board[self.getCenterY() // tile_height][(self.getCenterX() + tile_width) // tile_width] < 3:
                        self.turnManager.right = True
            #Can I turn left or right?
            if self.direction == Directions.RIGHT or self.direction == Directions.LEFT:
                if(self.isInMiddleOfTileX()): #IF pac man is approximately horiztonatally in middle of tile
                    if self.board[(self.getCenterY() + fudgeFactor) // tile_height][self.getCenterX() // tile_width] < 3:
                        self.turnManager.down = True
                    if self.board[(self.getCenterY() - fudgeFactor) // tile_height][self.getCenterX() // tile_width] < 3:
                        self.turnManager.up = True
                if(self.isInMiddleOfTileY()): #IF pac man is approximately vertically in middle of tile
                    if self.board[self.getCenterY() // tile_height][(self.getCenterX() - fudgeFactor) // tile_width] < 3:
                        self.turnManager.left = True
                    if self.board[self.getCenterY() // tile_height][(self.getCenterX() + fudgeFactor) // tile_width] < 3:
                        self.turnManager.right = True
        else: #This is for wrapping around the board horizontally. If you want to wrap vertically, this code must change
            self.turnManager.right = True
            self.turnManager.left = True
        #print(f"right:{self.turnManager.right} left:{self.turnManager.left} up:{self.turnManager.up} down:{self.turnManager.down}")

    def trySetDirection(self,direction_request):
        if direction_request == Directions.RIGHT and self.turnManager.right:
            self.direction = direction_request
        if direction_request == Directions.LEFT and self.turnManager.left:
            self.direction = direction_request
        if direction_request == Directions.DOWN and self.turnManager.down:
            self.direction = direction_request
        if direction_request == Directions.UP and self.turnManager.up:
            self.direction = direction_request

    #Right = Forward, Left = turn around, Up = Counter Clockwise, Down = Clockwise
    #This is for the neural network, it makes it easier to reason in relative directions
    def trySetRelativeDirection(self, relative_direction_request):
        absolute_direction = self.__RelativeDirectionToAbsoluteDirection(relative_direction_request)
        self.trySetDirection(absolute_direction)


    def __RelativeDirectionToAbsoluteDirection(self, direction_request):
        absoluteDirection = Directions.RIGHT
        if self.direction == Directions.RIGHT:
            if direction_request == Directions.RIGHT:     
                absoluteDirection = Directions.RIGHT
            elif direction_request == Directions.LEFT:
                absoluteDirection = Directions.LEFT
            elif direction_request == Directions.UP:
                absoluteDirection = Directions.UP           
            elif direction_request == Directions.DOWN:
                absoluteDirection = Directions.DOWN
        if self.direction == Directions.LEFT:
            if direction_request == Directions.RIGHT:     
                absoluteDirection = Directions.LEFT
            elif direction_request == Directions.LEFT:
                absoluteDirection = Directions.RIGHT
            elif direction_request == Directions.UP:
                absoluteDirection = Directions.UP           
            elif direction_request == Directions.DOWN:
                absoluteDirection = Directions.DOWN
        if self.direction == Directions.UP:
            if direction_request == Directions.RIGHT:     
                absoluteDirection = Directions.UP
            elif direction_request == Directions.LEFT:
                absoluteDirection = Directions.DOWN
            elif direction_request == Directions.UP:
                absoluteDirection = Directions.RIGHT           
            elif direction_request == Directions.DOWN:
                absoluteDirection = Directions.LEFT
        if self.direction == Directions.DOWN:
            if direction_request == Directions.RIGHT:     
                absoluteDirection = Directions.DOWN
            elif direction_request == Directions.LEFT:
                absoluteDirection = Directions.UP
            elif direction_request == Directions.UP:
                absoluteDirection = Directions.RIGHT           
            elif direction_request == Directions.DOWN:
                absoluteDirection = Directions.LEFT
        return absoluteDirection      

    def __absoluteDirectionToRelativeDirection(self, absoluteDirection):
        relative_direction = Directions.RIGHT
        if self.direction == Directions.RIGHT:
            if absoluteDirection == Directions.RIGHT:     
                relative_direction = Directions.RIGHT
            elif absoluteDirection == Directions.LEFT:
                relative_direction = Directions.LEFT
            elif absoluteDirection == Directions.UP:
                relative_direction = Directions.UP           
            elif absoluteDirection == Directions.DOWN:
                relative_direction = Directions.DOWN
        if self.direction == Directions.LEFT:
            if absoluteDirection == Directions.RIGHT:     
                relative_direction = Directions.LEFT
            elif absoluteDirection == Directions.LEFT:
                relative_direction = Directions.RIGHT
            elif absoluteDirection == Directions.UP:
                relative_direction = Directions.UP           
            elif absoluteDirection == Directions.DOWN:
                relative_direction = Directions.DOWN
        if self.direction == Directions.UP:
            if absoluteDirection == Directions.RIGHT:     
                relative_direction = Directions.DOWN
            elif absoluteDirection == Directions.LEFT:
                relative_direction = Directions.UP
            elif absoluteDirection == Directions.UP:
                relative_direction = Directions.RIGHT           
            elif absoluteDirection == Directions.DOWN:
                relative_direction = Directions.LEFT
        if self.direction == Directions.DOWN:
            if absoluteDirection == Directions.RIGHT:     
                relative_direction = Directions.UP
            elif absoluteDirection == Directions.LEFT:
                relative_direction = Directions.DOWN
            elif absoluteDirection == Directions.UP:
                relative_direction = Directions.LEFT           
            elif absoluteDirection == Directions.DOWN:
                relative_direction = Directions.RIGHT
        return relative_direction      

    def getRelativeAvailableDirections(self) -> list[int]:
        turnManager = self.turnManager
        if self.direction == Directions.RIGHT:
            return [turnManager.right, turnManager.left, turnManager.up, turnManager.down]
        if self.direction == Directions.LEFT:
            return [turnManager.left, turnManager.right, turnManager.up, turnManager.down]
        if self.direction == Directions.UP:
            return [turnManager.up, turnManager.down, turnManager.right, turnManager.left]
        if self.direction == Directions.DOWN:
            return [turnManager.down, turnManager.up, turnManager.right, turnManager.left]       

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
    
    def getRelativeDirectionToNearestPellet(self) -> Directions:
        targetTile = self.getNearestPellet()
        path = self.getAStarTarget(targetTile)
        if(len(path) > 1):
            direction = self.getDirectionAdjacentToTile(path[1])
            return self.__absoluteDirectionToRelativeDirection(direction)
        else:
            return Directions.RIGHT


    def getDirectionAdjacentToTile(self, tile:tuple[int,int]) -> Directions:
        currentTile = self.getCurrentTile()
        rowDif = currentTile[0] - tile[0]
        colDif = currentTile[1] - tile[1]
        if rowDif > 0:
            return Directions.UP
        elif rowDif < 0:
            return Directions.DOWN
        elif colDif < 0: 
            return Directions.RIGHT
        elif colDif > 0:
            return Directions.LEFT
        else:
            print("getDirectionAdjacentToTile: warning, the tiles are identical")
            return Directions.RIGHT

    def getNearestPellet(self):
        currentTile = self.getCurrentTile()
        if(isValidPosition(currentTile)):
            return findNearestPellet(currentTile, self.board)
        else:
            return findNearestPellet((15,28),self.board)
        
    @staticmethod
    def _distanceToTargetHeuristic(position1:tuple[int,int],position2:tuple[int,int]):
        return math.sqrt(((position1[0] - position2[0]) **2) + ((position1[1] - position2[1]) ** 2))
    
    @staticmethod
    def __getDistanceFromPosition(startPosition:tuple[int,int],targetPosition:tuple[int,int]) -> int:
        verticalDistance = abs(startPosition[0] - targetPosition[0])
        horizontalDistance = abs(startPosition[1] - targetPosition[1])
        return verticalDistance + horizontalDistance

    def getAStarTarget(self, targetPosition:tuple[int,int]) -> tuple[bool, list[PathingNode]]:
        frontier = PriorityQueue()
        start = self.getCurrentTile()
        frontier.put(start,0)
        came_from: dict[tuple[int,int],tuple[int,int]] = {}
        cost_to_reach: dict[tuple[int,int],int] = {}

        came_from[start] = None
        cost_to_reach[start] = 0

        while not frontier.empty():
            currentTile = frontier.get()

            if currentTile == targetPosition:
                break
            #Note this won't wrap around the board, which is okay for now
            tileNeighbors = getValidAdjacentPositions(currentTile)  
            for neighbor in tileNeighbors:
                newCost = cost_to_reach[currentTile] + PacMan.__getDistanceFromPosition(neighbor,currentTile)
                if neighbor not in cost_to_reach.keys() or newCost < cost_to_reach[neighbor]:
                    cost_to_reach[neighbor] = newCost
                    priority = newCost + PacMan._distanceToTargetHeuristic(neighbor, targetPosition)
                    frontier.put(neighbor,priority)
                    came_from[neighbor] = currentTile

        revPath = [currentTile]
        parent = came_from[currentTile]
        while parent != None:
            revPath.append(parent)
            parent = came_from[parent]
        path = []
        while len(revPath) > 0:
            path.append(revPath.pop())
        self.CurrentPath = path
        self.CurrentTarget = targetPosition
        return path      

