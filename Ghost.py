class Ghost:
    def __init__(self, xPos, yPos, target, speed, image, dir, isDead, ghostId):
        self.xPos = xPos
        self.yPos = yPos
        self.centerX = xPos +22
        self.centerY = yPos + 22
        self.target = target
        self.speed = speed
        self.image = image
        self.direction = dir
        self.isDead = isDead
        self.ghostId = ghostId
        self.turns, self.isInBox = self.checkCollision()
        self.hitBox = self.draw()

    def draw(self):
        if (not powerPellet and not self.isDead) or (ghostsEaten[self.ghostId] and powerPellet and not self.isDead): #really gross
            screen.blit(self.image, (self.xPos, self.yPos))
        elif powerPellet and not self.isDead and not ghostsEaten[self.ghostId]:
            screen.blit(vulnerableGhostImage, (self.xPos, self.yPos))
        else:
            screen.blit(deadGhostImage, (self.xPos, self.yPos))
        self.hitBox = pg.rect.Rect((self.centerX - 18, self.centerY - 18), (36,36)) ## fudge this for more fair hitboxes 
        return self.hitBox

    def checkCollision(self): #returns valid turns and if ghost is in the box -> pretty gross code todo clean up
        
        self.isInBox = False
        tileHeight = (SCREEN_HEIGHT - 50) // 32
        tileWidth = SCREEN_WIDTH // 30
        fudgeFactor = 15
        self.turns = [False,False,False,False]
        if 0 < self.centerX // 30 < 29:
            if board[(self.centerY - fudgeFactor) // tileHeight][self.centerX // tileWidth] == 9: # checking for 9 to allow ghosts to move through gates
                self.turns[2] = True
            if board[self.centerY // tileHeight][(self.centerX - fudgeFactor) // tileWidth] < 3 \
                    or (board[self.centerY // tileHeight][(self.centerX - fudgeFactor) // tileWidth] == 9 and (
                    self.isInBox or self.isDead)):
                self.turns[1] = True
            if board[self.centerY // tileHeight][(self.centerX + fudgeFactor) // tileWidth] < 3 \
                    or (board[self.centerY // tileHeight][(self.centerX + fudgeFactor) // tileWidth] == 9 and (
                    self.isInBox or self.isDead)):
                self.turns[0] = True
            if board[(self.centerY + fudgeFactor) // tileHeight][self.centerX // tileWidth] < 3 \
                    or (board[(self.centerY + fudgeFactor) // tileHeight][self.centerX // tileWidth] == 9 and (
                    self.isInBox or self.isDead)):
                self.turns[3] = True
            if board[(self.centerY - fudgeFactor) // tileHeight][self.centerX // tileWidth] < 3 \
                    or (board[(self.centerY - fudgeFactor) // tileHeight][self.centerX // tileWidth] == 9 and (
                    self.isInBox or self.isDead)):
                self.turns[2] = True

            if self.direction == 2 or self.direction == 3:
                if 12 <= self.centerX % tileWidth <= 18:
                    if board[(self.centerY + fudgeFactor) // tileHeight][self.centerX // tileWidth] < 3 \
                            or (board[(self.centerY + fudgeFactor) // tileHeight][self.centerX // tileWidth] == 9 and (
                            self.isInBox or self.isDead)):
                        self.turns[3] = True
                    if board[(self.centerY - fudgeFactor) // tileHeight][self.centerX // tileWidth] < 3 \
                            or (board[(self.centerY - fudgeFactor) // tileHeight][self.centerX // tileWidth] == 9 and (
                            self.isInBox or self.isDead)):
                        self.turns[2] = True
                if 12 <= self.centerY % tileHeight <= 18:
                    if board[self.centerY // tileHeight][(self.centerX - tileWidth) // tileWidth] < 3 \
                            or (board[self.centerY // tileHeight][(self.centerX - tileWidth) // tileWidth] == 9 and (
                            self.isInBox or self.isDead)):
                        self.turns[1] = True
                    if board[self.centerY // tileHeight][(self.centerX + tileWidth) // tileWidth] < 3 \
                            or (board[self.centerY // tileHeight][(self.centerX + tileWidth) // tileWidth] == 9 and (
                            self.isInBox or self.isDead)):
                        self.turns[0] = True

            if self.direction == 0 or self.direction == 1:
                if 12 <= self.centerX % tileWidth <= 18:
                    if board[(self.centerY + fudgeFactor) // tileHeight][self.centerX // tileWidth] < 3 \
                            or (board[(self.centerY + fudgeFactor) // tileHeight][self.centerX // tileWidth] == 9 and (
                            self.isInBox or self.isDead)):
                        self.turns[3] = True
                    if board[(self.centerY - fudgeFactor) // tileHeight][self.centerX // tileWidth] < 3 \
                            or (board[(self.centerY - fudgeFactor) // tileHeight][self.centerX // tileWidth] == 9 and (
                            self.isInBox or self.isDead)):
                        self.turns[2] = True
                if 12 <= self.centerY % tileHeight <= 18:
                    if board[self.centerY // tileHeight][(self.centerX - fudgeFactor) // tileWidth] < 3 \
                            or (board[self.centerY // tileHeight][(self.centerX - fudgeFactor) // tileWidth] == 9 and (
                            self.isInBox or self.isDead)):
                        self.turns[1] = True
                    if board[self.centerY // tileHeight][(self.centerX + fudgeFactor) // tileWidth] < 3 \
                            or (board[self.centerY // tileHeight][(self.centerX + fudgeFactor) // tileWidth] == 9 and (
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
