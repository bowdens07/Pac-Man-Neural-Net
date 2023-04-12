#this class relies on a lot of globals. Consider some services to maybe clean stuff up
from abc import ABC, abstractmethod
import math
import pygame as pg
from GameStateService import GameStateService
from direction import Directions
from graphics import convertPositionToScreenCords, getTileHeight, getTileWidth
from utilities.PathingNode import PathingNode, PathingNodes
from utilities.PriorityQueue import PriorityQueue

class Ghost:
    def __init__(ABC, gameStateService: GameStateService, screen: pg.Surface, board:list[list[int]], xPos:int, yPos:int):
        ABC.gameStateService = gameStateService
        ABC.screen = screen
        ABC.board = board
        ABC.xPos = xPos
        ABC.yPos = yPos
        ABC.target = (450,450)
        ABC.speed = 2
        ABC.image = ABC._getGhostImage()
        ABC.direction = Directions.RIGHT
        ABC.dirRequest = Directions.RIGHT
        ABC.isDead = False
        ABC.isEaten = False
        ABC.turns, ABC.isInBox = ABC.checkCollision()
        ABC.vulnerableGhostImage = pg.transform.scale(pg.image.load(f'assets/VulnerableGhost.png'),(45,45))
        ABC.deadGhostImage = pg.transform.scale(pg.image.load(f'assets/DeadEyesRight.png'),(45,45))
        ABC.isLeavingBox = False
        #This is the last pathing node the ghost collided with - we use it to A* only once per node collision
        ABC.lastPathingNodePosition = (0,0)
        ABC.CurrentPath: list[PathingNode] = []

    @abstractmethod
    def _getGhostImage(ABC) -> pg.Surface:
        pass

    def getCenterX(ABC):
        return ABC.xPos + 22
    def getCenterY(ABC):
        return ABC.yPos + 22

    def setNewBoard(ABC, board:list[list[int]]): #necessary evil, board must be reset on game reset
        ABC.board = board


    def draw(ABC):
        if (not ABC.gameStateService.powerPellet and not ABC.isDead) or (ABC.isEaten and ABC.gameStateService.powerPellet and not ABC.isDead): #really gross
            ABC.screen.blit(ABC.image, (ABC.xPos, ABC.yPos))
        elif ABC.gameStateService.powerPellet and not ABC.isDead and not ABC.isEaten:
            ABC.screen.blit(ABC.vulnerableGhostImage, (ABC.xPos, ABC.yPos))
        else:
            ABC.screen.blit(ABC.deadGhostImage, (ABC.xPos, ABC.yPos))
        ABC.hitBox = pg.rect.Rect((ABC.getCenterX() - 18, ABC.getCenterY() - 18), (36,36)) ## fudge this for more fair hitboxes 

    def updateSpeed(ABC):
        if ABC.isDead:
            ABC.speed = 4
        elif ABC.gameStateService.powerPellet and not ABC.isEaten:
            ABC.speed = 1
        else:
            ABC.speed = 2 

    def getCurrentTile(ABC):
        col = ABC.getCenterX() // getTileWidth(ABC.screen)
        row = ABC.getCenterY() // getTileHeight(ABC.screen)
        return (row,col)        
    
    def isOnCenterOfTile(ABC):
        currentTile = ABC.getCurrentTile()
        (tileX, tileY) = convertPositionToScreenCords(currentTile)
        return abs(tileX - ABC.getCenterX()) == 0 and abs(tileY - ABC.getCenterY()) == 0


    def isOnPathingNode(ABC, pathingNodes: PathingNodes):
        currentTile = ABC.getCurrentTile()
        if currentTile in pathingNodes.nodeDict.keys():
            ABC.lastPathingNodePosition = currentTile
            return True
        return False
    

    def getHeuristicPlusPathCost(pathingNode:PathingNode, costSoFar:int,pacManPosiiton:tuple[int,int]) -> int:
        return costSoFar + pathingNode.getDistanceFromPosition(pacManPosiiton)

    def snapToCenterOfTile(ABC, target: tuple[int,int]):
        (xPos, yPos) = convertPositionToScreenCords(target)
        ABC.xPos = xPos - 22
        ABC.yPos = yPos - 22

    #This method relies on PacMan being inside the PathingNodes Neighbors, if not, we'll search the whole space and probably crash
    #Will only assign a target if Ghost is on a PathingNode and it doesn't have a path or it's on a new pathing node
    def getAStarTarget(ABC, pacManPosition:tuple[int,int], pathingNodes:PathingNodes) -> tuple[bool, list[PathingNode]]:
        hasGeneratedNewPath = False
        if ABC.isOnPathingNode(pathingNodes) and ABC.isOnCenterOfTile() and (len(ABC.CurrentPath) == 0 or ABC.CurrentPath[0].position != ABC.getCurrentTile()):
            ABC.snapToCenterOfTile(ABC.getCurrentTile())
            frontier = PriorityQueue()
            start = pathingNodes.nodeDict[ABC.getCurrentTile()]
            frontier.put(start,0)
            came_from: dict[PathingNode,PathingNode] = {}
            cost_to_reach: dict[PathingNode,int] = {}

            came_from[start] = None
            cost_to_reach[start] = 0

            while not frontier.empty():
                currentNode = frontier.get()
                if currentNode.neighborsPacMan[0]:
                    break

                for neighbor in currentNode.neighbors:
                    newCost = cost_to_reach[currentNode] + neighbor[0].getDistanceFromPosition(currentNode.position)
                    if neighbor[0] not in cost_to_reach.keys() or newCost < cost_to_reach[neighbor[0]]:
                        cost_to_reach[neighbor[0]] = newCost
                        priority = newCost + Ghost.__distanceToTargetHeuristic(neighbor[0].position, pacManPosition)
                        frontier.put(neighbor[0],priority)
                        came_from[neighbor[0]] = currentNode

            revPath = [currentNode]
            parent = came_from[currentNode]
            while parent != None:
                revPath.append(parent)
                parent = came_from[parent]
            path = []
            while len(revPath) > 0:
                path.append(revPath.pop())
            ABC.CurrentPath = path
            hasGeneratedNewPath = True
            return (hasGeneratedNewPath,path)
        else:
            return (hasGeneratedNewPath,ABC.CurrentPath)



            

    def __distanceToTargetHeuristic(position1:tuple[int,int],position2:tuple[int,int]):
        ##TODO: more expensive than manhattan distance, and I think it would work
        return math.sqrt(((position1[0] - position2[0]) **2) + ((position1[1] - position2[1]) ** 2))

    def checkCollision(ABC): #returns valid turns and if ghost is in the box -> pretty gross code todo clean up 
        ABC.isInBox = False
        tileHeight = getTileHeight(ABC.screen)
        tileWidth = getTileWidth(ABC.screen)
        fudgeFactor = 15
        ABC.turns = [False,False,False,False]
        if 0 < ABC.getCenterX() // 30 < 29:
            if ABC.board[(ABC.getCenterY() - fudgeFactor) // tileHeight][ABC.getCenterX() // tileWidth] == 9: # checking for 9 to allow ghosts to move through gates
                ABC.turns[2] = True
            if ABC.board[ABC.getCenterY() // tileHeight][(ABC.getCenterX() - fudgeFactor) // tileWidth] < 3 \
                    or (ABC.board[ABC.getCenterY() // tileHeight][(ABC.getCenterX() - fudgeFactor) // tileWidth] == 9 and (
                    ABC.isInBox or ABC.isDead)):
                ABC.turns[1] = True
            if ABC.board[ABC.getCenterY() // tileHeight][(ABC.getCenterX() + fudgeFactor) // tileWidth] < 3 \
                    or (ABC.board[ABC.getCenterY() // tileHeight][(ABC.getCenterX() + fudgeFactor) // tileWidth] == 9 and (
                    ABC.isInBox or ABC.isDead)):
                ABC.turns[0] = True
            if ABC.board[(ABC.getCenterY() + fudgeFactor) // tileHeight][ABC.getCenterX() // tileWidth] < 3 \
                    or (ABC.board[(ABC.getCenterY() + fudgeFactor) // tileHeight][ABC.getCenterX() // tileWidth] == 9 and (
                    ABC.isInBox or ABC.isDead)):
                ABC.turns[3] = True
            if ABC.board[(ABC.getCenterY() - fudgeFactor) // tileHeight][ABC.getCenterX() // tileWidth] < 3 \
                    or (ABC.board[(ABC.getCenterY() - fudgeFactor) // tileHeight][ABC.getCenterX() // tileWidth] == 9 and (
                    ABC.isInBox or ABC.isDead)):
                ABC.turns[2] = True

            if ABC.direction == 2 or ABC.direction == 3:
                if 12 <= ABC.getCenterX() % tileWidth <= 18:
                    if ABC.board[(ABC.getCenterY() + fudgeFactor) // tileHeight][ABC.getCenterX() // tileWidth] < 3 \
                            or (ABC.board[(ABC.getCenterY() + fudgeFactor) // tileHeight][ABC.getCenterX() // tileWidth] == 9 and (
                            ABC.isInBox or ABC.isDead)):
                        ABC.turns[3] = True
                    if ABC.board[(ABC.getCenterY() - fudgeFactor) // tileHeight][ABC.getCenterX() // tileWidth] < 3 \
                            or (ABC.board[(ABC.getCenterY() - fudgeFactor) // tileHeight][ABC.getCenterX() // tileWidth] == 9 and (
                            ABC.isInBox or ABC.isDead)):
                        ABC.turns[2] = True
                if 12 <= ABC.getCenterY() % tileHeight <= 18:
                    if ABC.board[ABC.getCenterY() // tileHeight][(ABC.getCenterX() - tileWidth) // tileWidth] < 3 \
                            or (ABC.board[ABC.getCenterY() // tileHeight][(ABC.getCenterX() - tileWidth) // tileWidth] == 9 and (
                            ABC.isInBox or ABC.isDead)):
                        ABC.turns[1] = True
                    if ABC.board[ABC.getCenterY() // tileHeight][(ABC.getCenterX() + tileWidth) // tileWidth] < 3 \
                            or (ABC.board[ABC.getCenterY() // tileHeight][(ABC.getCenterX() + tileWidth) // tileWidth] == 9 and (
                            ABC.isInBox or ABC.isDead)):
                        ABC.turns[0] = True

            if ABC.direction == 0 or ABC.direction == 1:
                if 12 <= ABC.getCenterX() % tileWidth <= 18:
                    if ABC.board[(ABC.getCenterY() + fudgeFactor) // tileHeight][ABC.getCenterX() // tileWidth] < 3 \
                            or (ABC.board[(ABC.getCenterY() + fudgeFactor) // tileHeight][ABC.getCenterX() // tileWidth] == 9 and (
                            ABC.isInBox or ABC.isDead)):
                        ABC.turns[3] = True
                    if ABC.board[(ABC.getCenterY() - fudgeFactor) // tileHeight][ABC.getCenterX() // tileWidth] < 3 \
                            or (ABC.board[(ABC.getCenterY() - fudgeFactor) // tileHeight][ABC.getCenterX() // tileWidth] == 9 and (
                            ABC.isInBox or ABC.isDead)):
                        ABC.turns[2] = True
                if 12 <= ABC.getCenterY() % tileHeight <= 18:
                    if ABC.board[ABC.getCenterY() // tileHeight][(ABC.getCenterX() - fudgeFactor) // tileWidth] < 3 \
                            or (ABC.board[ABC.getCenterY() // tileHeight][(ABC.getCenterX() - fudgeFactor) // tileWidth] == 9 and (
                            ABC.isInBox or ABC.isDead)):
                        ABC.turns[1] = True
                    if ABC.board[ABC.getCenterY() // tileHeight][(ABC.getCenterX() + fudgeFactor) // tileWidth] < 3 \
                            or (ABC.board[ABC.getCenterY() // tileHeight][(ABC.getCenterX() + fudgeFactor) // tileWidth] == 9 and (
                            ABC.isInBox or ABC.isDead)):
                        ABC.turns[0] = True
        else:
            ABC.turns[0] = True
            ABC.turns[1] = True
        if 350 < ABC.xPos < 550 and 370 < ABC.yPos < 480:
            ABC.isInBox = True
        else:
            ABC.isInBox = False
        return ABC.turns, ABC.isInBox

    @abstractmethod
    def moveGhost(ABC):
        pass

    def moveSue(ABC): #TODO bugged - if the ghosts move off screen they get stuck
        if ABC.direction == 0:
            if ABC.target[0] > ABC.xPos and ABC.turns[0]:
                ABC.xPos += ABC.speed
            elif not ABC.turns[0]:
                if ABC.target[1] > ABC.yPos and ABC.turns[3]:
                    ABC.direction = 3
                    ABC.yPos += ABC.speed
                elif ABC.target[1] < ABC.yPos and ABC.turns[2]:
                    ABC.direction = 2
                    ABC.yPos -= ABC.speed
                elif ABC.target[0] < ABC.xPos and ABC.turns[1]:
                    ABC.direction = 1
                    ABC.xPos -= ABC.speed
                elif ABC.turns[3]:
                    ABC.direction = 3
                    ABC.yPos += ABC.speed
                elif ABC.turns[2]:
                    ABC.direction = 2
                    ABC.yPos -= ABC.speed
                elif ABC.turns[1]:
                    ABC.direction = 1
                    ABC.xPos -= ABC.speed
            elif ABC.turns[0]:
                if ABC.target[1] > ABC.yPos and ABC.turns[3]:
                    ABC.direction = 3
                    ABC.yPos += ABC.speed
                if ABC.target[1] < ABC.yPos and ABC.turns[2]:
                    ABC.direction = 2
                    ABC.yPos -= ABC.speed
                else:
                    ABC.xPos += ABC.speed
        elif ABC.direction == 1:
            if ABC.target[1] > ABC.yPos and ABC.turns[3]:
                ABC.direction = 3
            elif ABC.target[0] < ABC.xPos and ABC.turns[1]:
                ABC.xPos -= ABC.speed
            elif not ABC.turns[1]:
                if ABC.target[1] > ABC.yPos and ABC.turns[3]:
                    ABC.direction = 3
                    ABC.yPos += ABC.speed
                elif ABC.target[1] < ABC.yPos and ABC.turns[2]:
                    ABC.direction = 2
                    ABC.yPos -= ABC.speed
                elif ABC.target[0] > ABC.xPos and ABC.turns[0]:
                    ABC.direction = 0
                    ABC.xPos += ABC.speed
                elif ABC.turns[3]:
                    ABC.direction = 3
                    ABC.yPos += ABC.speed
                elif ABC.turns[2]:
                    ABC.direction = 2
                    ABC.yPos -= ABC.speed
                elif ABC.turns[0]:
                    ABC.direction = 0
                    ABC.xPos += ABC.speed
            elif ABC.turns[1]:
                if ABC.target[1] > ABC.yPos and ABC.turns[3]:
                    ABC.direction = 3
                    ABC.yPos += ABC.speed
                if ABC.target[1] < ABC.yPos and ABC.turns[2]:
                    ABC.direction = 2
                    ABC.yPos -= ABC.speed
                else:
                    ABC.xPos -= ABC.speed
        elif ABC.direction == 2:
            if ABC.target[0] < ABC.xPos and ABC.turns[1]:
                ABC.direction = 1
                ABC.xPos -= ABC.speed
            elif ABC.target[1] < ABC.yPos and ABC.turns[2]:
                ABC.direction = 2
                ABC.yPos -= ABC.speed
            elif not ABC.turns[2]:
                if ABC.target[0] > ABC.xPos and ABC.turns[0]:
                    ABC.direction = 0
                    ABC.xPos += ABC.speed
                elif ABC.target[0] < ABC.xPos and ABC.turns[1]:
                    ABC.direction = 1
                    ABC.xPos -= ABC.speed
                elif ABC.target[1] > ABC.yPos and ABC.turns[3]:
                    ABC.direction = 3
                    ABC.yPos += ABC.speed
                elif ABC.turns[1]:
                    ABC.direction = 1
                    ABC.xPos -= ABC.speed
                elif ABC.turns[3]:
                    ABC.direction = 3
                    ABC.yPos += ABC.speed
                elif ABC.turns[0]:
                    ABC.direction = 0
                    ABC.xPos += ABC.speed
            elif ABC.turns[2]:
                if ABC.target[0] > ABC.xPos and ABC.turns[0]:
                    ABC.direction = 0
                    ABC.xPos += ABC.speed
                elif ABC.target[0] < ABC.xPos and ABC.turns[1]:
                    ABC.direction = 1
                    ABC.xPos -= ABC.speed
                else:
                    ABC.yPos -= ABC.speed
        elif ABC.direction == 3:
            if ABC.target[1] > ABC.yPos and ABC.turns[3]:
                ABC.yPos += ABC.speed
            elif not ABC.turns[3]:
                if ABC.target[0] > ABC.xPos and ABC.turns[0]:
                    ABC.direction = 0
                    ABC.xPos += ABC.speed
                elif ABC.target[0] < ABC.xPos and ABC.turns[1]:
                    ABC.direction = 1
                    ABC.xPos -= ABC.speed
                elif ABC.target[1] < ABC.yPos and ABC.turns[2]:
                    ABC.direction = 2
                    ABC.yPos -= ABC.speed
                elif ABC.turns[2]:
                    ABC.direction = 2
                    ABC.yPos -= ABC.speed
                elif ABC.turns[1]:
                    ABC.direction = 1
                    ABC.xPos -= ABC.speed
                elif ABC.turns[0]:
                    ABC.direction = 0
                    ABC.xPos += ABC.speed
            elif ABC.turns[3]:
                if ABC.target[0] > ABC.xPos and ABC.turns[0]:
                    ABC.direction = 0
                    ABC.xPos += ABC.speed
                elif ABC.target[0] < ABC.xPos and ABC.turns[1]:
                    ABC.direction = 1
                    ABC.xPos -= ABC.speed
                else:
                    ABC.yPos += ABC.speed
        if ABC.xPos < -30:
            ABC.xPos = 900
        elif ABC.xPos > 900:
            ABC.xPos - 30
        return ABC.xPos, ABC.yPos, ABC.direction    
    
    def _getOppositeSideTarget(ABC, pacMan_x,pacMan_y):
        if pacMan_x < 450: #basically move to the opposite side of the board pac-man is on if powerup
            runawayX = 900
        else:
            runawayX = 0
        if pacMan_y < 450:
            runawayY = 900
        else:
            runawayY = 0
        return (runawayX, runawayY)

    @abstractmethod
    def getRunAwayTarget(ABC, pacMan_x,pacMan_y):
        pass

    def setNewTarget(ABC,pacMan_x,pacMan_y):
        if ABC.isDead: #if dead, go to box
            ghostTarget = (380, 450) #inside the revive zone
        elif ABC.isLeavingBox:
                if not ABC.gameStateService.isInTheBox(ABC.getCenterX(), ABC.getCenterY()):
                    ABC.isLeavingBox = False
                    ghostTarget = (pacMan_x, pacMan_y)
                else:
                    ghostTarget = (400,100)
        elif ABC.gameStateService.isInReviveZone(ABC.getCenterX(), ABC.getCenterY()): #if not dead leave box
                ABC.isLeavingBox = True
                ghostTarget = (400,100)
                print("InBox, trying to leave")
        elif ABC.gameStateService.powerPellet: 
            if not ABC.isEaten: #If not eaten run
                ghostTarget = ABC.getRunAwayTarget(pacMan_x,pacMan_y)
            else: #If eaten and not dead, and not in box, must have respawend, resume chasing
                ghostTarget = (pacMan_x, pacMan_y)     
        else: #Not dead, not in box, now power pellet
            ghostTarget = (pacMan_x, pacMan_y)
        ABC.target = ghostTarget