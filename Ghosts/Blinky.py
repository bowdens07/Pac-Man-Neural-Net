import pygame as pg
from Ghosts.Ghost import Ghost
from PacMan import PacMan
from direction import Directions
from graphics import convertPositionToScreenCords
from utilities.PathingNode import PathingNodes

class Blinky(Ghost):
    
    def _getGhostImage(self):
        return pg.transform.scale(pg.image.load(f'assets/Blinky.png'),(45,45))

    def _getScatterTarget(ABC) -> tuple[int,int]:
        return (2,25)

    def moveGhost(self, pacMan: PacMan, pathingNodes: PathingNodes, board: list[list[int]]):
        self.moveGhostToTarget(pacMan.getCurrentTile(), pathingNodes, board)


