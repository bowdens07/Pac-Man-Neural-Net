#this class relies on a lot of globals. Consider some services to maybe clean stuff up
from abc import ABC, abstractmethod
import math
import pygame as pg
from GameStateService import GameStateService
from direction import Directions
from graphics import convertPositionToScreenCords, getTileHeight, getTileWidth
from utilities.PathingNode import PathingNode, PathingNodes
from utilities.PriorityQueue import PriorityQueue
import random

class Ghost:
    def __init__(ABC, gameStateService: GameStateService, screen: pg.Surface, board:list[list[int]], xPos:int, yPos:int):
        ABC.gameStateService = gameStateService
        ABC.screen = screen
        ABC.board = board
        ABC.xPos = xPos
        ABC.yPos = yPos
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
        ABC.CurrentTarget: tuple[int,int] = None
        ABC.hasGeneratedNewPath = False

    @abstractmethod
    def _getGhostImage(ABC) -> pg.Surface:
        pass

    #Scatter target must be a position with a pathingNode on it
    @abstractmethod
    def _getScatterTarget(ABC) -> tuple[int,int]:
        pass

    @abstractmethod
    def moveGhost(ABC, pacManPosition: tuple[int,int], pathingNodes: PathingNodes, board: list[list[int]]):
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
            ABC.speed = 3
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
        return abs(tileX - ABC.getCenterX()) < 2 and abs(tileY - ABC.getCenterY()) < 2

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
    #Make sure to pass a deep copy of pathingNodes, this algorithm will edit the neighbors of the nodes
    def getAStarTarget(ABC, pacManPosition:tuple[int,int], pathingNodes:PathingNodes) -> tuple[bool, list[PathingNode]]:
        hasGeneratedNewPath = False
        if ABC.isOnPathingNode(pathingNodes) and ABC.isOnCenterOfTile() and (len(ABC.CurrentPath) == 0 or ABC.CurrentPath[0].position != ABC.getCurrentTile()):
            ABC.snapToCenterOfTile(ABC.getCurrentTile())
            frontier = PriorityQueue()
            start = pathingNodes.nodeDict[ABC.getCurrentTile()]

            for neighbor in start.neighbors: #Do not allow the ghost to 180, remove the connection to any neighbor that causes it, unless it's trying to leave the box
                if(not ABC.isLeavingBox):
                    if Directions.reverseDirection(ABC.direction) == neighbor[1]:
                        start.neighbors.remove(neighbor)

            frontier.put(start,0)
            came_from: dict[PathingNode,PathingNode] = {}
            cost_to_reach: dict[PathingNode,int] = {}

            came_from[start] = None
            cost_to_reach[start] = 0

            while not frontier.empty():
                currentNode = frontier.get()
                if currentNode.neighborsTarget[0]:
                    break

                for neighbor in currentNode.neighbors:
                    newCost = cost_to_reach[currentNode] + neighbor[0].getDistanceFromPosition(currentNode.position)
                    if neighbor[0] not in cost_to_reach.keys() or newCost < cost_to_reach[neighbor[0]]:
                        cost_to_reach[neighbor[0]] = newCost
                        priority = newCost + Ghost._distanceToTargetHeuristic(neighbor[0].position, pacManPosition)
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
            ABC.hasGeneratedNewPath = hasGeneratedNewPath
            ABC.CurrentTarget = pacManPosition
            return (hasGeneratedNewPath,path)
        else:
            ABC.hasGeneratedNewPath = hasGeneratedNewPath
            return (hasGeneratedNewPath,ABC.CurrentPath)

    def flee(ABC, pathingNodes:PathingNodes):
            hasGeneratedNewPath = False
            if ABC.isOnPathingNode(pathingNodes) and ABC.isOnCenterOfTile()and (len(ABC.CurrentPath) == 0 or ABC.CurrentPath[0].position != ABC.getCurrentTile()):
                ABC.snapToCenterOfTile(ABC.getCurrentTile())
                start = pathingNodes.nodeDict[ABC.getCurrentTile()]
                neighbors = start.neighbors
                for neighbor in neighbors:
                    if(not ABC.isLeavingBox):
                        if neighbor[1] == Directions.reverseDirection(ABC.direction): #prevent ghosts from doing a 180
                            neighbors.remove(neighbor)
                target = neighbors[random.randrange(len(neighbors))][0] #pick a random neighbor that isn't a 180
                path = [start, target]
                ABC.CurrentPath = path
                hasGeneratedNewPath = True
                ABC.CurrentTarget = target.position
            return (hasGeneratedNewPath,ABC.CurrentPath)

    def moveToAStarTarget(ABC, target: tuple[int,int], pathingNodes: PathingNodes, fleeing:bool):
        (validDirections, isInBox) = ABC.checkCollision()
        if not any(validDirections): #The ghost is probably stuck from going too fast - Just snap it to the current tile and check collisions again
            (validDirections, isInBox) = ABC.snapToCenterOfTile(ABC.getCurrentTile())

        if(fleeing):
            (hasGeneratedNewPath, path) = ABC.flee(pathingNodes)
        else:
            (hasGeneratedNewPath, path) = ABC.getAStarTarget(target,pathingNodes)
        if len(path) > 0:
            #Get the direction the ghost wants to go
            SourceNode = path[0]
            if hasGeneratedNewPath:
                if SourceNode.neighborsTarget[0]: #If The Source node neighbors pac man, just go towards Pac-Man, unless this causes a direction reversal
                    if(Directions.reverseDirection(ABC.direction) != SourceNode.neighborsTarget[1]): #Does not cause a direction reversal
                        if(validDirections[SourceNode.neighborsTarget[1].value]):
                            ABC.dirRequest = SourceNode.neighborsTarget[1]
                        else: #If the ghost is on its target node just go the first valid direction that isn't a turn around
                            for i in range(len(validDirections)): #todo, get rid of the array of bools
                                if validDirections[i] and Directions(i) != Directions.reverseDirection(ABC.direction):
                                    ABC.dirRequest = Directions(i)
                    else: #Would cause a direction reversal, pick a random available direction that isn't reversing
                        SourceNodeNeighbors = SourceNode.neighbors
                        for neighbor in SourceNodeNeighbors:
                            if neighbor[1] == Directions.reverseDirection(ABC.direction): #prevent ghosts from doing a 180
                                SourceNodeNeighbors.remove(neighbor)
                        ABC.dirRequest = SourceNodeNeighbors[random.randrange(len(SourceNodeNeighbors))][1] #pick a random neighbor that isn't a 180                        
                else:
                    ABC.dirRequest = SourceNode.getDirectionToNeighbor(path[1])
            #Get the directions the ghost can go
            #The enum Directions corresponds to the list of bools
            if validDirections[ABC.dirRequest.value]:
                ABC.direction= ABC.dirRequest
        else:
            print("Warning: Ghost doesn't have a path")

        ABC.__moveGhostforward(validDirections)
        #Wrap the ghosts through the tunnel
        if ABC.xPos < -30:
            ABC.xPos = 900
        elif ABC.xPos > 900:
            ABC.xPos = -30

    def turnGhostAround(ABC): #180 the ghost and set their path to nothing, used to start fleeing
        ABC.direction = Directions.reverseDirection(ABC.direction)
        ABC.dirRequest = ABC.direction
        ABC.CurrentPath = []
        ABC.CurrentTarget = None

    def __moveGhostforward(ABC, validDirections:list[bool]):
        if ABC.direction == Directions.RIGHT and validDirections[Directions.RIGHT.value]:
            ABC.xPos += ABC.speed
        elif ABC.direction == Directions.LEFT and validDirections[Directions.LEFT.value]:
            ABC.xPos -= ABC.speed
        elif ABC.direction == Directions.UP and validDirections[Directions.UP.value]:
            ABC.yPos -= ABC.speed
        elif ABC.direction == Directions.DOWN and validDirections[Directions.DOWN.value]:
            ABC.yPos += ABC.speed
            
    def _distanceToTargetHeuristic(position1:tuple[int,int],position2:tuple[int,int]):
        ##TODO: more expensive than manhattan distance, and I think it would work
        return math.sqrt(((position1[0] - position2[0]) **2) + ((position1[1] - position2[1]) ** 2))

    def moveGhostToTarget(self, target: tuple[int,int], pathingNodes: PathingNodes, board: list[list[int]]):
            isFleeing = False
            ghostTarget = target if not self.gameStateService.isScatterMode else self._getScatterTarget()
            if self.isDead: #if dead, go to box
                ghostTarget = (16, 12) #The node in the revive zone
            elif self.isLeavingBox:
                    if not self.gameStateService.isInTheBox(self.getCenterX(), self.getCenterY()):
                        self.isLeavingBox = False
                        ghostTarget = target
                    else:
                        ghostTarget = (12,14)
            elif self.gameStateService.isInReviveZone(self.getCenterX(), self.getCenterY()): #if not dead and in the box start trying to leave box
                    self.isLeavingBox = True
                    ghostTarget = (12,14)
                    print("InBox, trying to leave")
            elif self.gameStateService.powerPellet: 
                if not self.isEaten: #If not eaten run
                    isFleeing = True
                else: #If eaten and not dead, and not in box, must have respawend, resume chasing - this is only here for clarity
                    ghostTarget = target
            pathingNodesWithTarget = pathingNodes.getCopyWithTarget(ghostTarget, board)
            self.moveToAStarTarget(ghostTarget, pathingNodesWithTarget, isFleeing)

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
