
import pygame
from pygame.locals import *
from l01 import *

from Circle import Circle

SCREEN_W = 1920
SCREEN_H = 1080
WORLD_W = 1080 / 10
WORLD_H = 1080 / 10

screen, clock = init(SCREEN_W, SCREEN_H)
keys = global_vars.keys

m = Circle(20, 20, 2, (14, 240, 240, 255))

speed = 0.1
m_speed = 0.2
max_vel = 10

fb1 = pygame.Surface((WORLD_W, WORLD_H), pygame.SRCALPHA)
fb2 = pygame.Surface((WORLD_W, WORLD_H), pygame.SRCALPHA)

while True:
  # get input
  pe()

  screen.fill((20,20,20))
  fb1.fill((0, 0, 0, 20))

  #update
  m.vel.x += m_speed * ((keys["right"] or keys["d"]) - (keys["left"] or keys["a"]))
  m.vel.y += m_speed * ((keys["down"] or keys["s"]) - (keys["up"] or keys["w"]))
  
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
  m.draw(fb1)

  # handle screen
  fb2.blit(fb1,(0,0))
  screen.blit(pygame.transform.scale(fb2, (1080,1080)), (420,0))
  update_screen()

