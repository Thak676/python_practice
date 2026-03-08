
import pygame
from pygame.locals import *
from l01 import *

screen, clock = init(1280, 1080)
m = IR("i/soldat_02.png", 0, 0)
m.vy = 0
jump_sfx = pygame.mixer.Sound("i/jump_01.wav")
prev_space = False
jump_count = 0

fb = pygame.Surface((128, 108))

keys = global_vars.keys

while True:
  # get input
  pe()

  # update
  m.x += (keys["right"] or keys["d"])  - (keys["left"] or keys["a"])
  
  # gravity
  m.vy += 0.5
  m.y += m.vy
  
  if m.y > 50:
      m.y = 50
      m.vy = 0
      jump_count = 0
  
  if keys["space"] and not prev_space:
    if jump_count < 2:
      m.vy = -7
      jump_count += 1
      jump_sfx.play()
      print("jump")
  
  prev_space = keys["space"]

  prev_space = keys["space"]

  # draw
  m.draw(fb)

  # handle screen
  screen.blit(pygame.transform.scale(fb, screen.get_size()), (0,0))
  update_screen()
