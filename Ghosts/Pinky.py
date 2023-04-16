import pygame as pg
from Ghosts.Ghost import Ghost
from direction import Directions
from utilities.PathingNode import PathingNodes

class Pinky(Ghost):

    def getRunAwayTarget(self,pacMan_x,pacMan_y):
        return (pacMan_x,self._getOppositeSideTarget(pacMan_x,pacMan_y)[1])
    
    def _getGhostImage(ABC):
        return pg.transform.scale(pg.image.load(f'assets/Pinky.png'),(45,45))
    
    def moveGhost(self, target: tuple[int,int], pathingNodes: PathingNodes):
        self.moveToAStarTarget(target, pathingNodes)