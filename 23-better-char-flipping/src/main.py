
import pygame
from pygame.locals import *
from l01 import *

keys = global_vars.keys

screen, clock = init(810, 810)

m = IR("data/m_03_02.png", 10, 10)
m.img_normal = m.img
m.img_flipped = pygame.transform.flip(m.img, True, False)
m.img_pointer = m.img

fb = pygame.Surface((270, 270))

while True:
    fb.fill((14, 230, 230))
    pe()
    if (keys["left"]):
        m.img_pointer = m.img_flipped
    if (keys["right"]):
        m.img_pointer = m.img
    fb.blit(m.img_pointer, m.pos)
    m.x += keys["right"] - keys["left"]
    m.y += keys["down"] - keys["up"]
    screen.blit(pygame.transform.scale(fb, screen.get_size()), (0,0))
    clock.tick(60)
    pygame.display.update()
