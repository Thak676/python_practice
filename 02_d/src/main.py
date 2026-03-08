
import pygame
import random
from l01 import *
from enemies import Enemy
from player import Player
from weapons import Dagger, OrbWeapon, Whip, Fireball
from gems import drop_gems, collect_gems, Gem
from hud import draw_hud
from upgrade import run_upgrade_screen
from menu import run_start_menu, run_pause_menu
from items import maybe_spawn_potion, collect_potions

screen, clock = init(1760, 1024)
k = global_vars.keys

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

player = Player("data/m_03_02.png", -96, -60)
cam_x: float = player.cx - fb_w / 2
cam_y: float = player.cy - fb_h / 2

run_start_menu(fb, screen, clock)
esc_prev = False
shake_frames = 0  # --- SCREEN SHAKE counter (remove to disable) ---

enemies: list = []
projectiles: list = []
spawn_timer: int = 0
spawn_interval: int = 90       # shrinks over time
SPAWN_MIN: int = 20
WIN_FRAMES: int = 20 * 60 * 60  # 20 minutes
MAX_TIER_CAP: int = len(Enemy.VARIANTS) - 1
dagger = Dagger()
orb = OrbWeapon(count=0)
whip = Whip()
whip.active = False
fireball = Fireball()
gems: list = []
potions: list = []
frame: int = 0
max_tier: int = 0

while True:

    # handle input
    pe()
    frame += 1
    esc_curr = pygame.key.get_pressed()[pygame.K_ESCAPE]
    if esc_curr and not esc_prev:
        run_pause_menu(fb, screen, clock)
    esc_prev = esc_curr
    
    # Move player
    right: bool = k["right"] or k["d"]
    left: bool  = k["left"]  or k["a"]
    player.x += (right - left) * player.speed
    player.y += ((k["down"] or k["s"]) - (k["up"] or k["w"])) * player.speed
    player.update_facing(right, left)
    
    cam_x += (player.cx - fb_w / 2 - cam_x) * 0.1
    cam_y += (player.cy - fb_h / 2 - cam_y) * 0.1

    # spawn scaling: every 30 s reduce interval by 20%
    if frame % 1800 == 0:
        spawn_interval = max(SPAWN_MIN, int(spawn_interval * 0.8))

    # tier scaling: unlock next variant every 60 s
    if frame % 3600 == 0:
        max_tier = min(max_tier + 1, MAX_TIER_CAP)

    # spawn enemies
    spawn_timer += 1
    if spawn_timer >= spawn_interval:
        spawn_timer = 0
        enemies.append(Enemy.spawn(int(cam_x), int(cam_y), fb_w, fb_h, max_tier))

    # update player (damage / iframes)
    # --- SCREEN SHAKE: set shake_frames=8 on hit (remove this block to disable) ---
    if player.update(enemies):
        shake_frames = 8

    weapon_slots = (
        [((255, 220, 80), True)]  # dagger always first
        + [((120, 180, 255), True)] * (1 if orb.count > 0 else 0)
        + [((255, 140, 40),  True)] * (1 if whip.active    else 0)
        + [((255, 80,  20),  True)] * (1 if fireball.active else 0)
    )[:3]

    # game-over / win check
    if not player.alive or frame >= WIN_FRAMES:
        msg = "YOU WIN!" if frame >= WIN_FRAMES else "GAME OVER"
        draw_hud(fb, player, frame, weapon_slots)
        screen.blit(pygame.transform.scale(fb, screen.get_size()), (0, 0))
        font = pygame.font.SysFont(None, 80)
        surf = font.render(msg, True, (255, 255, 100))
        screen.blit(surf, surf.get_rect(center=screen.get_rect().center))
        pygame.display.update()
        pygame.time.wait(3000)
        break

    # update weapons & projectiles
    dagger.update(player, projectiles)
    orb.update(player, enemies)
    if whip.active:
        whip.update(player, enemies)
    if fireball.active:
        fireball.update(player, enemies, projectiles)
    for p in projectiles:
        p.update(enemies)
    gems += drop_gems(enemies)
    enemies     = [e for e in enemies     if e.hp > 0]
    projectiles = [p for p in projectiles if not p.dead]
    gems, xp = collect_gems(gems, player)
    pot = maybe_spawn_potion(frame, int(cam_x), int(cam_y), fb_w, fb_h)
    if pot:
        potions.append(pot)
    potions = collect_potions(potions, player)
    if player.add_xp(xp) > 0:
        run_upgrade_screen(fb, screen, player, dagger, orb, whip, fireball, clock, k)

    # update enemies
    for e in enemies:
        e.update(player.cx, player.cy)

    # draw to fb
    fb.blits(tiled_bg_blits(int(cam_x), int(cam_y), bg_variants, bg_w, bg_h, fb_w, fb_h))
    for g in gems:
        g.draw(fb, int(cam_x), int(cam_y))
    for pot in potions:
        pot.draw(fb, int(cam_x), int(cam_y))
    for e in enemies:
        e.draw(fb, int(cam_x), int(cam_y))
    fb.blit(player.img, (player.x - int(cam_x), player.y - int(cam_y)))
    for p in projectiles:
        p.draw(fb, int(cam_x), int(cam_y))
    orb.draw(fb, player, int(cam_x), int(cam_y))
    if whip.active:
        whip.draw(fb, player, int(cam_x), int(cam_y))
    draw_hud(fb, player, frame, weapon_slots)

    # fb to screen
    # --- SCREEN SHAKE: offset blit when shaking (remove these 3 lines to disable) ---
    if shake_frames > 0:
        shake_frames -= 1
    ox = random.randint(-2, 2) if shake_frames > 0 else 0
    oy = random.randint(-2, 2) if shake_frames > 0 else 0
    screen.blit(pygame.transform.scale(fb, screen.get_size()), (ox, oy))
    update_screen()
