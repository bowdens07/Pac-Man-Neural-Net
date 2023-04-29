from Game import PacManGame
import pygame as pg

game = PacManGame(True,True,3,180,True, False, True)

runGame = True
while runGame:
    runGame = game.runSingleGameLoop()

pg.quit()
