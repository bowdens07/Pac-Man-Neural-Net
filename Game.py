import pygame as pg
import copy
from direction import Directions
from board import default_board
from graphics import draw_board
from GameStateService import GameStateService
from Ghost import Ghost

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

blinkyImage = pg.transform.scale(pg.image.load(f'assets/Blinky.png'),(45,45))
inkyImage = pg.transform.scale(pg.image.load(f'assets/Inky.png'),(45,45))
pinkyImage = pg.transform.scale(pg.image.load(f'assets/Pinky.png'),(45,45))
sueImage = pg.transform.scale(pg.image.load(f'assets/Sue.png'),(45,45))
#end graphics logic

pacMan_x = 450
pacMan_y = 663
direction_request = Directions.RIGHT
pacManDirection = Directions.RIGHT
pacManVelocity = 2


gameStateService = GameStateService()
 
ghostsEaten = [False,False,False,False]
ghostTargets = [(pacMan_x, pacMan_y),(pacMan_x, pacMan_y),(pacMan_x, pacMan_y),(pacMan_x, pacMan_y)]
ghostSpeeds = [2,2,2,2]

blinky_x = 56
blinky_y = 58
blinkyDirection = Directions.RIGHT
blinkyDead = False
blinkyBox = False
screen.get_width()
inky_x = 440 
inky_y = 388
inkyDirection = Directions.UP
inkyDead = False
inkyBox = False

pinky_x = 440
pinky_y = 438
pinkyDirection = Directions.UP
pinkyDead = False
pinkyBox = False

sue_x = 440
sue_y = 438
sueDirection = Directions.UP
sueDead = False
sueBox = False

gameWon = False

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

def getTargets(blinky_x,blinky_y,inky_x, inky_y, pinky_x,pinky_y, sue_x, sue_y):
    if pacMan_x < 450: #basicall move to the opposite side of the board pac-man is on if powerup
        runawayX = 900
    else:
        runawayX = 0
    if pacMan_y < 450:
        runawayY = 900
    else:
        runawayY = 0
    returnTarget = (380, 400) #inside the box
#Bugged right now : Todo, once eyes get into box, set them to leave box, then purusue pac man again
    if gameStateService.powerPellet:
        if not blinky.isDead:
            blinkyTarget = (runawayX, runawayY)
        else: 
            blinkyTarget = returnTarget
        if not inky.isDead:
            inkyTarget = (runawayX, pacMan_y)
        else: 
            inkyTarget = returnTarget
        if not pinky.isDead:
            pinkyTarget = (pacMan_x, runawayY)
        else: 
            pinkyTarget = returnTarget
        if not sue.isDead:
            sueTarget = (450, 450)
        else: 
            sueTarget = returnTarget
    else: 
        if not blinky.isDead:
            if isInTheBox(blinky_x, blinky_y):
                blinkyTarget = (400,100)
            else:
                blinkyTarget = (pacMan_x, pacMan_y)
        else: 
            blinkyTarget = returnTarget
        if not inky.isDead:
            if isInTheBox(inky_x, inky_y):
                inkyTarget = (400,100)
            else:
                inkyTarget = (pacMan_x, pacMan_y)                
        else: 
            inkyTarget = returnTarget
        if not pinky.isDead:
            if isInTheBox(pinky_x,pinky_y):
                pinkyTarget = (400,100)
            else:
                pinkyTarget = (pacMan_x, pacMan_y)
        else: 
            pinkyTarget = returnTarget
        if not sue.isDead:
            if isInTheBox(sue_x,sue_y):
                sueTarget = (400,100)
            else:
                sueTarget = (pacMan_x, pacMan_y)
        else: 
            sueTarget = returnTarget     

    return [blinkyTarget, inkyTarget, pinkyTarget, sueTarget]

def isInTheBox(xPosition, yPosition) -> bool:
    return 340 < xPosition < 560 and 330 < yPosition < 500

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

def drawHud(gameStateService: GameStateService):
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

#TODO: get rid of this class mismanagement
vulnerableGhostImage = pg.transform.scale(pg.image.load(f'assets/VulnerableGhost.png'),(45,45))
deadGhostImage = pg.transform.scale(pg.image.load(f'assets/DeadEyesRight.png'),(45,45))

blinky = Ghost(gameStateService, screen, board, blinky_x,blinky_y, ghostTargets[0], ghostSpeeds[0], blinkyImage, blinkyDirection, blinkyDead, False, 0, vulnerableGhostImage, deadGhostImage)
inky = Ghost(gameStateService, screen, board, inky_x,inky_y, ghostTargets[1], ghostSpeeds[1], inkyImage, inkyDirection, inkyDead, False, 1, vulnerableGhostImage, deadGhostImage)
pinky = Ghost(gameStateService, screen, board, pinky_x,pinky_y, ghostTargets[2], ghostSpeeds[2], pinkyImage, pinkyDirection, pinkyDead, False, 2, vulnerableGhostImage, deadGhostImage)
sue = Ghost(gameStateService, screen, board, sue_x,sue_y, ghostTargets[3], ghostSpeeds[3], sueImage, sueDirection, sueDead, False, 3, vulnerableGhostImage, deadGhostImage)
ghosts = [blinky,inky,pinky,sue]

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
            g.isEaten = False #TODO why intellisense white?
        #ghostsEaten = [False, False, False, False] 

    if gameStateService.startupCounter < 240 and not gameStateService.gameOver and not gameStateService.gameWon:
        gameStateService.gameStart = False
        gameStateService.startupCounter += 1
    else:
        gameStateService.gameStart = True
    screen.fill('black')
    
#set ghosts speeds - tightly coupled
    if not gameStateService.powerPellet:
        ghostSpeeds = [1,1,1,1]
    else:
        ghostSpeeds = [1,1,1,1]
        for g in ghosts: #TODO: This really sucks bad 
            if g.isEaten:
                ghostSpeeds[g.ghostId] = 2
        if blinkyDead:
            ghostSpeeds[0] =  4       
        if inkyDead:
            ghostSpeeds[1] =  4    
        if pinkyDead:
            ghostSpeeds[2] =  4    
        if sueDead:
            ghostSpeeds[3] =  4    


    availableTurns = getValidTurns(getPacManCenterX())
    if gameStateService.gameStart and not gameStateService.gameOver and not gameStateService.gameWon:
        pacMan_x, pacMan_y = movePacMan(pacMan_x, pacMan_y)
        blinky_x, blinky_y, blinkyDirection = blinky.moveSue()
        inky_x, inky_y, inkyDirection = inky.moveSue()
        pinky_x, pinky_y, pinkyDirection = pinky.moveSue()
        sue_x, sue_y, sueDirection = sue.moveSue()

    gameStateService.score, gameStateService.powerPellet, gameStateService.powerCounter, ghosts = checkCollisions(gameStateService.score, gameStateService.powerPellet, gameStateService.powerCounter, ghosts)
    draw_board(screen, board, boardColor, screen.get_height(), screen.get_width(), flicker)
    pacManHitBox = pg.draw.circle(screen, 'black', (getPacManCenterX(), getPacManCenterY()), 20, 2)
    drawPacMan(gameStateService)
    #TODO: redeclaring the ghosts every frame is unaceptable. Change that 
    blinky = Ghost(gameStateService, screen, board, blinky_x,blinky_y, ghostTargets[0], ghostSpeeds[0], blinkyImage, blinkyDirection, blinkyDead, ghosts[0].isEaten, 0, vulnerableGhostImage, deadGhostImage)
    inky = Ghost(gameStateService, screen, board, inky_x,inky_y, ghostTargets[1], ghostSpeeds[1], inkyImage, inkyDirection, inkyDead, ghosts[1].isEaten, 1, vulnerableGhostImage, deadGhostImage)
    pinky = Ghost(gameStateService, screen, board, pinky_x,pinky_y, ghostTargets[2], ghostSpeeds[2], pinkyImage, pinkyDirection, pinkyDead, ghosts[2].isEaten, 2, vulnerableGhostImage, deadGhostImage)
    sue = Ghost(gameStateService, screen, board, sue_x,sue_y, ghostTargets[3], ghostSpeeds[3], sueImage, sueDirection, sueDead, ghosts[3].isEaten, 3, vulnerableGhostImage, deadGhostImage)
    ghosts = [blinky,inky,pinky,sue]

    drawHud(gameStateService)
    ghostTargets = getTargets(blinky_x,blinky_y,inky_x, inky_y, pinky_x,pinky_y, sue_x, sue_y)

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
                    #move everyone back to init positions - make this a function - more like reset game function 
                    gameStateService.powerPellet = False
                    gameStateService.powerCounter = False
                    pacMan_x = 450
                    pacMan_y = 663
                    pacManDirection = Directions.RIGHT

                    blinky_x = 56
                    blinky_y = 58
                    blinkyDirection = Directions.RIGHT
                    blinkyDead = False

                    inky_x = 440 
                    inky_y = 388
                    inkyDirection = Directions.UP
                    inkyDead = False

                    pinky_x = 440
                    pinky_y = 438
                    pinkyDirection = Directions.UP
                    pinkyDead = False

                    sue_x = 440
                    sue_y = 438
                    sueDirection = Directions.UP
                    sueDead = False
                    for g in ghosts: 
                        g.isEaten = False
                    #ghostsEaten = [False, False, False, False]
                    break
                else:
                    gameStateService.gameOver = True
                    gameStateService.gameStart = False
                    gameStateService.startupCounter = 0
        #ghostsEaten[g.ghostId]
        elif (gameStateService.powerPellet and not g.isDead and not g.isEaten and pacManHitBox.colliderect(g.hitBox)):
            if g.ghostId == 0: #eliminate this coupling by pulling ghost into it's own class that doesn't need to be made every frame
                blinkyDead = True
            if g.ghostId == 1:
                inkyDead = True
            if g.ghostId == 2:
                pinkyDead = True
            if g.ghostId == 3:
                sueDead = True
            g.isDead = True

            #ghostsEaten[g.ghostId] = True
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
                    gameStateService.powerPellet = False
                    gameStateService.powerCounter = False
                    pacMan_x = 450
                    pacMan_y = 663
                    pacManDirection = Directions.RIGHT
                    direction_request = Directions.RIGHT

                    blinky_x = 56
                    blinky_y = 58
                    blinkyDirection = Directions.RIGHT
                    blinkyDead = False

                    inky_x = 440 
                    inky_y = 388
                    inkyDirection = Directions.UP
                    inkyDead = False

                    pinky_x = 440
                    pinky_y = 438
                    pinkyDirection = Directions.UP
                    pinkyDead = False

                    sue_x = 440
                    sue_y = 438
                    sueDirection = Directions.UP
                    sueDead = False
                    for g in ghosts: 
                        g.isEaten = False
                    #ghostsEaten = [False, False, False, False]   
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

    #reset the ghosts if they make it to the box
    if blinky.isInBox and blinky.isDead:
        blinkyDead = False
    if inky.isInBox and inky.isDead:
        inkyDead = False        
    if pinky.isInBox and pinky.isDead:
        pinkyDead = False
    if sue.isInBox and sue.isDead:
        sueDead = False
    pg.display.flip() ##draws the screen, I think
pg.quit() # End the game