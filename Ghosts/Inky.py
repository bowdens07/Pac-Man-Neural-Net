import pygame as pg
from Ghosts.Ghost import Ghost

class Inky(Ghost):

    def getRunAwayTarget(self,pacMan_x,pacMan_y):
        return (self._getOppositeSideTarget(pacMan_x,pacMan_y)[0], pacMan_y)
    
    def _getGhostImage(ABC):
        return pg.transform.scale(pg.image.load(f'assets/Inky.png'),(45,45))