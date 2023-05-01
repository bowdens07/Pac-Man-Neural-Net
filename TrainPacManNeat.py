import pygame as pg
import os
import neat
from Game import PacManGame

from direction import Directions
from graphics import convertPositionToScreenCords
import pickle

def run_neat(config, generations:int):
    population = neat.Checkpointer.restore_checkpoint('neat-checkpoint-1153')
    population.config.fitness_threshold = 2620
    #population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)
    population.add_reporter(neat.Checkpointer(generations))

    winner = population.run(eval_genomes, generations)
    with open("best.pickle", "wb") as f:
        pickle.dump(winner, f)



def eval_genomes(genomes, configuration):
    for (genome_id, genome) in genomes:
        game = PacManGame(lockFrameRate=False,drawGhostPaths=False,pacManLives=0,startUpTime=0,allowReplays=False, pelletTimeLimit=True, renderGraphics=False)
        test_genome(genome,configuration,game)


def test_genome(genome, config, game:PacManGame):
    genome.fitness = 0
    neuralNet = neat.nn.FeedForwardNetwork.create(genome, config)
    runGame = True
    while runGame:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                quit()

        nearestPelletDirection = game.pacMan.getRelativeDirectionToNearestPellet()
        availableTurns = game.pacMan.getRelativeAvailableDirections()
        netOutput = neuralNet.activate(
            [
                game.pacMan.getCenterX(), game.pacMan.getCenterY(),
                game.pacMan.direction.value, 
                game.blinky.getCenterX(),game.blinky.getCenterY(), 
                game.pinky.getCenterX(),game.pinky.getCenterY(), 
                game.sue.getCenterX(),game.sue.getCenterY(),
                game.inky.getCenterX(),game.inky.getCenterY(), 
                game.gameStateService.powerPellet, 
                nearestPelletDirection.value,
                availableTurns[0],availableTurns[1],availableTurns[2],availableTurns[3]
            ]
        )
        direction_request = netOutput.index(max(netOutput))
        runGame = game.runSingleGameLoop(Directions(direction_request))
    calculate_exploration_fitness(genome, game)


def calculate_exploration_fitness(genome, game: PacManGame):
    #subtract 100 points for every time it lingers on a tile for more than 1.5 seconds
    genome.fitness += (game.gameStateService.score - (game.lingeredOnTileCounter * 100))


def watch_best(config):
    with open("bestGhostPacManNeat.pickle", "rb") as f:
        winner = pickle.load(f)

    game = PacManGame(lockFrameRate=True,drawGhostPaths=False,pacManLives=0,startUpTime=0,allowReplays=False, pelletTimeLimit=True, renderGraphics=True)
    test_genome(winner, config,game)


#Code to do training
if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config.txt")

    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)
    #run_neat(config,1000)
    watch_best(config)

    

