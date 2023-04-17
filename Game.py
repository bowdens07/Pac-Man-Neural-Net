import pygame as pg
import copy
from Ghosts.Ghost import Ghost
from PacMan import PacMan
from direction import Directions
from board import default_board
from graphics import convertPositionToScreenCords, draw_board, drawFromPositionToPositions, drawHud, drawLine, drawPath, drawPathingNodeConnections, drawPathingNodes, drawTileOutlines
from GameStateService import GameStateService
from Ghosts.Blinky import Blinky
from Ghosts.Inky import Inky
from Ghosts.Pinky import Pinky
from Ghosts.Sue import Sue
from utilities.PathingNode import PathingNode, PathingNodes


pg.init()


# more graphics logic

screen = pg.display.set_mode([900,950])
timer = pg.time.Clock()
fps = 60 #This might need to be uncapped for training
board = copy.deepcopy(default_board)
boardColor = 'blue'
font = pg.font.Font('freesansbold.ttf',20) #arbitrary

#end graphics logic


pacManImage = pg.transform.scale(pg.image.load(f'assets/PacManMid.png'),(45,45))
gameStateService = GameStateService()

pacMan = PacMan(gameStateService, screen, board, 450,663)

#Note - Ghosts must start precisely in the center of a tile, on a Pathing node, otherwise, they will break
blinky = Blinky(gameStateService, screen, board, 53,48)
inky = Inky(gameStateService, screen, board, 440,388)
pinky = Pinky(gameStateService, screen, board, 53,48)
sue = Sue(gameStateService, screen, board, 440,438)
ghosts: list[Ghost] = [pinky]#[blinky,inky,pinky,sue]


flicker = False
gameStateService.powerPellet = False
runGame = True
       

def resetPositions():
    gameStateService.powerPellet = False
    gameStateService.powerCounter = False
    pacMan.xPos = 450
    pacMan.yPos = 663
    pacMan.direction = Directions.RIGHT
    pacMan.turnManager.resetTurns()
    
    blinky.xPos = 53
    blinky.yPos = 48
    blinky.direction = Directions.RIGHT
    blinky.isDead = False
    blinky.isEaten = False

    inky.xPos = 440
    inky.yPos = 388
    inky.direction = Directions.UP
    inky.isDead = False
    inky.isEaten = False

    #pinky.xPos = 440
    #pinky.yPos = 438
    pinky.xPos = 53
    pinky.yPos = 48
    pinky.direction = Directions.UP
    pinky.isDead = False
    pinky.isEaten = False

    sue.xPos = 440
    sue.yPos = 438
    sue.direction = Directions.UP
    sue.isDead = False
    sue.isEaten = False

def checkGhostCollision(pacMan:PacMan, ghosts:list[Ghost], gameStateService:GameStateService):
    for g in ghosts:
        if not gameStateService.powerPellet: 
            if (not g.isDead and pacMan.hitbox.colliderect(g.hitBox)):
                if gameStateService.lives > 0:
                    print("Pac-Man Died, resetting positions")
                    gameStateService.lives -= 1
                    gameStateService.startupCounter = 0 
                    resetPositions()
                    break
                else:
                    gameStateService.gameOver = True
                    gameStateService.gameStart = False
                    gameStateService.startupCounter = 0
        elif(not g.isDead and pacMan.hitbox.colliderect(g.hitBox)):
            if (not g.isEaten):
                g.isDead = True
                g.isEaten = True
                numGhosts = len([g for g in ghosts if g.isEaten])
                gameStateService.score += (2 ** numGhosts) * 100
                print("Ate ghost")
            else:
                if gameStateService.lives > 0:
                    print("Pac-Man Died, resetting positions")
                    gameStateService.lives -= 1
                    gameStateService.startupCounter = 0 
                    resetPositions()
                    break
                else:
                    gameStateService.gameOver = True
                    gameStateService.gameStart = False
                    gameStateService.startupCounter = 0


direction_request = Directions.RIGHT
pathingNodes = PathingNodes(board)

#Main game loop
while runGame:
    timer.tick(fps)

    #counter stuff animates pac man chomping, not in love with it, but hey
    if gameStateService.counter < 26:
        gameStateService.counter +=1
        if gameStateService.counter > 3:
            flicker = False
    else:
        gameStateService.counter = 0
        flicker = True
    #manage powerPellets
    if gameStateService.powerPellet and gameStateService.powerCounter < 6000:
        gameStateService.powerCounter += 1
        print(gameStateService.powerCounter)
    elif gameStateService.powerPellet and gameStateService.powerCounter >= 6000:
        gameStateService.powerCounter = 0
        gameStateService.powerPellet = False
        print("PowerPellet Expired")
        for g in ghosts:
            g.isEaten = False 

    if gameStateService.startupCounter < 240 and not gameStateService.gameOver and not gameStateService.gameWon:
        gameStateService.gameStart = False
        gameStateService.startupCounter += 1
    else:
        gameStateService.gameStart = True
    screen.fill('black')
    
    for g in ghosts:
        g.updateSpeed()

    
    
    if gameStateService.gameStart and not gameStateService.gameOver and not gameStateService.gameWon:
        pacMan.movePacMan()
        #blinky.moveGhost(pacMan.getTilePosition(),pathingNodes)
        #inky.moveSue()
        pinky.moveGhost(pacMan.getFourTilesAhead(),pathingNodes, board)
        #sue.moveSue()

    #pacManNeighbors = pathingNodes.getNeighboringNodes(pacMan.getTilePosition(),board)
    #neighborstr = ""
    #for neighbor in pacManNeighbors:
    #    neighborstr += f"{neighbor[0].position},"
    #print(neighborstr)

    gameStateService.score, gameStateService.powerPellet, gameStateService.powerCounter = pacMan.checkCollisions(gameStateService.score, gameStateService.powerPellet, gameStateService.powerCounter, ghosts)
    draw_board(screen, board, boardColor, screen.get_height(), screen.get_width(), flicker)
    drawTileOutlines(screen, board)
    #drawPathingNodes(screen, pathingNodes)
    #drawPathingNodeConnections(screen,pathingNodes)
    #drawFromPositionToPositions(pacMan.getTilePosition(),[neighborPosition[0].position for neighborPosition in pacManNeighbors], screen)

    pacMan.draw(gameStateService)
    for g in ghosts:
        g.draw()
        g.checkCollision()

    #If blinky is on a pathing node, draw a green rectangle on him: for debugging
    #if blinky.isOnPathingNode(pathingNodes):
    #    pg.draw.rect(screen,'blue', [blinky.xPos + 10,blinky.yPos + 10,20,20],0,10)

    #Draw the tile four tiles ahead of pac-man
    #fourTilesAhead = pacMan.getFourTilesAhead()
    #fourTilesCoords = convertPositionToScreenCords(fourTilesAhead)
    #pg.draw.rect(screen,'blue', pg.Rect(fourTilesCoords[0],fourTilesCoords[1],20,20),0,10)

    #path = blinky.CurrentPath
    #if path is not None and len(path) > 0:
    #    for i in range(len(path) -1):
    #        drawLine(path[i].position, path[i + 1].position, screen,(255,0,0))
    #    drawLine(path[len(path) - 1].position, pacMan.getTilePosition(), screen,(255,0,0))
    

    drawPath(pinky.CurrentPath, (255,192,203), screen)
    drawPath(blinky.CurrentPath, (255,0,0), screen)
    
    drawHud(gameStateService,screen, pacManImage, font)    
      
    #check for game win
    gameStateService.gameWon = True
    for i in range(len(board)):
        if 1 in board[i] or 2 in board[i]:
            gameStateService.gameWon = False

    checkGhostCollision(pacMan, ghosts, gameStateService)

    for event in pg.event.get():
        #process keyboard inputs
        if event.type == pg.QUIT:
            runGame = False
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_RIGHT:
                direction_request = Directions.RIGHT
            if event.key == pg.K_LEFT:
                direction_request = Directions.LEFT
            if event.key == pg.K_UP:
                direction_request = Directions.UP
            if event.key == pg.K_DOWN:
                direction_request = Directions.DOWN
            if event.key == pg.K_SPACE and (gameStateService.gameOver or gameStateService.gameWon):
                gameStateService.startupCounter = 0 
                resetPositions()
                board = copy.deepcopy(default_board)
                pacMan.setNewBoard(board)
                for g in ghosts:
                    g.setNewBoard(board)   
                gameStateService.gameOver = False
                gameStateService.gameWon = False  

        if event.type == pg.KEYUP:
            if event.key == pg.K_RIGHT and direction_request == Directions.RIGHT:
                direction_request = pacMan.direction
                #print("requesting Right")
            if event.key == pg.K_LEFT  and direction_request == Directions.LEFT:
                direction_request = pacMan.direction
                #print("requesting Left")
            if event.key == pg.K_UP  and direction_request == Directions.UP:
                direction_request = pacMan.direction
                #print("requesting Up")
            if event.key == pg.K_DOWN  and direction_request == Directions.DOWN: 
                direction_request = pacMan.direction  
                #print("requesting Down")
        #set the new direction if you can
    if direction_request == Directions.RIGHT and pacMan.turnManager.right:
        pacMan.direction = direction_request
        #print("Turning Right")
    if direction_request == Directions.LEFT and pacMan.turnManager.left:
        pacMan.direction = direction_request
        #print("Turning Left")
    if direction_request == Directions.DOWN and pacMan.turnManager.down:
        pacMan.direction = direction_request
        #print("Turning Down")
    if direction_request == Directions.UP and pacMan.turnManager.up:
        pacMan.direction = direction_request
        #print("Turning Up")

    for g in ghosts:
        if gameStateService.isInReviveZone(g.getCenterX(),g.getCenterY()):
            g.isDead = False
    pg.display.flip() ##draws the screen
pg.quit() # End the game