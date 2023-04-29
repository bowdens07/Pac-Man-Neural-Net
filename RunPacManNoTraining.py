from Game import PacManGame
import pygame as pg

game = PacManGame(True,True,3,180,False, False)

runGame = True
while runGame:
    runGame = game.runSingleGameLoop()

pg.quit()
