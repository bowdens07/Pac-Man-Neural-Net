from Game import PacManGame
import pygame as pg

game = PacManGame(True,True,0,0,True)

runGame = True
while runGame:
    runGame = game.runSingleGameLoop()

pg.quit()
