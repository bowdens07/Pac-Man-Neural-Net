import pygame as pg
from Ghosts.Ghost import Ghost

class Blinky(Ghost):

    def getRunAwayTarget(self,pacMan_x,pacMan_y):
        return self._getOppositeSideTarget(pacMan_x,pacMan_y)
    
    def _getGhostImage(ABC):
        return pg.transform.scale(pg.image.load(f'assets/Blinky.png'),(45,45))