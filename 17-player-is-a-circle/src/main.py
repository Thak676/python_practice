
import pygame
from pygame.locals import *
from l01 import *

from Circle import Circle

screen, clock = init(980, 980)
keys = global_vars.keys
m: Circle = Circle(10, 10, 4, (255,0,0))
fb = pygame.Surface((270, 270))

while True:
  # get input
  pe()

  # update
  m.x += keys["right"] - keys["left"]
  m.y += keys["down"] - keys["up"]

  # draw to fb
  fb.fill((0,0,0))
  m.draw(fb)

  # screen
  screen.blit(pygame.transform.scale(fb, screen.get_size()), (0, 0))
  update_screen()
