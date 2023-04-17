import pygame as pg
from Ghosts.Ghost import Ghost

class Inky(Ghost):
    
    def _getGhostImage(ABC):
        return pg.transform.scale(pg.image.load(f'assets/Inky.png'),(45,45))