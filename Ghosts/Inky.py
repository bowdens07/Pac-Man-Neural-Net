import pygame as pg
from GameStateService import GameStateService
from Ghosts.Blinky import Blinky
from Ghosts.Ghost import Ghost
from PacMan import PacMan
from board import getNearestValidPosition, isAWall, isValidPosition
from utilities.PathingNode import PathingNodes

class Inky(Ghost):
    def __init__(self, gameStateService: GameStateService, screen: pg.Surface, board:list[list[int]], xPos:int, yPos:int, blinky: Blinky):
        Ghost.__init__(self, gameStateService,screen,board, xPos, yPos)
        self.blinky = blinky
    def _getGhostImage(ABC):
        return pg.transform.scale(pg.image.load(f'assets/Inky.png'),(45,45))
    
    def _getScatterTarget(ABC) -> tuple[int,int]:
        return (30,23)

    def moveGhost(self, pacMan: PacMan, pathingNodes: PathingNodes, board: list[list[int]]):
        targetStart = pacMan.getXTilesAhead(2)
        blinkyPosition = self.blinky.getCurrentTile()
        positionDifference = ((targetStart[0] - blinkyPosition[0]), (targetStart[1] - blinkyPosition[1]))
        proposedPosition = ((targetStart[0] + positionDifference[0]), (targetStart[1] + positionDifference[1]))
        actualPosition = getNearestValidPosition(proposedPosition)
        self.moveGhostToTarget(actualPosition, pathingNodes, board)