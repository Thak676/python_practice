
import pygame
from l01 import *
keys = global_vars.keys

screen, clock = init(1920, 1280)

m = IR("data/m_03_02.png", 10, 10)
background = IR("data/desert_scene_01.png", 0, 0)

fb = pygame.Surface((192, 128))

while True:
    # get input
    pe()

    # process input
    m.x += keys["right"] - keys["left"]
    m.y += keys["down"] - keys["up"]

    # draw to fb
    fb.fill((14, 255, 255))
    background.draw(fb)
    fb.blit(m.img, m.pos)

    # handle screen
    screen.blit(pygame.transform.scale(fb, screen.get_size()), (0,0))
    pygame.display.update()
