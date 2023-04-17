import pygame as pg
from Ghosts.Ghost import Ghost

class Sue(Ghost):
    
    def _getGhostImage(ABC):
        return pg.transform.scale(pg.image.load(f'assets/Sue.png'),(45,45))