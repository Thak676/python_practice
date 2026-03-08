
import pygame
from pygame.locals import *
from l01 import *

Vec2 = pygame.math.Vector2

from Circle import Circle

screen, clock = init(980, 980)
m = IR("i/theodore_04.png", 10, 10)
fb = pygame.Surface((270, 270))
keys = global_vars.keys

enemies = []
speed = 1.0
framecount = 0

while True:

    # get input
    pe()

    # update
    framecount += 1
    if (framecount % 60 == 0):
        c1: Circle = Circle()
        enemies.append(c1)
        print(enemies)
        
    m.x += keys["right"] - keys["left"]
    m.y += keys["down"] - keys["up"]
    for c in enemies:
        vec2 = Vec2(m.x - c.x, m.y - c.y)
        vec2.normalize_ip()
        c.pos += vec2 * speed

    # draw
    screen.fill((100, 100, 100))
    m.draw(fb)
    for circ in enemies:
        pygame.draw.circle(fb, (255, 0, 0), circ.pos, 4)

    # handle screen
    screen.blit(pygame.transform.scale(fb, (980, 980)), (0,0))
    update_screen()
