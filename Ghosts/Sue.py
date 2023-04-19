import pygame as pg
from Ghosts.Ghost import Ghost
from PacMan import PacMan
from utilities.PathingNode import PathingNodes

class Sue(Ghost):
    
    def _getGhostImage(ABC):
        return pg.transform.scale(pg.image.load(f'assets/Sue.png'),(45,45))
    
    def _getScatterTarget(ABC) -> tuple[int,int]:
        return (30,8)

    def moveGhost(self, pacMan: PacMan, pathingNodes: PathingNodes, board: list[list[int]]):
        if Ghost._distanceToTargetHeuristic(self.getCurrentTile(),pacMan.getCurrentTile()) > 8:
            self.moveGhostToTarget(pacMan.getCurrentTile(), pathingNodes, board)
        else:
            self.moveGhostToTarget(self._getScatterTarget(), pathingNodes, board)

