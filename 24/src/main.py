
import pygame
from l01 import *
keys = global_vars.keys

screen, clock = init(1760, 1024)

m = IR("data/m_03_02.png", 10, 10)
m.speed = 0.3
background = IR("data/background.png", 0, 0)

rock = IR("data/rock 01.png", 64, 64)

fb = pygame.Surface((256, 160))

while True:
    # get input
    pe()

    # process input
    m.x += keys["right"] - keys["left"]
    m.y += keys["down"] - keys["up"]

    # draw to fb
    fb.fill((14, 255, 255))
    background.draw(fb)
    m.draw(fb)
    rock.draw(fb)

    # handle screen
    screen.blit(pygame.transform.scale(fb, screen.get_size()), (0,0))
    clock.tick(60)
    pygame.display.update()
