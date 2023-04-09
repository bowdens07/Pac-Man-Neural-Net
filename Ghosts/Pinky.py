import pygame as pg
from Ghosts.Ghost import Ghost

class Pinky(Ghost):

    def getRunAwayTarget(self,pacMan_x,pacMan_y):
        return (pacMan_x,self._getOppositeSideTarget(pacMan_x,pacMan_y)[1])
    
    def _getGhostImage(ABC):
        return pg.transform.scale(pg.image.load(f'assets/Inky.png'),(45,45))