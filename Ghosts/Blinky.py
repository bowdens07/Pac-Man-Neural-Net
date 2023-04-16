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
        self.moveToAStarTarget(target, pathingNodes)


