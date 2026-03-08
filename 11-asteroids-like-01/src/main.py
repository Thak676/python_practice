
import pygame
from pygame.locals import *
from l01 import *

from Circle import Circle

WORLD_W = 640
WORLD_H = 640

screen, clock = init(WORLD_W, WORLD_H)
keys = global_vars.keys

m = Circle(20, 20, 4, (14, 240, 240))

speed = 0.1
max_vel = 50

while True:
  # get input
  pe()

  #update
  m.vel.x += keys["right"] - keys["left"]
  m.vel.y += keys["down"] - keys["up"]
  
  if m.vel.length() > max_vel:
    m.vel.scale_to_length(max_vel)
    
  m.pos += m.vel * speed

  if m.x > WORLD_W:
    m.x = 0
  elif m.x < 0:
    m.x = WORLD_W
    
  if m.y > WORLD_H:
    m.y = 0
  elif m.y < 0:
    m.y = WORLD_H

  #draw
  m.draw(screen)

  # handle screen
  update_screen()

