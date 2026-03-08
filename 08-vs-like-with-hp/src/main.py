
import pygame
from pygame.locals import *
from l01 import init, IR, global_vars, process_events, update_screen

from update_and_draw import update_and_draw

CAMERA_W = 270
CAMERA_H = 270

screen, clock = init(980, 980)
m = IR("i/theodore_04.png", 0, 0)
m.hp = 100
keys = global_vars.keys

fb = pygame.Surface((CAMERA_W, CAMERA_H)) 

while True:
    
    # get input
    process_events()

    # update and draw
    update_and_draw(fb,(CAMERA_W, CAMERA_H), m, keys)

    # handle screen
    screen.blit(pygame.transform.scale(fb, (980, 980)), (0,0))
    update_screen()
