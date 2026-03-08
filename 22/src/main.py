
import pygame
from l01 import *
keys = global_vars.keys

screen, clock = init(640, 640)

class Grid:
    def __init__(self, x, y):
       self.x = x
       self.y = y

grid: Grid = Grid(16, 16)

class Player:
    def __init__(self, x, y):
       self.x = x
       self.y = y
m = Player(300, 300)

speed = 3.0

while True:
    pe()
    m.x += (keys["right"] - keys["left"]) * speed
    m.y += (keys["down"] - keys["up"]) * speed
    
    i: int = 0
    j: int = 0
    while (i < 16):
        j = 0
        while (j < 16):
            pygame.draw.rect(screen, (16 * i, 16 * j, 255), pygame.Rect(i * 40, j * 40, 40, 40))
            j += 1
        i += 1
    pygame.draw.rect(screen, (0, 255, 0), pygame.Rect(m.x, m.y, 40, 40))
    update_screen()

