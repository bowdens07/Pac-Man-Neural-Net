import pygame as pg
import math


PI = math.pi #TODO: remove after replacing rendering with sprites


def draw_board(screen,board, boardColor, screen_height, screen_width, flicker):
    tile_height = (screen_height - 50) // 32 #32 vertical tiles, leave 50 px for UI elements at bottom (may remove)
    half_tile_height = tile_height * 0.5 

    tile_width = screen_width // 30 #30 horizontal tiles
    half_tile_width = tile_width * 0.5 

    #pg.draw.rect(screen, (255,0,0), pg.Rect(345,380,210,110)) box
    #pg.draw.rect(screen, (0,0,255), pg.Rect(400,100,50,50)) leave box target
    pg.draw.rect(screen, (0,0,255), pg.Rect(350,450,200,30)) #revive zone

    # not thrilled with this render method. It's a lot of math. Maybe consider some static calculations for each relevant position? Let's clock performance later to see if we train fast enough
    #I want to use sprites, this is going to kill performance if we draw all these shapes every frame.
    for row in range(len(board)):
        for column in range(len(board[row])):
            if board[row][column] == 1:
                pg.draw.circle(screen, 'white', (column * tile_width + (half_tile_width), row * tile_height + (half_tile_height)),4) ##consider making this a private method to calc circle size
            elif board[row][column] == 2 and not flicker:
                pg.draw.circle(screen, 'white', (column * tile_width + (half_tile_width), row * tile_height + (half_tile_height)),10)
            elif board[row][column] == 3:
                pg.draw.line(screen,boardColor, ((column * tile_width + half_tile_width), row * tile_height), ((column * tile_width + half_tile_width), row * tile_height + tile_height), 3)
            elif board[row][column] == 4:
                pg.draw.line(screen,boardColor, ((column * tile_width), row * tile_height + half_tile_height), ((column * tile_width + tile_width), row * tile_height + half_tile_height), 3)
            elif board[row][column] == 5:
                pg.draw.arc(screen, boardColor, [(column * tile_width - (tile_width * 0.4)) - 2, (row * tile_height + (0.5 * tile_height)), tile_width, tile_height],
                                0, PI / 2, 3)
            elif board[row][column] == 6:
                pg.draw.arc(screen, boardColor,
                                [(column * tile_width + (tile_width * 0.5)), (row * tile_height + (0.5 * tile_height)), tile_width, tile_height], PI / 2, PI, 3)
            elif board[row][column] == 7:
                pg.draw.arc(screen, boardColor, [(column * tile_width + (tile_width * 0.5)), (row * tile_height - (0.4 * tile_height)), tile_width, tile_height], PI,
                                3 * PI / 2, 3)
            elif board[row][column] == 8:
                pg.draw.arc(screen, boardColor,
                                [(column * tile_width - (tile_width * 0.4)) - 2, (row * tile_height - (0.4 * tile_height)), tile_width, tile_height], 3 * PI / 2,
                                2 * PI, 3)
            elif board[row][column] == 9: #gate for the ghosts
                pg.draw.line(screen,'white', ((column * tile_width), row * tile_height + half_tile_height), ((column * tile_width + tile_width), row * tile_height + half_tile_height), 3)