from Game import PacManGame
import pygame as pg
import os
import neat

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "Neat", "config.txt")

    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)


def test_genome(genome, config):
    neuralNet = neat.nn.FeedForwardNetwork.create(genome, config)
    game = PacManGame(lockFrameRate=False,drawGhostPaths=False,pacManLives=0,startUpTime=0,exitOnLoss=True, pelletTimeLimit=True)
    runGame = True
    while runGame:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                quit()
        runGame = game.runSingleGameLoop()

game = PacManGame(True,True,3,180,False, False)

runGame = True
while runGame:
    runGame = game.runSingleGameLoop()

pg.quit()
