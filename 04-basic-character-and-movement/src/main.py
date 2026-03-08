
import pygame
from pygame.locals import *
from l01 import *

screen, clock = init(980, 980)

m = IR("i/theodore_04.png", 10, 10)

fb = pygame.Surface((270, 270))

k = global_vars.keys
keys = global_vars.keys

while True:
    screen.fill((14, 250, 250))
    m.draw(fb)
    pe()

    m.x += keys["right"] - keys["left"]
    m.y += keys["down"] - keys["up"]

    screen.blit(pygame.transform.scale(fb, (980, 980)), (0,0))
    update_screen()
