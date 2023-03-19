import pygame as pg
from direction import Directions
from board import default_board
from graphics import draw_board

pg.init()

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 950


# more graphics logic
direction_request = Directions.RIGHT
direction = Directions.RIGHT
counter = 0
pacManImages = []
pacManImages.append(pg.transform.scale(pg.image.load(f'assets/PacManClose.png'),(45,45)))
pacManImages.append(pg.transform.scale(pg.image.load(f'assets/PacManMid.png'),(45,45)))
pacManImages.append(pg.transform.scale(pg.image.load(f'assets/PacManOpen.png'),(45,45)))
#end graphics logic

pacMan_x = 450
pacMan_y = 663
pacManVelocity = 0

def getPacManCenterX():
    return pacMan_x + 23

def getPacManCenterY():
    return pacMan_y + 24

screen = pg.display.set_mode([SCREEN_WIDTH,SCREEN_HEIGHT])
timer = pg.time.Clock()
fps = 60 #This might need to be uncapped for training
font = pg.font.Font('freesansbold.ttf',20) #arbitrary
board = default_board
boardColor = 'blue'
flicker = False
availableTurns = [False,False,False,False] # R, L, U, D -> make this a class

def isInMiddleOfTileX():
    tile_width = SCREEN_WIDTH // 30 #30 horizontal tiles
    if 12 <= getPacManCenterX() % tile_width <= 18:
        return True
    return False

def isInMiddleOfTileY():
    tile_height = SCREEN_HEIGHT // 30 #30 horizontal tiles
    if 12 <= getPacManCenterY() % tile_height <= 18:
        return True
    return False

## More likely I want to make a velocity system -> see if position + velocity is valid, then decide to move or not.
def getValidTurns(xPos):
    turns = [False,False,False,False]
    tile_height = (SCREEN_HEIGHT - 50) // 32 #32 vertical tiles, leave 50 px for UI elements at bottom (may remove)
    tile_width = SCREEN_WIDTH // 30 #30 horizontal tiles
    fudgeFactor = 15
    validTurnstring = ""
    # check collision based on xPos and yPos of player +/- fudgeFactor 
    if xPos //30 < 29:
        #Can I reverse Direction?
        if direction == Directions.RIGHT: # <3 because board values 0,1,2 can be moved into, rest are walls
            if board[getPacManCenterY() // tile_height][(getPacManCenterX() - fudgeFactor) // tile_width]  < 3:
                turns[1] = True
                validTurnstring += "can turn left"
        if direction == Directions.LEFT:
            if board[getPacManCenterY() // tile_height][(getPacManCenterX() + fudgeFactor) // tile_width]  < 3:
                turns[0] = True
                validTurnstring += "can turn right"
        if direction == Directions.UP:
            if board[(getPacManCenterY() + fudgeFactor) // tile_height][getPacManCenterX() // tile_width]  < 3:
                turns[3] = True
                validTurnstring += "can turn up"
        if direction == Directions.DOWN:
            if board[(getPacManCenterY() - fudgeFactor) // tile_height][getPacManCenterX() // tile_width]  < 3:
                turns[2] = True
                validTurnstring += "can turn down1"

        #Can I turn up or down?
        if direction == Directions.UP or direction == Directions.DOWN:
            if(isInMiddleOfTileX()): #IF pac man is approximately horiztonatally in middle of tile
                if board[(getPacManCenterY() + fudgeFactor) // tile_height][getPacManCenterX() // tile_width] < 3:
                    turns[3] = True
                validTurnstring += "can turn down2"
                if board[(getPacManCenterY() - fudgeFactor) // tile_height][getPacManCenterX() // tile_width] < 3:
                    turns[2] = True
                validTurnstring += "can turn up"
            if(isInMiddleOfTileY()): #IF pac man is approximately horiztonatally in middle of tile
                if board[getPacManCenterY() // tile_height][(getPacManCenterX() - tile_width) // tile_width] < 3:
                    turns[1] = True
                    validTurnstring += "can turn left"
                if board[getPacManCenterY() // tile_height][getPacManCenterX() + tile_width // tile_width] < 3:
                    turns[0] = True
                    validTurnstring += "can turn right"
        #Can I turn left or right?
        if direction == Directions.RIGHT or direction == Directions.LEFT:
            if(isInMiddleOfTileX()): #IF pac man is approximately horiztonatally in middle of tile
                if board[(getPacManCenterY() + fudgeFactor) // tile_height][getPacManCenterX() // tile_width] < 3:
                    turns[3] = True
                validTurnstring += "can turn down3"
                if board[(getPacManCenterY() - fudgeFactor) // tile_height][getPacManCenterX() // tile_width] < 3:
                    turns[2] = True
                validTurnstring += "can turn up"
            if(isInMiddleOfTileY()): #IF pac man is approximately horiztonatally in middle of tile
                if board[getPacManCenterY() // tile_height][(getPacManCenterX() - fudgeFactor) // tile_width] < 3:
                    turns[1] = True
                    validTurnstring += "can turn left"
                if board[getPacManCenterY() // tile_height][getPacManCenterX() + fudgeFactor // tile_width] < 3:
                    turns[0] = True
                    validTurnstring += "can turn right"
    else: #This is for wrapping around the board horizontally. If you want to wrap vertically, this code must change
        turns[0] = True
        turns[1] = True
    print(validTurnstring)
    return turns
    
def movePacMan(pacManX, pacManY):
    if direction == Directions.RIGHT and availableTurns[Directions.RIGHT]:
        pacManX += pacManVelocity
    elif direction == Directions.LEFT and availableTurns[Directions.LEFT]:
        pacManX -= pacManVelocity
    elif direction == Directions.UP and availableTurns[Directions.UP]:
        pacManY -= pacManVelocity
    elif direction == Directions.DOWN and availableTurns[Directions.DOWN]:
        pacManY += pacManVelocity
    return pacManX, pacManY
    

runGame = True

def drawPacMan():
    if direction == Directions.RIGHT: 
        screen.blit(pacManImages[counter // 9], (pacMan_x,pacMan_y))
    elif direction == Directions.LEFT: 
        screen.blit(pg.transform.flip(pacManImages[counter // 9],True,False), (pacMan_x,pacMan_y))
    elif direction == Directions.UP: 
        screen.blit(pg.transform.rotate(pacManImages[counter // 9],90), (pacMan_x,pacMan_y))
    elif direction == Directions.DOWN: 
        screen.blit(pg.transform.rotate(pacManImages[counter // 9],-90), (pacMan_x,pacMan_y))        

#Main game loop
while runGame:
    timer.tick(fps)

    #counter stuff animates pac man chomping, not in love with it, but hey
    if counter < 26:
        counter +=1
        if counter > 3:
            flicker = False
    else:
        counter = 0
        flicker = True

    screen.fill('black')
    
    #availableTurns = getValidTurns(getPacManCenterX())
    #pacMan_x, pacMan_y = movePacMan(pacMan_x, pacMan_y)
    draw_board(screen, board, boardColor, SCREEN_HEIGHT, SCREEN_WIDTH, flicker)
    drawPacMan()

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
        if event.type == pg.KEYUP:
            if event.key == pg.K_RIGHT and direction_request == Directions.RIGHT:
                direction_request = Directions.RIGHT
                print("requesting Right")
            if event.key == pg.K_LEFT  and direction_request == Directions.LEFT:
                direction_request = Directions.LEFT
                print("requesting Left")
            if event.key == pg.K_UP  and direction_request == Directions.UP:
                direction_request = Directions.UP
                print("requesting Up")
            if event.key == pg.K_DOWN  and direction_request == Directions.DOWN: 
                direction_request = Directions.DOWN      
                print("requesting Down")
        #set the new direction if you can
        for direction in Directions:
            if direction_request == direction and availableTurns[direction]:
                direction = direction_request
                print("Set Direction " + direction.name)

        if pacMan_x > 900: #wrap pac man if he moves off screen, magic numbers are for visuals
            pacMan_x = -47
        elif pacMan_x < -50:
            pacMan_x = 897
    pg.display.flip() ##draws the screen, I think
pg.quit() # End the game