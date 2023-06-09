# Default representation of the board
# 0 = empty black rectangle, 1 = dot, 2 = big dot, 3 = vertical line,
# 4 = horizontal line, 5 = top right, 6 = top left, 7 = bot left, 8 = bot right
# 9 = gate, # 10 = black rectangle, inacessible to everyone
default_board = [
[6, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 5],
[3, 6, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 5, 6, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 5, 3],
[3, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 3],
[3, 3, 1, 6, 4, 4, 5, 1, 6, 4, 4, 4, 5, 1, 3, 3, 1, 6, 4, 4, 4, 5, 1, 6, 4, 4, 5, 1, 3, 3],
[3, 3, 2, 3, 10, 10, 3, 1, 3, 10, 10, 10, 3, 1, 3, 3, 1, 3, 10, 10, 10, 3, 1, 3, 10, 10, 3, 2, 3, 3],
[3, 3, 1, 7, 4, 4, 8, 1, 7, 4, 4, 4, 8, 1, 7, 8, 1, 7, 4, 4, 4, 8, 1, 7, 4, 4, 8, 1, 3, 3],
[3, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 3],
[3, 3, 1, 6, 4, 4, 5, 1, 6, 5, 1, 6, 4, 4, 4, 4, 4, 4, 5, 1, 6, 5, 1, 6, 4, 4, 5, 1, 3, 3],
[3, 3, 1, 7, 4, 4, 8, 1, 3, 3, 1, 7, 4, 4, 5, 6, 4, 4, 8, 1, 3, 3, 1, 7, 4, 4, 8, 1, 3, 3],
[3, 3, 1, 1, 1, 1, 1, 1, 3, 3, 1, 1, 1, 1, 3, 3, 1, 1, 1, 1, 3, 3, 1, 1, 1, 1, 1, 1, 3, 3],
[3, 7, 4, 4, 4, 4, 5, 1, 3, 7, 4, 4, 5, 0, 3, 3, 0, 6, 4, 4, 8, 3, 1, 6, 4, 4, 4, 4, 8, 3],
[3, 10, 10, 10, 10, 10, 3, 1, 3, 6, 4, 4, 8, 0, 7, 8, 0, 7, 4, 4, 5, 3, 1, 3, 10, 10, 10, 10, 10, 3],
[3, 10, 10, 10, 10, 10, 3, 1, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 1, 3, 10, 10, 10, 10, 10, 3],
[8, 10, 10, 10, 10, 10, 3, 1, 3, 3, 0, 6, 4, 4, 9, 9, 4, 4, 5, 0, 3, 3, 1, 3, 10, 10, 10, 10, 10, 7],
[4, 4, 4, 4, 4, 4, 8, 1, 7, 8, 0, 3, 0, 0, 0, 0, 0, 0, 3, 0, 7, 8, 1, 7, 4, 4, 4, 4, 4, 4],
[0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
[4, 4, 4, 4, 4, 4, 5, 1, 6, 5, 0, 3, 0, 0, 0, 0, 0, 0, 3, 0, 6, 5, 1, 6, 4, 4, 4, 4, 4, 4],
[5, 10, 10, 10, 10, 10, 3, 1, 3, 3, 0, 7, 4, 4, 4, 4, 4, 4, 8, 0, 3, 3, 1, 3, 10, 10, 10, 10, 10, 6],
[3, 10, 10, 10, 10, 10, 3, 1, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 1, 3, 10, 10, 10, 10, 10, 3],
[3, 10, 10, 10, 10, 10, 3, 1, 3, 3, 0, 6, 4, 4, 4, 4, 4, 4, 5, 0, 3, 3, 1, 3, 10, 10, 10, 10, 10, 3],
[3, 6, 4, 4, 4, 4, 8, 1, 7, 8, 0, 7, 4, 4, 5, 6, 4, 4, 8, 0, 7, 8, 1, 7, 4, 4, 4, 4, 5, 3],
[3, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 3],
[3, 3, 1, 6, 4, 4, 5, 1, 6, 4, 4, 4, 5, 1, 3, 3, 1, 6, 4, 4, 4, 5, 1, 6, 4, 4, 5, 1, 3, 3],
[3, 3, 1, 7, 4, 5, 3, 1, 7, 4, 4, 4, 8, 1, 7, 8, 1, 7, 4, 4, 4, 8, 1, 3, 6, 4, 8, 1, 3, 3],
[3, 3, 2, 1, 1, 3, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 3, 1, 1, 2, 3, 3],
[3, 7, 4, 5, 1, 3, 3, 1, 6, 5, 1, 6, 4, 4, 4, 4, 4, 4, 5, 1, 6, 5, 1, 3, 3, 1, 6, 4, 8, 3],
[3, 6, 4, 8, 1, 7, 8, 1, 3, 3, 1, 7, 4, 4, 5, 6, 4, 4, 8, 1, 3, 3, 1, 7, 8, 1, 7, 4, 5, 3],
[3, 3, 1, 1, 1, 1, 1, 1, 3, 3, 1, 1, 1, 1, 3, 3, 1, 1, 1, 1, 3, 3, 1, 1, 1, 1, 1, 1, 3, 3],
[3, 3, 1, 6, 4, 4, 4, 4, 8, 7, 4, 4, 5, 1, 3, 3, 1, 6, 4, 4, 8, 7, 4, 4, 4, 4, 5, 1, 3, 3],
[3, 3, 1, 7, 4, 4, 4, 4, 4, 4, 4, 4, 8, 1, 7, 8, 1, 7, 4, 4, 4, 4, 4, 4, 4, 4, 8, 1, 3, 3],
[3, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 3],
[3, 7, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 8, 3],
[7, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 8]
         ]

def isValidPosition(position:tuple[int,int]) -> bool:
    return position[0] < len(default_board) and position[1] < len(default_board[0])

def isAWall(position:tuple[int,int])-> bool:
    return default_board[position[0]][position[1]] >= 3

def isInBox(position:tuple[int,int])->bool:
     return  (position[0] > 13 and position[0] < 17) and (position [1] > 11 and position[1] < 18)

def getNearestValidPosition(position:tuple[int,int]) -> tuple[int,int]:
    #put the position in valid bounds
    row, col = position
    if position[0] < 2:
        row = 2
    if position[0] > 30:    
        row = 30
    if position[1] < 2:
        col = 2
    if position[1] > 27:
        col = 27
    if(isAWall((row,col))):
        return __findNearestNonWallNonBoxTile((row,col))
    return row,col
    
def __findNearestNonWallNonBoxTile(position:tuple[int,int]):
    frontier = [position]
    while len(frontier) > 0:
        candidatePosition = frontier.pop(0)
        if isValidPosition(candidatePosition) and not isAWall(candidatePosition) and not isInBox(candidatePosition):
            return candidatePosition
        for neighbor in __getAdjacentPositions(candidatePosition):
            frontier.append(neighbor)
    print("Warning: Could not find a valid position for Inky from the starting point")

#Finds nearest pellet or power pellet tile on a given board
def findNearestPellet(position:tuple[int,int], board:list[list[int]]):
    frontier = [position]
    explored = []
    while len(frontier) > 0:
        candidatePosition = frontier.pop(0)
        if board[candidatePosition[0]][candidatePosition[1]] == 1 or board[candidatePosition[0]][candidatePosition[1]] == 2:
            return candidatePosition
        explored.append(candidatePosition)
        if isValidPosition(candidatePosition) and not isAWall(candidatePosition) and not isInBox(candidatePosition):
            for neighbor in __getAdjacentPositions(candidatePosition):
                if(neighbor not in explored):
                    frontier.append(neighbor)
    return None #Could not find pellet

def __getAdjacentPositions(position:tuple[int,int]):
    searchDirections = [[1,0],[-1,0],[0,1],[0,-1]] #right, left, up down
    neighbors = []
    for direction in searchDirections:
        candidatePosition = ((position[0] + direction[0]), (position[1] + direction[1]))
        if isValidPosition(candidatePosition):
            neighbors.append(candidatePosition)
    return neighbors

def getValidAdjacentPositions(position:tuple[int,int]) -> list[tuple[int,int]]:
    adjacentPositionsIncludingWalls = __getAdjacentPositions(position)
    validAdjacentPositions = []
    for candidatePosition in adjacentPositionsIncludingWalls:
        if not isAWall(candidatePosition) and not isInBox(candidatePosition):
            validAdjacentPositions.append(candidatePosition)
    return validAdjacentPositions

def getRemainingPellets(board)-> int:
    remainingPellets = 0
    for i in range(len(board)):
        for j in range(len(board[i])):  
            if board[i][j] == 1 or board[i][j] == 2:
                remainingPellets += 1
    return remainingPellets


#print(len(default_board))
#print(len(default_board[0]))
#print(getRemainingPellets(default_board))