import pygame as pg
from Ghosts.Ghost import Ghost
from PacMan import PacMan
from direction import Directions
from utilities.PathingNode import PathingNodes

class Pinky(Ghost):

    def _getGhostImage(ABC):
        return pg.transform.scale(pg.image.load(f'assets/Pinky.png'),(45,45))

    def _getScatterTarget(ABC) -> tuple[int,int]:
        return (2,3)

    def moveGhost(self, pacMan: PacMan, pathingNodes: PathingNodes, board: list[list[int]]):
        self.moveGhostToTarget(pacMan.getFourTilesAhead(), pathingNodes, board)