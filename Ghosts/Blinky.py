import pygame as pg
from Ghosts.Ghost import Ghost
from direction import Directions
from graphics import convertPositionToScreenCords
from utilities.PathingNode import PathingNodes

class Blinky(Ghost):

    def getRunAwayTarget(self,pacMan_x,pacMan_y):
        return self._getOppositeSideTarget(pacMan_x,pacMan_y)
    
    def _getGhostImage(self):
        return pg.transform.scale(pg.image.load(f'assets/Blinky.png'),(45,45))

    def moveGhost(self, target: tuple[int,int], pathingNodes: PathingNodes):
        (hasGeneratedNewPath, path) = self.getAStarTarget(target,pathingNodes)

        if len(path) > 0:
            #Get the direction the ghost wants to go
            SourceNode = path[0]
            if hasGeneratedNewPath:
                if SourceNode.neighborsPacMan[0]: #If The Source node neighbors pac man, just go towards Pac-Man
                    self.dirRequest = SourceNode.neighborsPacMan[1]
                else:
                    self.dirRequest = SourceNode.getDirectionToNeighbor(path[1])
            #Get the directions the ghost can go
            (validDirections, isInBox) = self.checkCollision()
            #The enum Directions corresponds to the list of bools
            if validDirections[self.dirRequest.value]:
                self.direction= self.dirRequest
        else:
            print("Warning: Blinky doesn't have a path")

        self.__moveGhostforward()
        #Wrap the ghosts through the tunnel
        if self.xPos < -30:
            self.xPos = 900
        elif self.xPos > 900:
            self.xPos - 30

    def __moveGhostforward(self):
        if self.direction == Directions.RIGHT:
            self.xPos += self.speed
        elif self.direction == Directions.LEFT:
            self.xPos -= self.speed
        elif self.direction == Directions.UP:
            self.yPos -= self.speed
        elif self.direction == Directions.DOWN:
            self.yPos += self.speed