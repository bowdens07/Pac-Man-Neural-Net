from direction import Directions


class PathingNode:
    def __init__(self, position:tuple[int,int]):
        self.neighbors: list[tuple[PathingNode, Directions]] = []
        self.row = position[0]
        self.col = position[1]
        self.position: tuple[int,int] = position #redudnant, but easier for reasoning


class PathingNodes: #uses the board to connect every pathing node to its neighbors
    def __init__(self, board): 
        self.nodeDict: dict[tuple[int,int],PathingNode] = {}
        
        #Key is Row, Value is dict of all cols that have a node on said row
        pathingNodeByRowDict = {
        2: [2,7,13,16,22,27],
        6: [2,7,10,13,16,19,22,27],
        9: [2,7,10,13,16,19,22,27],
        12: [10,13,16,19],
        15: [7,10,19,22],
        18: [10,19],
        21: [2,7,10,13,16,19,22,27],
        24:[2,4,7,10,13,16,19,22,25,27],
        27:[2,4,7,10,13,16,19,22,25,27],
        30: [2,13,16,27]
        }

        #Creates every node on the map and gives it a pathing node
        for key, val in pathingNodeByRowDict.items():
            for col in val:
                self.nodeDict[(key,col)] = PathingNode((key,col))
        self.__findNeighbors(self.nodeDict[(2,2)],board, [[1,0],[-1,0],[0,1],[0,-1]]) # connect all the nodes starting at (2,2)
        #No reason to make the algorithm smart enough to reach across the board, adding the last two neighbors that wrap the board manually
        self.nodeDict[(15,7)].neighbors.append([self.nodeDict[(15,22)],Directions.LEFT])
        self.nodeDict[(15,22)].neighbors.append([self.nodeDict[(15,7)],Directions.RIGHT])

    def __getSearchPosition(basePosition:tuple[int,int], searchDirection:list[list[int]], counter:int): #This takes a direction and multiplies it by a counter to make a new ROW, COL space to search
        return ((basePosition[0] + (counter * searchDirection[0])),(basePosition[1] + (counter * searchDirection[1])))

    def __interpretDirection(direction:list[int]) -> Directions:
        if direction == [0,1]:
            return Directions.UP
        if direction == [0,-1]:
            return Directions.DOWN
        if direction == [1,0]:
            return Directions.RIGHT
        if direction == [-1,0]:
            return Directions.LEFT

    def __getPossibleSearchDirections(curSearchDirection):
        #whever you came from, you cannot search back that way, cuts down on the algorithm redudancy 
        possibleSearchDirections = [[1,0],[-1,0],[0,1],[0,-1]] #right, left, up down
        if curSearchDirection == [0,1]:
            possibleSearchDirections.remove([0,-1])
        if curSearchDirection == [0,-1]:
            possibleSearchDirections.remove([0,1])
        if curSearchDirection == [1,0]:
            possibleSearchDirections.remove([-1,0])
        if curSearchDirection == [-1,0]:
            possibleSearchDirections.remove([1,0])
        return possibleSearchDirections
    
    def __reverseDirection(direction):
        if direction == Directions.RIGHT:
            return Directions.LEFT
        if direction == Directions.LEFT:
            return Directions.RIGHT
        if direction == Directions.UP:
            return Directions.DOWN
        if direction == Directions.DOWN:
            return Directions.UP
        
    def __findNeighbors(self, node:PathingNode,board:list[list[int]], searchDirections:list[list[int]]): #DFS search for neighbors in every cardinal direction, stops if hits a wall
        searchDirections = [[1,0],[-1,0],[0,1],[0,-1]] #right, left, up down
        for searchDirection in searchDirections:
            counter = 1
            searchPosition = PathingNodes.__getSearchPosition(node.position,searchDirection,counter)
            while searchPosition[0] < 33 and searchPosition[1] < 30 and board[searchPosition[0]][searchPosition[1]] < 3:
                if searchPosition in self.nodeDict.keys():
                    neighbor = self.nodeDict[searchPosition]
                    knownNeighbor = [existingNeighbor for existingNeighbor in node.neighbors if existingNeighbor[0] == neighbor]
                    if len(knownNeighbor) == 0:
                        directionToNeighbor = PathingNodes.__interpretDirection(searchDirection)
                        node.neighbors.append((neighbor, directionToNeighbor))
                        neighbor.neighbors.append((node, PathingNodes.__reverseDirection(directionToNeighbor)))
                        self.__findNeighbors(neighbor,board, PathingNodes.__getPossibleSearchDirections(searchDirection))
                    break
                counter += 1
                searchPosition = PathingNodes.__getSearchPosition(node.position,searchDirection,counter)


