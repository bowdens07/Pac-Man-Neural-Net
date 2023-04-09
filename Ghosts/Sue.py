import pygame as pg
from Ghosts.Ghost import Ghost

class Sue(Ghost):

    def getRunAwayTarget(self,pacMan_x,pacMan_y):
        return (450,450)
    
    def _getGhostImage(ABC):
        return pg.transform.scale(pg.image.load(f'assets/Sue.png'),(45,45))