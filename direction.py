from enum import IntEnum

class Directions(IntEnum):
    RIGHT = 0,
    LEFT = 1,
    UP = 2,
    DOWN = 3

    def reverseDirection(direction):
        if direction == Directions.RIGHT:
            return Directions.LEFT
        if direction == Directions.LEFT:
            return Directions.RIGHT
        if direction == Directions.UP:
            return Directions.DOWN
        if direction == Directions.DOWN:
            return Directions.UP
