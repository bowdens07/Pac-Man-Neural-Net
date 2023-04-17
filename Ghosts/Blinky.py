import pygame as pg
from Ghosts.Ghost import Ghost
from direction import Directions
from graphics import convertPositionToScreenCords
from utilities.PathingNode import PathingNodes

class Blinky(Ghost):
    
    def _getGhostImage(self):
        return pg.transform.scale(pg.image.load(f'assets/Blinky.png'),(45,45))

    def moveGhost(self, target: tuple[int,int], pathingNodes: PathingNodes, board: list[list[int]]):
        self.moveToAStarTarget(target, pathingNodes, False)


