
import pygame
from l01 import *

screen, clock = init(1760, 1024)
k = global_vars.keys

m = IR("data/m_03_02.png", -96, -60)
m.img_normal = m.img
m.img_flip = pygame.transform.flip(m.img, True, False)
bg_img = pygame.image.load("data/background.png").convert_alpha()
bg_w, bg_h = bg_img.get_size()
bg_variants = [
    bg_img,
    pygame.transform.flip(bg_img, True, False),
    pygame.transform.flip(bg_img, False, True),
    pygame.transform.flip(bg_img, True, True),
]

# fb = pygame.Surface((192, 120))
fb = pygame.Surface((256, 160))
fb_w, fb_h = fb.get_size()

def tiled_bg_blits(cam_x, cam_y, bg_variants, bg_w, bg_h, fb_w, fb_h):
    tx_start = cam_x // bg_w;  tx_end = (cam_x + fb_w) // bg_w
    ty_start = cam_y // bg_h;  ty_end = (cam_y + fb_h) // bg_h
    return [
        (bg_variants[(tx % 2) + (ty % 2) * 2], (tx * bg_w - cam_x, ty * bg_h - cam_y))
        for ty in range(ty_start, ty_end + 1)
        for tx in range(tx_start, tx_end + 1)
    ]

facing_right: bool = True
cam_x: float = m.x + m.img.get_width() / 2 - fb_w / 2
cam_y: float = m.y + m.img.get_height() / 2 - fb_h / 2

while True:

    # handle input
    pe()
    
    # Move player
    right: bool = k["right"] or k["d"]
    left: bool = k["left"] or k["a"]
    if right and not facing_right:
        facing_right = True
    if left and facing_right:
        facing_right = False
    m.x += right - left
    m.y += (k["down"] or k["s"]) - (k["up"] or k["w"])
    
    target_x = m.x + m.img.get_width() / 2 - fb_w / 2
    target_y = m.y + m.img.get_height() / 2 - fb_h / 2
    cam_x += (target_x - cam_x) * 0.1
    cam_y += (target_y - cam_y) * 0.1

    # draw to fb
    fb.blits(tiled_bg_blits(int(cam_x), int(cam_y), bg_variants, bg_w, bg_h, fb_w, fb_h))
    m.img = m.img_normal if facing_right else m.img_flip
    fb.blit(m.img, (m.x - int(cam_x), m.y - int(cam_y)))

    # fb to screen
    screen.blit(pygame.transform.scale(fb, screen.get_size()), (0, 0))
    update_screen()

