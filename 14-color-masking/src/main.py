
import pygame
from pygame.locals import *
from l01 import *
import math

SCREEN_W = 1080
SCREEN_H = 1080

screen, clock = init(SCREEN_W, SCREEN_H)
spacebase = IR("i/spacebase_01.png", 5, 5)
spacebase_green = IR("i/spacebase_01_green_only.png", 5, 5)
spacebase_red = IR("i/spacebase_01_red_only.png", 5, 5)
spacebase_blue = IR("i/spacebase_01_blue_only.png", 5, 5)

color_mask = pygame.mask.from_surface(spacebase_green.img)
color_mask_red = pygame.mask.from_surface(spacebase_red.img)
color_mask_blue = pygame.mask.from_surface(spacebase_blue.img)

fb = pygame.Surface((108, 108))

framecount: int = 0
pulse_speed: float = 0.02

while True:
  # calculate dynamic pulse value (100 to 255)
  pulse_val = 180 + abs(math.sin(framecount * pulse_speed)) * 75 # add number and mult number need to add up to 255 to keep color within correct bounds
  
  # create surface with dynamic green component
  color_change_surf = color_mask.to_surface(setcolor=(0, int(pulse_val), 0, 255), unsetcolor=(0, 0, 0, 0))
  color_change_surf_red = color_mask_red.to_surface(setcolor=(int(pulse_val), 0, 0, 255), unsetcolor=(0, 0, 0, 0))
  color_change_surf_blue = color_mask_blue.to_surface(setcolor=(0, 0, int(pulse_val), 255), unsetcolor=(0, 0, 0, 0))
  
  # clear frame buffer
  fb.fill((0, 0, 0))

  # get input
  process_events()

  # draw
  # update the spacebase image with the new colored surface
  spacebase.draw(fb)
  spacebase_red.img = color_change_surf_red
  spacebase_red.draw(fb)
  spacebase_green.img = color_change_surf
  spacebase_green.draw(fb)
  spacebase_blue.img = color_change_surf_blue
  spacebase_blue.draw(fb)

  # handle screen
  screen.blit(pygame.transform.scale(fb, (SCREEN_W, SCREEN_H)), (0, 0))
  framecount += 1
  update_screen()
