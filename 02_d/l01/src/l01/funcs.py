
import pygame
import sys
from pygame.locals import *
from . import global_vars
from typing import Callable

#global_vars.screen = pygame.display.set_mode((x, y), pygame.FULLSCREEN)
def init(x: int, y: int):
	pygame.init()
	global_vars.screen = pygame.display.set_mode((x, y))
	global_vars.clock = pygame.time.Clock()
	return global_vars.screen, global_vars.clock
	
def quit():
	pygame.quit()
	sys.exit()

def fill_screen(r: int, g: int, b: int):
	global_vars.screen.fill((r, g, b))
fs: callable = fill_screen

def update_screen():
	pygame.display.update()
	global_vars.clock.tick(60)
us: callable = update_screen

def process_events():
    keys = global_vars.keys
    for event in pygame.event.get():
        if event.type == QUIT:
            quit()
        if event.type == KEYDOWN:
            if event.key == K_UP:
                keys["up"] = True
            if event.key == K_DOWN:
                keys["down"] = True
            if event.key == K_LEFT:
                keys["left"] = True
            if event.key == K_RIGHT:
                keys["right"] = True
            if event.key == K_w:
                keys["w"] = True
            if event.key == K_s:
                keys["s"] = True
            if event.key == K_a:
                keys["a"] = True
            if event.key == K_d:
                keys["d"] = True
            if event.key == K_SPACE:
                keys["space"] = True
        if event.type == KEYUP:
            if event.key == K_UP:
                keys["up"] = False
            if event.key == K_DOWN:
                keys["down"] = False
            if event.key == K_w:
                keys["w"] = False
            if event.key == K_s:
                keys["s"] = False
            if event.key == K_a:
                keys["a"] = False
            if event.key == K_d:
                keys["d"] = False
            if event.key == K_LEFT:
                keys["left"] = False
            if event.key == K_RIGHT:
                keys["right"] = False
            if event.key == K_SPACE:
                keys["space"] = False
pe: callable = process_events

