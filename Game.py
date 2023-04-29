import pygame as pg
import copy
from Ghosts.Ghost import Ghost
from PacMan import PacMan
from direction import Directions
from board import default_board
from graphics import convertPositionToScreenCords, draw_board, drawFromPositionToPositions, drawHud, drawLine, drawPath, drawPathToTarget, drawPathingNodeConnections, drawPathingNodes, drawTileOutlines
from GameStateService import GameStateService
from Ghosts.Blinky import Blinky
from Ghosts.Inky import Inky
from Ghosts.Pinky import Pinky
from Ghosts.Sue import Sue
from utilities.PathingNode import PathingNode, PathingNodes


class PacManGame:


    def __init__(self, lockFrameRate:bool, drawGhostPaths:bool, pacManLives:int, startUpTime:int, allowReplays:bool, pelletTimeLimit:bool, renderGraphics:bool):
        pg.init()
        self.lockFrameRate = lockFrameRate
        self.drawGhostPaths = drawGhostPaths
        self.screen = pg.display.set_mode([900,950])
        self.timer = pg.time.Clock()
        self.fps = 60 #This might need to be uncapped for training
        self.board = copy.deepcopy(default_board)
        self.boardColor = 'blue'
        self.font = pg.font.Font('freesansbold.ttf',20) #arbitrary
        self.pacManImage = pg.transform.scale(pg.image.load(f'assets/PacManMid.png'),(45,45))
        self.gameStateService = GameStateService(pacManLives)
        self.pacMan = PacMan(self.gameStateService, self.screen, self.board, 450,663)
        self.startUpTime = startUpTime
        self.allowReplays = allowReplays
        self.pelletTimeLimit = pelletTimeLimit
        self.renderGraphics = renderGraphics

        #Note - Ghosts must start precisely in the center of a tile, on a Pathing node, otherwise, they will break
        self.blinky = Blinky(self.gameStateService, self.screen, self.board, 53,48)
        self.inky = Inky(self.gameStateService, self.screen, self.board, 413,440, self.blinky)
        self.pinky = Pinky(self.gameStateService, self.screen, self.board, 413,440)
        self.sue = Sue(self.gameStateService, self.screen, self.board, 413,440)
        self.ghosts: list[Ghost] = []#[self.blinky,self.inky,self.pinky,self.sue]

        self.flicker = False
        self.gameStateService.powerPellet = False
        self.runGame = True

        self.direction_request = Directions.RIGHT
        self.pathingNodes = PathingNodes(self.board)
       
    def getAvailablePacManDirections(self) -> list[int]:
        return self.pacMan.getRelativeAvailableDirections()

    def __resetPositions(self):
        self.gameStateService.powerPellet = False
        self.gameStateService.powerCounter = False
        self.gameStateService.scatterCounter = 0
        self.gameStateService.isScatterMode = True
        self.pacMan.xPos = 450
        self.pacMan.yPos = 663
        self.pacMan.direction = Directions.RIGHT
        self.pacMan.turnManager.resetTurns()
        
        self.blinky.xPos = 53
        self.blinky.yPos = 48
        self.blinky.direction = Directions.RIGHT
        self.blinky.isDead = False
        self.blinky.isEaten = False

        self.inky.xPos = 413
        self.inky.yPos = 440
        self.inky.direction = Directions.UP
        self.inky.isDead = False
        self.inky.isEaten = False

        #pinky.xPos = 440
        #pinky.yPos = 438
        self.pinky.xPos = 413
        self.pinky.yPos = 440
        self.pinky.direction = Directions.UP
        self.pinky.isDead = False
        self.pinky.isEaten = False

        self.sue.xPos = 413
        self.sue.yPos = 440
        self.sue.direction = Directions.UP
        self.sue.isDead = False
        self.sue.isEaten = False

    def __checkGhostCollision(self, pacMan:PacMan, ghosts:list[Ghost], gameStateService:GameStateService):
        for g in ghosts:
            if not gameStateService.powerPellet: 
                if (not g.isDead and pacMan.hitbox.colliderect(g.hitBox)):
                    if gameStateService.lives > 0:
                        #print("Pac-Man Died, resetting positions")
                        gameStateService.lives -= 1
                        gameStateService.startupCounter = 0 
                        self.__resetPositions()
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
                    #print("Ate ghost")
                else:
                    if gameStateService.lives > 0:
                        #print("Pac-Man Died, resetting positions")
                        gameStateService.lives -= 1
                        gameStateService.startupCounter = 0 
                        self.__resetPositions()
                        break
                    else:
                        gameStateService.gameOver = True
                        gameStateService.gameStart = False
                        gameStateService.startupCounter = 0

    def __handleGameEvents(self, captureKeyboardLogic: bool = True):
        for event in pg.event.get():
                #process keyboard inputs
                if event.type == pg.QUIT:
                    self.gameStateService.runGame = False
                    print("trying to quit!")
                if captureKeyboardLogic and event.type == pg.KEYDOWN:
                    if event.key == pg.K_RIGHT:
                        self.direction_request = Directions.RIGHT
                    if event.key == pg.K_LEFT:
                        self.direction_request = Directions.LEFT
                    if event.key == pg.K_UP:
                        self.direction_request = Directions.UP
                    if event.key == pg.K_DOWN:
                        self.direction_request = Directions.DOWN
                    if event.key == pg.K_SPACE and (self.gameStateService.gameOver or self.gameStateService.gameWon):
                        self.gameStateService.startupCounter = 0 
                        self.__resetPositions()
                        self.board = copy.deepcopy(default_board)
                        self.pacMan.setNewBoard(self.board)
                        for g in self.ghosts:
                            g.setNewBoard(self.board)   
                        self.gameStateService.gameOver = False
                        self.gameStateService.gameWon = False  
                        self.gameStateService.lives = 3

                if event.type == pg.KEYUP:
                    if event.key == pg.K_RIGHT and self.direction_request == Directions.RIGHT:
                        self.direction_request = self.pacMan.direction
                        #print("requesting Right")
                    if event.key == pg.K_LEFT  and self.direction_request == Directions.LEFT:
                        self.direction_request = self.pacMan.direction
                        #print("requesting Left")
                    if event.key == pg.K_UP  and self.direction_request == Directions.UP:
                        self.direction_request = self.pacMan.direction
                        #print("requesting Up")
                    if event.key == pg.K_DOWN  and self.direction_request == Directions.DOWN: 
                        self.direction_request = self.pacMan.direction  
                        #print("requesting Down")





    #Main game loop
    #returns bool to inidicate if game is over or not
    def runSingleGameLoop(self, turnRequest:Directions = None) -> bool:
        self.timer.tick(self.fps if self.lockFrameRate else 0)

        #counter stuff animates pac man chomping, consider refactor
        if self.gameStateService.counter < 26:
            self.gameStateService.counter +=1
            if self.gameStateService.counter > 3:
                self.flicker = False
        else:
            self.gameStateService.counter = 0
            self.flicker = True

        #manage scatter mode
        if self.gameStateService.isScatterMode:
            if self.gameStateService.scatterCounter < 420:
                self.gameStateService.scatterCounter +=1
            elif self.gameStateService.scatterCounter >= 420:
                self.gameStateService.scatterCounter = 0
                self.gameStateService.isScatterMode = False
                #print("Scatter mode over")
        else:
            if self.gameStateService.attackCounter < 1200:
                self.gameStateService.attackCounter += 1
            elif self.gameStateService.attackCounter >= 1200:
                self.gameStateService.isScatterMode = True
                self.gameStateService.attackCounter = 0
                #print("Scatter mode beginning")
            
        #manage powerPellets
        if self.gameStateService.powerPellet and self.gameStateService.powerCounter < 600:
            self.gameStateService.powerCounter += 1
            #print(self.gameStateService.powerCounter)
        elif self.gameStateService.powerPellet and self.gameStateService.powerCounter >= 600:
            self.gameStateService.powerCounter = 0
            self.gameStateService.powerPellet = False
            #print("PowerPellet Expired")
            for g in self.ghosts:
                g.isEaten = False 
        
        if self.gameStateService.startupCounter < self.startUpTime and not self.gameStateService.gameOver and not self.gameStateService.gameWon:
            self.gameStateService.gameStart = False
            self.gameStateService.startupCounter += 1
        else:
            self.gameStateService.gameStart = True
        self.screen.fill('black')
        
        for g in self.ghosts:
            g.updateSpeed()

        if self.gameStateService.gameStart and not self.gameStateService.gameOver and not self.gameStateService.gameWon:
            self.pacMan.movePacMan()
            for g in self.ghosts:
                g.moveGhost(self.pacMan, self.pathingNodes, self.board)

        #print(f"Nearest Pellet Tile {self.pacMan.getNearestPellet()[0]},{self.pacMan.getNearestPellet()[1]}")
        #pacManNeighbors = pathingNodes.getNeighboringNodes(pacMan.getTilePosition(),board)
        #neighborstr = ""
        #for neighbor in pacManNeighbors:
        #    neighborstr += f"{neighbor[0].position},"
        #print(neighborstr)

        self.gameStateService.score, self.gameStateService.powerPellet, self.gameStateService.powerCounter = self.pacMan.checkCollisions(self.gameStateService.score, self.gameStateService.powerPellet, self.gameStateService.powerCounter)
        self.gameStateService.pelletCounter += 1

        if self.gameStateService.powerCounter == 0 and self.gameStateService.powerPellet: #If the counter is 0 and we ate a pellet, make ghosts eatable again, and turn them around
            for g in self.ghosts: 
                g.isEaten = False
                g.turnGhostAround()
        if(self.renderGraphics):
            draw_board(self.screen, self.board, self.boardColor, self.screen.get_height(), self.screen.get_width(), self.flicker)
            #drawTileOutlines(self.screen, self.board)
            #drawPathingNodes(screen, pathingNodes)
            #drawPathingNodeConnections(screen,pathingNodes)
            #drawFromPositionToPositions(pacMan.getTilePosition(),[neighborPosition[0].position for neighborPosition in pacManNeighbors], screen)
        
        if(self.renderGraphics):
            self.pacMan.draw(self.gameStateService)
            
        for g in self.ghosts:
            if(self.renderGraphics):
                g.draw()
            g.checkCollision()
        
        if self.drawGhostPaths:
            drawPathToTarget(self.pinky.CurrentPath, self.pinky.CurrentTarget, (255,192,203), self.screen,6)
            drawPathToTarget(self.blinky.CurrentPath, self.blinky.CurrentTarget, (255,0,0), self.screen,8)
            drawPathToTarget(self.sue.CurrentPath, self.sue.CurrentTarget, (255,140,0), self.screen,6)
            drawPathToTarget(self.inky.CurrentPath, self.inky.CurrentTarget, (0, 255, 255), self.screen,6)

        if(self.renderGraphics):    
            drawHud(self.gameStateService,self.screen, self.pacManImage, self.font)    
        
        #check for game win
        self.gameStateService.gameWon = True
        for i in range(len(self.board)):
            if 1 in self.board[i] or 2 in self.board[i]:
                self.gameStateService.gameWon = False

        self.__checkGhostCollision(self.pacMan, self.ghosts, self.gameStateService)
        
        if not self.allowReplays and (self.gameStateService.gameOver or self.gameStateService.gameWon):
            return False

        if turnRequest == None:
            self.__handleGameEvents()
            self.pacMan.trySetDirection(self.direction_request)
        else:
            self.__handleGameEvents(captureKeyboardLogic=False)
            self.pacMan.trySetRelativeDirection(turnRequest)


        for g in self.ghosts:
            if self.gameStateService.isInReviveZone(g.getCenterX(),g.getCenterY()):
                g.isDead = False

        if(self.renderGraphics):
            pg.display.flip() ##draws the screen
        
        #if pelletTimeLimit mode and pac man hasn't eaten a pellet in 10 sec, subtract from score and end the game
        if self.pelletTimeLimit and self.gameStateService.pelletCounter > 600:
            self.gameStateService.gameOver = True
            self.gameStateService.runGame = False

        return self.gameStateService.runGame
