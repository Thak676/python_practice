
import pygame
from pygame.locals import *
from l01 import *

import random

CAMERA_WIDTH = 270
CAMERA_HEIGHT = 270
SCREEN_WIDTH = 980
SCREEN_HEIGHT = 980

screen, clock = init(SCREEN_WIDTH, SCREEN_HEIGHT)

m = IR("i/theodore_04.png", 10, 10)

fb = pygame.Surface((CAMERA_WIDTH, CAMERA_HEIGHT))

k = global_vars.keys
keys = global_vars.keys

class Entity:
    def __init__(self):
        self.x: number = random.randint(0, CAMERA_WIDTH)
        self.y: number = random.randint(0, CAMERA_HEIGHT)


entity: Entity = Entity()

#randX: number = random.randint(0, CAMERA_WIDTH)
#randY: number = random.randint(0, CAMERA_HEIGHT)

while True:

    # get input
    pe()

    # update
    m.x += keys["right"] - keys["left"]
    m.y += keys["down"] - keys["up"]


    # draw to fb
    # fb.fill((0, 0, 0))
    m.draw(fb)
    pygame.draw.circle(fb, (255, 0, 0), m.pos, 4)

    # draw screen
    screen.blit(pygame.transform.scale(fb, (SCREEN_WIDTH, SCREEN_HEIGHT)), (0,0))
    update_screen()

