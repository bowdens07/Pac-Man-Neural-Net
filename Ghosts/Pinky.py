import pygame as pg
from Ghosts.Ghost import Ghost
from direction import Directions
from utilities.PathingNode import PathingNodes

class Pinky(Ghost):

    
    def _getGhostImage(ABC):
        return pg.transform.scale(pg.image.load(f'assets/Pinky.png'),(45,45))

    def _getScatterTarget(ABC) -> tuple[int,int]:
        return (2,3)

    def moveGhost(self, target: tuple[int,int], pathingNodes: PathingNodes, board: list[list[int]]):
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