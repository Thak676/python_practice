
import pygame
import sys
import datetime
from pygame.locals import *
from l01 import *

screen, clock = init(1080, 1080)
k = global_vars.keys

m = IR("data/m_03_02.png", 30, 60)
speed = 1

fb = pygame.Surface((240, 240))

cliff0 = IR("data/cliff/0.png", 0, 0)
cliff1 = IR("data/cliff/1.png", 0, 0)
cliff2 = IR("data/cliff/2.png", 0, 0)
cliff3 = IR("data/cliff/3.png", 0, 0)
cliff4 = IR("data/cliff/4.png", 0, 0)
cliff5 = IR("data/cliff/5.png", 0, 0)
cliff6 = IR("data/cliff/6.png", 0, 0)
cliff7 = IR("data/cliff/7.png", 0, 0)
cliff8 = IR("data/cliff/8.png", 0, 0)

ground1 = IR("data/ground.png", 0, 0)

map = [
    14,15,00,00,00,13,14,15,00,13,14,14,14,14,14,14,14,14,14,14,14,14,14,14,14,15,00,00,13,14, # 1
    14,15,00,00,00,13,14,15,00,13,14,14,14,14,14,14,14,14,14,14,14,14,14,14,14,15,00,00,13,14, # 2
    14,15,00,00,00,13,14,15,00,13,14,14,14,14,14,14,14,14,14,14,14,14,14,14,14,15,00,00,13,14, # 3
    14,15,00,00,00,13,14,15,00,13,14,14,14,14,14,14,14,14,14,14,14,14,14,14,14,15,00,00,13,14, # 4
    14,15,00,00,00,13,14,15,00,13,14,14,14,14,14,14,14,14,14,14,14,14,14,14,14,15,00,00,13,14, # 5
    14,15,00,00,00,13,14,15,00,13,14,14,14,14,14,14,14,14,14,14,14,14,14,14,14,15,00,00,13,14, # 6
    14,15,00,00,00,13,14,15,00,13,14,14,14,14,14,14,14,14,14,14,14,14,14,14,14,15,00,00,13,14, # 7
    14,15,00,00,00,16,17,18,00,16,17,17,17,17,17,17,17,17,17,17,17,17,17,17,17,18,00,00,13,14, # 8
    14,15,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,13,14, # 9
    14,15,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,13,14, # 10
    14,15,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,13,14, # 11
    14,15,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,13,14, # 12
    14,15,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,13,14, # 13
    14,15,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,13,14, # 14
    14,15,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,13,14, # 15
    14,15,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,13,14, # 16
    14,15,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,13,14, # 17
    14,15,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,13,14, # 18
    14,15,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,13,14, # 19
    14,15,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,13,14, # 20
    14,15,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,13,14, # 21
    14,15,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,13,14, # 22
    14,15,00,00,00,10,11,12,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,13,14, # 23
    14,15,00,00,00,13,14,15,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,13,14, # 24
    14,15,00,00,00,13,14,15,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,13,14, # 25
    14,15,00,00,00,13,14,15,00,10,11,11,11,11,11,11,11,11,11,11,11,11,11,11,11,12,00,00,13,14, # 26
    14,15,00,00,00,13,14,15,00,14,14,14,14,14,14,14,14,14,14,14,14,14,14,14,14,15,00,00,13,14, # 27
    14,15,00,00,00,13,14,15,00,14,14,14,14,14,14,14,14,14,14,14,14,14,14,14,14,15,00,00,13,14, # 28
    14,15,00,00,00,13,14,15,00,14,14,14,14,14,14,14,14,14,14,14,14,14,14,14,14,15,00,00,13,14, # 29
    14,15,00,00,00,13,14,15,14,14,14,14,14,14,14,14,14,14,14,14,14,14,14,14,14,15,00,00,13,14  # 30
]

def check_collision(player_rect, tilemap, tile_width=30, tile_size=8):
    """Check if player collides with solid tiles (value 1)"""
    # Get the tiles the player overlaps
    left = player_rect.left // tile_size
    right = player_rect.right // tile_size
    top = player_rect.top // tile_size
    bottom = player_rect.bottom // tile_size
    
    # Clamp to map bounds
    left = max(0, min(left, tile_width - 1))
    right = max(0, min(right, tile_width - 1))
    top = max(0, min(top, tile_width - 1))
    bottom = max(0, min(bottom, tile_width - 1))
    
    # Check each tile the player overlaps
    for row in range(top, bottom + 1):
        for col in range(left, right + 1):
            tile_index = row * tile_width + col
            if tile_index < len(tilemap) and tilemap[tile_index] == 14:
                return True
    return False

while True:

    # handle input
    keys = pygame.key.get_pressed()
    mods = pygame.key.get_mods()
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_s and (mods & KMOD_CTRL):
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"fb_{timestamp}.png"
                pygame.image.save(fb, filename)
                print(f"Saved {filename}")
            
            if event.key == K_UP:
                k["up"] = True
            if event.key == K_DOWN:
                k["down"] = True
            if event.key == K_LEFT:
                k["left"] = True
            if event.key == K_RIGHT:
                k["right"] = True
            if event.key == K_w:
                k["w"] = True
            if event.key == K_s:
                k["s"] = True
            if event.key == K_a:
                k["a"] = True
            if event.key == K_d:
                k["d"] = True
            if event.key == K_SPACE:
                k["space"] = True
        if event.type == KEYUP:
            if event.key == K_UP:
                k["up"] = False
            if event.key == K_DOWN:
                k["down"] = False
            if event.key == K_w:
                k["w"] = False
            if event.key == K_s:
                k["s"] = False
            if event.key == K_a:
                k["a"] = False
            if event.key == K_d:
                k["d"] = False
            if event.key == K_LEFT:
                k["left"] = False
            if event.key == K_RIGHT:
                k["right"] = False
            if event.key == K_SPACE:
                k["space"] = False
    

    
    # Move player
    m.x += (k["right"] or k["d"]) - (k["left"] or k["a"])
    m.y += (k["down"] or k["s"]) - (k["up"] or k["w"])
    
    # # Store previous position
    # prev_x, prev_y = m.x, m.y
    # # Check collision and revert if needed
    # if check_collision(m.rect, map):
    #     m.x, m.y = prev_x, prev_y

    # draw to fb
    fb.fill((14, 240, 240)) 
    i: int = 0
    while (i < len(map)):
        if map[i] == 10:
            cliff0.x = (i % 30) * 8
            cliff0.y = (i // 30) * 8
            cliff0.draw(fb)
        if map[i] == 11:
            cliff1.x = (i % 30) * 8
            cliff1.y = (i // 30) * 8
            cliff1.draw(fb)
        if map[i] == 12:
            cliff2.x = (i % 30) * 8
            cliff2.y = (i // 30) * 8
            cliff2.draw(fb)
        if map[i] == 13:
            cliff3.x = (i % 30) * 8
            cliff3.y = (i // 30) * 8
            cliff3.draw(fb)
        if map[i] == 14:
            cliff4.x = (i % 30) * 8
            cliff4.y = (i // 30) * 8
            cliff4.draw(fb)
        if map[i] == 15:
            cliff5.x = (i % 30) * 8
            cliff5.y = (i // 30) * 8
            cliff5.draw(fb)
        if map[i] == 16:
            cliff6.x = (i % 30) * 8
            cliff6.y = (i // 30) * 8
            cliff6.draw(fb)
        if map[i] == 17:
            cliff7.x = (i % 30) * 8
            cliff7.y = (i // 30) * 8
            cliff7.draw(fb)
        if map[i] == 18:
            cliff8.x = (i % 30) * 8
            cliff8.y = (i // 30) * 8
            cliff8.draw(fb)
        if map[i] == 0:
            ground1.x = (i % 30) * 8
            ground1.y = (i // 30) * 8
            ground1.draw(fb)
        i += 1
    m.draw(fb)

    # fb to screen
    screen.blit(pygame.transform.scale(fb, screen.get_size()), (0, 0))
    update_screen()
