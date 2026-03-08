
import math
import pygame
from pygame.locals import *
from l01 import *
from player import Player
from slerp import slerp
keys = global_vars.keys
import sys

screen, clock = init(640, 640)

player: Player = Player((60, 60, 255), 10, 10, 40, 40)

# t: float = 0.0
# dt: float = 0.001
speed: float = 0.3

while True:
    screen.fill((160, 160, 160))
    pe()
    player.x += (keys["right"] - keys["left"]) * speed
    # player.y += (keys["down"] - keys["up"]) * speed

    pygame.draw.rect(screen, player.color, player.rect)

    # player.x = slerp(10, 590, (math.sin(t * math.pi * 2) + 1) / 2)
    # t = (t + dt) % 1.0
    # t = (t + dt)

    pygame.display.flip()
