
import pygame
from pygame.locals import *
import sys
import random
from l01 import *
import math
import sys

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

# generate starfield
stars = []
for _ in range(50):
    stars.append({
        'x': random.randint(0, 107),
        'y': random.randint(0, 107),
        'color': random.randint(100, 255)
    })

# player setup
player_pos = pygame.Vector2(fb.get_width() / 2, fb.get_height() / 2)
player_vel = pygame.Vector2(0, 0)
player_accel = 0.1
player_max_speed = 2.0
player_friction = 0.98

player_surf = pygame.Surface((3, 3))
player_surf.fill((255, 255, 0)) # yellow ship

camera = pygame.Vector2(0, 0)

framecount: int = 0
pulse_speed: float = 0.02

while True:
  # calculate dynamic pulse value (100 to 255)
  pulse_val = 180 + abs(math.sin(framecount * pulse_speed)) * 75 # add number and mult number need to add up to 255 to keep color within correct bounds
  blue_pulse_val = 150 + abs(math.sin(framecount * pulse_speed)) * 105 # add number and mult number need to add up to 255 to keep color within correct bounds  

  # create surface with dynamic green component
  color_change_surf = color_mask.to_surface(setcolor=(0, int(pulse_val), 0, 255), unsetcolor=(0, 0, 0, 0))
  color_change_surf_red = color_mask_red.to_surface(setcolor=(int(pulse_val), 0, 0, 255), unsetcolor=(0, 0, 0, 0))
  color_change_surf_blue = color_mask_blue.to_surface(setcolor=(0, 0, int(blue_pulse_val), 255), unsetcolor=(0, 0, 0, 0))
  
  # clear frame buffer
  fb.fill((0, 0, 0))

  # update camera (smooth tracking)
  # Basic idea: we want to draw to the low-res buffer (fb) but display it smoothly on the high-res screen.
  # We do this by tracking the camera with float precision, snapping to integers for the drawing on fb, 
  # and then using the sub-pixel remainder to offset the final blit to the screen.
  
  # Calculate ideal camera position
  target_cam_x = player_pos.x - fb.get_width() / 2
  target_cam_y = player_pos.y - fb.get_height() / 2
  
  camera.x = target_cam_x
  camera.y = target_cam_y

  # Integer camera position for pixel-perfect drawing on the low-res buffer
  cam_x_int = int(camera.x)
  cam_y_int = int(camera.y)
  
  # Sub-pixel offset for smooth movement on high-res screen
  # 1 unit on fb = 10 units on screen. 
  # The remainder is the sub-pixel part.
  
  cam_offset_x = (camera.x - cam_x_int) * (SCREEN_W / fb.get_width())
  cam_offset_y = (camera.y - cam_y_int) * (SCREEN_H / fb.get_height())

  # draw stars (parallax)
  for s in stars:
    if random.random() < 0.01:
      s['color'] = random.randint(100, 255)
    
    # Calculate star position relative to camera with wrapping
    # Use integer camera position to keep stars locked to pixel grid
    sx = (s['x'] - cam_x_int * 0.5) % fb.get_width()
    sy = (s['y'] - cam_y_int * 0.5) % fb.get_height()
    fb.set_at((int(sx), int(sy)), (s['color'], s['color'], s['color']))

  # get input
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()

  keys = pygame.key.get_pressed()
  accel = pygame.Vector2(0, 0)
  if keys[K_LEFT] or keys[K_a]:
    accel.x -= player_accel
  if keys[K_RIGHT] or keys[K_d]:
    accel.x += player_accel
  if keys[K_UP] or keys[K_w]:
    accel.y -= player_accel
  if keys[K_DOWN] or keys[K_s]:
    accel.y += player_accel

  # physics
  player_vel += accel
  if player_vel.length() > player_max_speed:
      player_vel.scale_to_length(player_max_speed)
  
  player_pos += player_vel
  player_vel *= player_friction # simple friction

  # draw
  # update the spacebase image with the new colored surface
  # draw relative to integer camera
  blit_pos = (5 - cam_x_int, 5 - cam_y_int)
  
  spacebase.img.set_colorkey((0,0,0)) # ensure transparency works if not set
  fb.blit(spacebase.img, blit_pos)

  spacebase_red.img = color_change_surf_red
  fb.blit(spacebase_red.img, blit_pos)
  
  spacebase_green.img = color_change_surf
  fb.blit(spacebase_green.img, blit_pos)

  spacebase_blue.img = color_change_surf_blue
  fb.blit(spacebase_blue.img, blit_pos)

  # draw player
  screen_pos = player_pos - pygame.Vector2(cam_x_int, cam_y_int)
  fb.blit(player_surf, screen_pos)

  # handle screen
  scaled_surf = pygame.transform.scale(fb, (SCREEN_W + int(SCREEN_W/fb.get_width()), SCREEN_H + int(SCREEN_H/fb.get_height()))) # Scale slightly larger to cover potential sub-pixel gap
  screen.blit(scaled_surf, (-cam_offset_x, -cam_offset_y))
  framecount += 1
  update_screen()
