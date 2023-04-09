import pygame as pg
import copy
from Ghosts.Ghost import Ghost
from direction import Directions
from board import default_board
from graphics import draw_board
from GameStateService import GameStateService
from Ghosts.Blinky import Blinky
from Ghosts.Inky import Inky
from Ghosts.Pinky import Pinky
from Ghosts.Sue import Sue


pg.init()

##TODO BUG: Go to bottom left corner. Go up, hold left, soon as turn left press UP. Pac man can get off the grid, check out fudge factor

# more graphics logic

screen = pg.display.set_mode([900,950])
timer = pg.time.Clock()
fps = 60 #This might need to be uncapped for training
font = pg.font.Font('freesansbold.ttf',20) #arbitrary
board = copy.deepcopy(default_board)
boardColor = 'blue'

pacManImages = []
pacManImages.append(pg.transform.scale(pg.image.load(f'assets/PacManClose.png'),(45,45)))
pacManImages.append(pg.transform.scale(pg.image.load(f'assets/PacManMid.png'),(45,45)))
pacManImages.append(pg.transform.scale(pg.image.load(f'assets/PacManOpen.png'),(45,45)))

#end graphics logic

pacMan_x = 450
pacMan_y = 663
direction_request = Directions.RIGHT
pacManDirection = Directions.RIGHT
pacManVelocity = 2


gameStateService = GameStateService()
 
gameWon = False

blinky = Blinky(gameStateService, screen, board, 56,58)
inky = Inky(gameStateService, screen, board, 440,388)
pinky = Pinky(gameStateService, screen, board, 440,438)
sue = Sue(gameStateService, screen, board, 440,438)
ghosts: list[Ghost] = [blinky,inky,pinky,sue]


def getPacManCenterX():
    return pacMan_x + 22

def getPacManCenterY():
    return pacMan_y + 23

flicker = False
availableTurns = [False,False,False,False] # R, L, U, D -> make this a class
gameStateService.powerPellet = False
lives = 3

def isInMiddleOfTileX():
    tile_width = screen.get_width() // 30 #30 horizontal tiles
    if 12 <= getPacManCenterX() % tile_width <= 18:
        return True
    return False

def isInMiddleOfTileY():
    tile_height = (screen.get_height() - 50) // 32 #32 vertical tiles
    if 12 <= getPacManCenterY() % tile_height <= 18:
        return True
    return False

## More likely I want to make a velocity system -> see if position + velocity is valid, then decide to move or not.
def getValidTurns(xPos):
    turns = [False,False,False,False]
    tile_height = (screen.get_height() - 50) // 32 #32 vertical tiles, leave 50 px for UI elements at bottom (may remove)
    tile_width = screen.get_width() // 30 #30 horizontal tiles
    fudgeFactor = 17 
    # check collision based on xPos and yPos of player +/- fudgeFactor 
    if xPos //30 < 29:
        #Can I reverse Direction?
        if pacManDirection == Directions.RIGHT: # <3 because board values 0,1,2 can be moved into, rest are walls
            if board[getPacManCenterY() // tile_height][(getPacManCenterX() - fudgeFactor) // tile_width]  < 3:
                turns[1] = True
        if pacManDirection == Directions.LEFT:
            if board[getPacManCenterY() // tile_height][(getPacManCenterX() + fudgeFactor) // tile_width]  < 3:
                turns[0] = True
        if pacManDirection == Directions.UP:
            if board[(getPacManCenterY() + fudgeFactor) // tile_height][getPacManCenterX() // tile_width]  < 3:
                turns[3] = True
        if pacManDirection == Directions.DOWN:
            if board[(getPacManCenterY() - fudgeFactor) // tile_height][getPacManCenterX() // tile_width]  < 3:
                turns[2] = True

        #Can I turn up or down?
        if pacManDirection == Directions.UP or pacManDirection == Directions.DOWN:
            if(isInMiddleOfTileX()): #IF pac man is approximately horiztonatally in middle of tile
                if board[(getPacManCenterY() + fudgeFactor) // tile_height][getPacManCenterX() // tile_width] < 3:
                    turns[3] = True
                if board[(getPacManCenterY() - fudgeFactor) // tile_height][getPacManCenterX() // tile_width] < 3:
                    turns[2] = True
            if(isInMiddleOfTileY()): #IF pac man is approximately horiztonatally in middle of tile
                if board[getPacManCenterY() // tile_height][(getPacManCenterX() - tile_width) // tile_width] < 3:
                    turns[1] = True
                if board[getPacManCenterY() // tile_height][(getPacManCenterX() + tile_width) // tile_width] < 3:
                    turns[0] = True
        #Can I turn left or right?
        if pacManDirection == Directions.RIGHT or pacManDirection == Directions.LEFT:
            if(isInMiddleOfTileX()): #IF pac man is approximately horiztonatally in middle of tile
                if board[(getPacManCenterY() + fudgeFactor) // tile_height][getPacManCenterX() // tile_width] < 3:
                    turns[3] = True
                if board[(getPacManCenterY() - fudgeFactor) // tile_height][getPacManCenterX() // tile_width] < 3:
                    turns[2] = True
            if(isInMiddleOfTileY()): #IF pac man is approximately vertically in middle of tile
                if board[getPacManCenterY() // tile_height][(getPacManCenterX() - fudgeFactor) // tile_width] < 3:
                    turns[1] = True
                if board[getPacManCenterY() // tile_height][(getPacManCenterX() + fudgeFactor) // tile_width] < 3:
                    turns[0] = True
    else: #This is for wrapping around the board horizontally. If you want to wrap vertically, this code must change
        turns[0] = True
        turns[1] = True
    return turns
    
def movePacMan(pacManX, pacManY):
    if pacManDirection == Directions.RIGHT and availableTurns[Directions.RIGHT]:
        pacManX += pacManVelocity
    elif pacManDirection == Directions.LEFT and availableTurns[Directions.LEFT]:
        pacManX -= pacManVelocity
    elif pacManDirection == Directions.UP and availableTurns[Directions.UP]:
        pacManY -= pacManVelocity
    elif pacManDirection == Directions.DOWN and availableTurns[Directions.DOWN]:
        pacManY += pacManVelocity
    return pacManX, pacManY

#ghosts doesn't have to be returned as a shallow copy will do, but I will for now
def checkCollisions(curScore, power, powerCount, ghosts: list[Ghost]):
    tile_height = (screen.get_height() - 50) // 32 #32 vertical tiles
    tile_width = screen.get_width() // 30 #30 horizontal tiles
    if 0 < pacMan_x < 870:
        if board[getPacManCenterY() // tile_height][getPacManCenterX() // tile_width] == 1:
            board[getPacManCenterY() // tile_height][getPacManCenterX() // tile_width] = 0 #eat the pellet
            curScore += 10
        if board[getPacManCenterY() // tile_height][getPacManCenterX() // tile_width] == 2:
            board[getPacManCenterY() // tile_height][getPacManCenterX() // tile_width] = 0 #eat the pellet
            curScore += 50
            power = True
            print("Power pellet Eaten")
            powerCount = 0
            for g in ghosts: 
                g.isEaten = False
            #eatenGhosts = [False,False,False,False]
    return curScore, power, powerCount, ghosts 


def drawHud(gameStateService: GameStateService): ##TODO bugged
    scoreText = font.render(f'Score: {gameStateService.score}', True, 'white')
    screen.blit(scoreText,(10,920))
    for i in range(lives):
        screen.blit(pg.transform.scale(pacManImages[1], (30,30)), (650 + i * 40, 915))
    if(gameStateService.gameOver): ##compress this to a single function
        pg.draw.rect(screen,'white', [50,200,800,300],0,10)
        pg.draw.rect(screen,'dark gray', [70,220,768,268],0,10)
        gameOverText = font.render('Game over! Space bar to restart!', True, "red")
        screen.blit(gameOverText, (100,300))
    if(gameWon):
        pg.draw.rect(screen,'white', [50,200,800,300],0,10)
        pg.draw.rect(screen,'dark gray', [70,220,768,268],0,10)
        gameOverText = font.render('Victory! Space bar to restart!', True, 'white')
        screen.blit(gameOverText, (100,300))

runGame = True

def drawPacMan(gameStateService: GameStateService):
    if pacManDirection == Directions.RIGHT: 
        screen.blit(pacManImages[gameStateService.counter // 9], (pacMan_x,pacMan_y))
    elif pacManDirection == Directions.LEFT: 
        screen.blit(pg.transform.flip(pacManImages[gameStateService.counter // 9],True,False), (pacMan_x,pacMan_y))
    elif pacManDirection == Directions.UP: 
        screen.blit(pg.transform.rotate(pacManImages[gameStateService.counter // 9],90), (pacMan_x,pacMan_y))
    elif pacManDirection == Directions.DOWN: 
        screen.blit(pg.transform.rotate(pacManImages[gameStateService.counter // 9],-90), (pacMan_x,pacMan_y))        

def resetPositions():
    gameStateService.powerPellet = False
    gameStateService.powerCounter = False
    pacMan_x = 450 ##todo once you make a pac man class, this will work
    pacMan_y = 663
    pacManDirection = Directions.RIGHT
    
    blinky.xPos = 56
    blinky.yPos = 58
    blinky.direction = Directions.RIGHT
    blinky.isDead = False
    blinky.isEaten = False

    inky.xPos = 440
    inky.yPos = 388
    inky.direction = Directions.UP
    inky.isDead = False
    inky.isEaten = False

    pinky.xPos = 440
    pinky.yPos = 438
    pinky.direction = Directions.UP
    pinky.isDead = False
    pinky.isEaten = False

    sue.xPos = 440
    sue.yPos = 438
    sue.direction = Directions.UP
    sue.isDead = False
    sue.isEaten = False

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
    if gameStateService.powerPellet and gameStateService.powerCounter < 9999: ##TODO change back to 600
        gameStateService.powerCounter += 1
        print(gameStateService.powerCounter)
    elif gameStateService.powerPellet and gameStateService.powerCounter >= 9999:
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
    
#set ghosts speeds - tightly coupled
    for g in ghosts:
        g.updateSpeed()

    availableTurns = getValidTurns(getPacManCenterX())
    if gameStateService.gameStart and not gameStateService.gameOver and not gameStateService.gameWon:
        pacMan_x, pacMan_y = movePacMan(pacMan_x, pacMan_y)
        blinky_x, blinky_y, blinkyDirection = blinky.moveSue()
        inky_x, inky_y, inkyDirection = inky.moveSue()
        pinky_x, pinky_y, pinkyDirection = pinky.moveSue()
        sue_x, sue_y, sueDirection = sue.moveSue()
        #print(f'BlinkyPos ${blinky_x},{blinky_y}') seems to be valid

    gameStateService.score, gameStateService.powerPellet, gameStateService.powerCounter, ghosts = checkCollisions(gameStateService.score, gameStateService.powerPellet, gameStateService.powerCounter, ghosts)
    draw_board(screen, board, boardColor, screen.get_height(), screen.get_width(), flicker)
    pacManHitBox = pg.draw.circle(screen, 'black', (getPacManCenterX(), getPacManCenterY()), 20, 2)
    drawPacMan(gameStateService)

    #print(f'Inky Turns L: {inky.turns[0]} R: {inky.turns[1]} U: {inky.turns[2]} D: {inky.turns[3]} C-XY: {inky.getCenterX()},{inky.getCenterY()}')


    for g in ghosts:
    #    g.turns, g.isInBox = g.checkCollision()
        g.draw()
        g.checkCollision() #for some reason collision is always true when not reusinc ctors
        g.setNewTarget(pacMan_x,pacMan_y)
        
    drawHud(gameStateService)

    #check for game win
    gameStateService.gameWon = True
    for i in range(len(board)):
        if 1 in board[i] or 2 in board[i]:
            gameStateService.gameWon = False

    for g in ghosts:
        if not gameStateService.powerPellet: 
            if (not g.isDead and pacManHitBox.colliderect(g.hitBox)):
                if lives > 0:
                    print("Pac-Man Died, resetting game")
                    lives -= 1
                    gameStateService.startupCounter = 0 
                    pacMan_x = 450 ##todo remove after making pac man class
                    pacMan_y = 663
                    resetPositions()
                    break
                else:
                    gameStateService.gameOver = True
                    gameStateService.gameStart = False
                    gameStateService.startupCounter = 0
        elif (gameStateService.powerPellet and not g.isDead and not g.isEaten and pacManHitBox.colliderect(g.hitBox)):
            g.isDead = True
            g.isEaten = True
            numGhosts = len([g for g in ghosts if g.isEaten])
            gameStateService.score += (2 ** numGhosts) * 100
            print("Ate ghost: " + str(g.ghostId))




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
                    gameStateService.startupCounter = 0  #repasted elsewhere. Make it a function!
                    #move everyone back to init positions - make this a function - more like reset game function 
                    pacMan_x = 450 ##todo remove after making pac man class
                    pacMan_y = 663
                    resetPositions()

                    #this logic below is unique to restart
                    board = copy.deepcopy(default_board)
                    for g in ghosts: #make sure the ghost's board match the new board
                        g.setNewBoard(board)   
                        
                    gameStateService.gameOver = False
                    gameStateService.gameWon = False  

        if event.type == pg.KEYUP:
            if event.key == pg.K_RIGHT and direction_request == Directions.RIGHT:
                direction_request = pacManDirection
                #print("requesting Right")
            if event.key == pg.K_LEFT  and direction_request == Directions.LEFT:
                direction_request = pacManDirection
                #print("requesting Left")
            if event.key == pg.K_UP  and direction_request == Directions.UP:
                direction_request = pacManDirection
                #print("requesting Up")
            if event.key == pg.K_DOWN  and direction_request == Directions.DOWN: 
                direction_request = pacManDirection  
                #print("requesting Down")
        #set the new direction if you can
    if direction_request == Directions.RIGHT and availableTurns[Directions.RIGHT]:
        pacManDirection = direction_request
        #print("Turning Right")
    if direction_request == Directions.LEFT and availableTurns[Directions.LEFT]:
        pacManDirection = direction_request
        #print("Turning Left")
    if direction_request == Directions.DOWN and availableTurns[Directions.DOWN]:
        pacManDirection = direction_request
        #print("Turning Down")
    if direction_request == Directions.UP and availableTurns[Directions.UP]:
        pacManDirection = direction_request
        #print("Turning Up")

    if pacMan_x > 900: #wrap pac man if he moves off screen, magic numbers are for visuals
        pacMan_x = -47
    elif pacMan_x < -50:
        pacMan_x = 897

    for g in ghosts:
        if gameStateService.isInReviveZone(g.getCenterX(),g.getCenterY()):
            g.isDead = False
    pg.display.flip() ##draws the screen
pg.quit() # End the game