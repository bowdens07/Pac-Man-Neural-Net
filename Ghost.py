#this class relies on a lot of globals. Consider some services to maybe clean stuff up
from GameStateService import GameStateService
import pygame as pg

class Ghost:
    def __init__(self, gameStateService: GameStateService, screen: pg.Surface, board:list[list[int]], xPos, yPos, target, speed, image, dir, isDead, isEaten, ghostId, vulnGhostImage, deadGhostImage):
        self.gameStateService = gameStateService
        self.screen = screen
        self.board = board
        self.xPos = xPos
        self.yPos = yPos
        self.target = target
        self.speed = speed
        self.image = image
        self.direction = dir
        self.isDead = isDead
        self.isEaten = isEaten
        self.ghostId = ghostId
        self.turns, self.isInBox = self.checkCollision()
        self.vulnerableGhostImage = vulnGhostImage
        self.deadGhostImage = deadGhostImage

        
    def getCenterX(self):
        return self.xPos + 22
    def getCenterY(self):
        return self.yPos + 22

    def setNewBoard(self, board:list[list[int]]): #necessary evil, board must be reset on game reset
        self.board = board


    def draw(self):
        if (not self.gameStateService.powerPellet and not self.isDead) or (self.isEaten and self.gameStateService.powerPellet and not self.isDead): #really gross
            self.screen.blit(self.image, (self.xPos, self.yPos))
        elif self.gameStateService.powerPellet and not self.isDead and not self.isEaten:
            self.screen.blit(self.vulnerableGhostImage, (self.xPos, self.yPos))
        else:
            self.screen.blit(self.deadGhostImage, (self.xPos, self.yPos))
        self.hitBox = pg.rect.Rect((self.getCenterX() - 18, self.getCenterY() - 18), (36,36)) ## fudge this for more fair hitboxes 

    def checkCollision(self): #returns valid turns and if ghost is in the box -> pretty gross code todo clean up
        
        self.isInBox = False
        tileHeight = (self.screen.get_height() - 50) // 32
        tileWidth = self.screen.get_width() // 30
        fudgeFactor = 15
        self.turns = [False,False,False,False]
        if 0 < self.getCenterX() // 30 < 29:
            if self.board[(self.getCenterY() - fudgeFactor) // tileHeight][self.getCenterX() // tileWidth] == 9: # checking for 9 to allow ghosts to move through gates
                self.turns[2] = True
            if self.board[self.getCenterY() // tileHeight][(self.getCenterX() - fudgeFactor) // tileWidth] < 3 \
                    or (self.board[self.getCenterY() // tileHeight][(self.getCenterX() - fudgeFactor) // tileWidth] == 9 and (
                    self.isInBox or self.isDead)):
                self.turns[1] = True
            if self.board[self.getCenterY() // tileHeight][(self.getCenterX() + fudgeFactor) // tileWidth] < 3 \
                    or (self.board[self.getCenterY() // tileHeight][(self.getCenterX() + fudgeFactor) // tileWidth] == 9 and (
                    self.isInBox or self.isDead)):
                self.turns[0] = True
            if self.board[(self.getCenterY() + fudgeFactor) // tileHeight][self.getCenterX() // tileWidth] < 3 \
                    or (self.board[(self.getCenterY() + fudgeFactor) // tileHeight][self.getCenterX() // tileWidth] == 9 and (
                    self.isInBox or self.isDead)):
                self.turns[3] = True
            if self.board[(self.getCenterY() - fudgeFactor) // tileHeight][self.getCenterX() // tileWidth] < 3 \
                    or (self.board[(self.getCenterY() - fudgeFactor) // tileHeight][self.getCenterX() // tileWidth] == 9 and (
                    self.isInBox or self.isDead)):
                self.turns[2] = True

            if self.direction == 2 or self.direction == 3:
                if 12 <= self.getCenterX() % tileWidth <= 18:
                    if self.board[(self.getCenterY() + fudgeFactor) // tileHeight][self.getCenterX() // tileWidth] < 3 \
                            or (self.board[(self.getCenterY() + fudgeFactor) // tileHeight][self.getCenterX() // tileWidth] == 9 and (
                            self.isInBox or self.isDead)):
                        self.turns[3] = True
                    if self.board[(self.getCenterY() - fudgeFactor) // tileHeight][self.getCenterX() // tileWidth] < 3 \
                            or (self.board[(self.getCenterY() - fudgeFactor) // tileHeight][self.getCenterX() // tileWidth] == 9 and (
                            self.isInBox or self.isDead)):
                        self.turns[2] = True
                if 12 <= self.getCenterY() % tileHeight <= 18:
                    if self.board[self.getCenterY() // tileHeight][(self.getCenterX() - tileWidth) // tileWidth] < 3 \
                            or (self.board[self.getCenterY() // tileHeight][(self.getCenterX() - tileWidth) // tileWidth] == 9 and (
                            self.isInBox or self.isDead)):
                        self.turns[1] = True
                    if self.board[self.getCenterY() // tileHeight][(self.getCenterX() + tileWidth) // tileWidth] < 3 \
                            or (self.board[self.getCenterY() // tileHeight][(self.getCenterX() + tileWidth) // tileWidth] == 9 and (
                            self.isInBox or self.isDead)):
                        self.turns[0] = True

            if self.direction == 0 or self.direction == 1:
                if 12 <= self.getCenterX() % tileWidth <= 18:
                    if self.board[(self.getCenterY() + fudgeFactor) // tileHeight][self.getCenterX() // tileWidth] < 3 \
                            or (self.board[(self.getCenterY() + fudgeFactor) // tileHeight][self.getCenterX() // tileWidth] == 9 and (
                            self.isInBox or self.isDead)):
                        self.turns[3] = True
                    if self.board[(self.getCenterY() - fudgeFactor) // tileHeight][self.getCenterX() // tileWidth] < 3 \
                            or (self.board[(self.getCenterY() - fudgeFactor) // tileHeight][self.getCenterX() // tileWidth] == 9 and (
                            self.isInBox or self.isDead)):
                        self.turns[2] = True
                if 12 <= self.getCenterY() % tileHeight <= 18:
                    if self.board[self.getCenterY() // tileHeight][(self.getCenterX() - fudgeFactor) // tileWidth] < 3 \
                            or (self.board[self.getCenterY() // tileHeight][(self.getCenterX() - fudgeFactor) // tileWidth] == 9 and (
                            self.isInBox or self.isDead)):
                        self.turns[1] = True
                    if self.board[self.getCenterY() // tileHeight][(self.getCenterX() + fudgeFactor) // tileWidth] < 3 \
                            or (self.board[self.getCenterY() // tileHeight][(self.getCenterX() + fudgeFactor) // tileWidth] == 9 and (
                            self.isInBox or self.isDead)):
                        self.turns[0] = True
        else:
            self.turns[0] = True
            self.turns[1] = True
        if 350 < self.xPos < 550 and 370 < self.yPos < 480:
            self.isInBox = True
        else:
            self.isInBox = False
        return self.turns, self.isInBox

    def moveSue(self): #TODO bugged - if the ghosts move off screen they get stuck
        if self.direction == 0:
            if self.target[0] > self.xPos and self.turns[0]:
                self.xPos += self.speed
            elif not self.turns[0]:
                if self.target[1] > self.yPos and self.turns[3]:
                    self.direction = 3
                    self.yPos += self.speed
                elif self.target[1] < self.yPos and self.turns[2]:
                    self.direction = 2
                    self.yPos -= self.speed
                elif self.target[0] < self.xPos and self.turns[1]:
                    self.direction = 1
                    self.xPos -= self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.yPos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.yPos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.xPos -= self.speed
            elif self.turns[0]:
                if self.target[1] > self.yPos and self.turns[3]:
                    self.direction = 3
                    self.yPos += self.speed
                if self.target[1] < self.yPos and self.turns[2]:
                    self.direction = 2
                    self.yPos -= self.speed
                else:
                    self.xPos += self.speed
        elif self.direction == 1:
            if self.target[1] > self.yPos and self.turns[3]:
                self.direction = 3
            elif self.target[0] < self.xPos and self.turns[1]:
                self.xPos -= self.speed
            elif not self.turns[1]:
                if self.target[1] > self.yPos and self.turns[3]:
                    self.direction = 3
                    self.yPos += self.speed
                elif self.target[1] < self.yPos and self.turns[2]:
                    self.direction = 2
                    self.yPos -= self.speed
                elif self.target[0] > self.xPos and self.turns[0]:
                    self.direction = 0
                    self.xPos += self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.yPos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.yPos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.xPos += self.speed
            elif self.turns[1]:
                if self.target[1] > self.yPos and self.turns[3]:
                    self.direction = 3
                    self.yPos += self.speed
                if self.target[1] < self.yPos and self.turns[2]:
                    self.direction = 2
                    self.yPos -= self.speed
                else:
                    self.xPos -= self.speed
        elif self.direction == 2:
            if self.target[0] < self.xPos and self.turns[1]:
                self.direction = 1
                self.xPos -= self.speed
            elif self.target[1] < self.yPos and self.turns[2]:
                self.direction = 2
                self.yPos -= self.speed
            elif not self.turns[2]:
                if self.target[0] > self.xPos and self.turns[0]:
                    self.direction = 0
                    self.xPos += self.speed
                elif self.target[0] < self.xPos and self.turns[1]:
                    self.direction = 1
                    self.xPos -= self.speed
                elif self.target[1] > self.yPos and self.turns[3]:
                    self.direction = 3
                    self.yPos += self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.xPos -= self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.yPos += self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.xPos += self.speed
            elif self.turns[2]:
                if self.target[0] > self.xPos and self.turns[0]:
                    self.direction = 0
                    self.xPos += self.speed
                elif self.target[0] < self.xPos and self.turns[1]:
                    self.direction = 1
                    self.xPos -= self.speed
                else:
                    self.yPos -= self.speed
        elif self.direction == 3:
            if self.target[1] > self.yPos and self.turns[3]:
                self.yPos += self.speed
            elif not self.turns[3]:
                if self.target[0] > self.xPos and self.turns[0]:
                    self.direction = 0
                    self.xPos += self.speed
                elif self.target[0] < self.xPos and self.turns[1]:
                    self.direction = 1
                    self.xPos -= self.speed
                elif self.target[1] < self.yPos and self.turns[2]:
                    self.direction = 2
                    self.yPos -= self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.yPos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.xPos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.xPos += self.speed
            elif self.turns[3]:
                if self.target[0] > self.xPos and self.turns[0]:
                    self.direction = 0
                    self.xPos += self.speed
                elif self.target[0] < self.xPos and self.turns[1]:
                    self.direction = 1
                    self.xPos -= self.speed
                else:
                    self.yPos += self.speed
        if self.xPos < -30:
            self.xPos = 900
        elif self.xPos > 900:
            self.xPos - 30
        return self.xPos, self.yPos, self.direction    