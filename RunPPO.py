import path
from stable_baselines3 import PPO
import pygame as pg
from Game import PacManGame
from direction import Directions
import os


def main():
    game = PacManGame(lockFrameRate=True,drawGhostPaths=False,pacManLives=0,startUpTime=0,allowReplays=False, pelletTimeLimit=True, renderGraphics=True)
    model = PPO.load(os.path.join("PPOLogs","best_model.zip"), env=game)

    observation = game.reset()
    runGame = True
    while runGame:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    quit()

            action, _states = model.predict(observation)
            #todo convert netOutptut into direction request
            runGame = game.runSingleGameLoop(Directions(action))
   

if __name__ == "__main__":
     main()