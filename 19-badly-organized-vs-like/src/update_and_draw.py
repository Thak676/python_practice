
import pygame
from pygame.math import Vector2
import os
import random
from random import randint

from Circle import Circle

Vec2 = Vector2

# Game States
STATE_PLAYING = 0
STATE_LEVEL_UP = 1
game_state = STATE_PLAYING

# Player Stats
player_stats = {
    "move_speed": 1.0, 
    "projectile_speed": 3.0,
    "fire_rate": 60, # Frames per shot
    "pickup_radius": 30
}

# Leveling
level = 1
xp_needed = 5
available_upgrades = []

class Projectile(Circle):
    def __init__(self, x, y, r, color, velocity):
        super().__init__(x, y, r, color)
        self.velocity = velocity

    def update(self):
        self.x += self.velocity.x
        self.y += self.velocity.y

class XP(Circle):
    def __init__(self, x, y, value):
        super().__init__(x, y, 2, (0, 0, 255)) # Blue, small
        self.value = value

def generate_upgrades():
    options = [
        {"name": "Move Speed +10%", "key": "move_speed", "value": 1.1, "type": "mult"},
        {"name": "Fire Rate +10%", "key": "fire_rate", "value": 0.9, "type": "mult"}, # Lower is faster (frames)
        {"name": "Proj Speed +10%", "key": "projectile_speed", "value": 1.1, "type": "mult"},
        {"name": "Pickup Range +20%", "key": "pickup_radius", "value": 1.2, "type": "mult"},
        {"name": "Heal 20 HP", "key": "heal", "value": 20, "type": "add"}
    ]
    # Pick 3 unique upgrades
    return random.sample(options, 3)

enemies = []
projectiles = []
xp_drops = []
_colliding = []

pygame.font.init()
font = pygame.font.SysFont("Arial", 24)
menu_font = pygame.font.SysFont("Arial", 32)

try:
    grass_tile = pygame.image.load("tile_generator/grass_01.png").convert()
except FileNotFoundError:
    try:
        grass_tile = pygame.image.load("src/tile_generator/grass_01.png").convert()
    except FileNotFoundError:
        grass_tile = pygame.Surface((16, 16))
        grass_tile.fill((34, 177, 76))

try:
    bullet_sound = pygame.mixer.Sound("i/bullet_01.wav")
except FileNotFoundError:
    try:
        bullet_sound = pygame.mixer.Sound("src/i/bullet_01.wav")
    except FileNotFoundError:
        print("Warning: bullet_01.wav not found")
        bullet_sound = None

enemy_speed = 0.3

_framecount = 0
player_xp = 0

spawn_timer = 0
SPAWN_rate = 180

def update_game(m, keys, camera_size):
    global _framecount, spawn_timer, _colliding, player_xp
    
    _framecount += 1
            
    # Spawn enemies
    spawn_timer += 1
    if spawn_timer >= SPAWN_rate: 
        spawn_timer = 0
        angle = randint(0, 360)
        min_spawn = 80
        max_spawn = 200
        distance = randint(min_spawn, max_spawn)
        
        spawn_vec = Vec2(distance, 0).rotate(angle)
        enemy_x = m.x + spawn_vec.x
        enemy_y = m.y + spawn_vec.y
        c = Circle(enemy_x, enemy_y, 4, (255, 0, 0))
        enemies.append(c)

    # Damage from colliding
    if (_framecount % 30 == 0):
        for c in _colliding:
            print(c)
            m.hp -= 10
            
    # Shooting logic
    fire_cooldown = max(1, int(player_stats["fire_rate"]))
    if (_framecount % fire_cooldown == 0) and enemies:
        player_pos = Vec2(m.x, m.y)
        shooting_range = 150 
        
        nearby_enemies = [e for e in enemies if player_pos.distance_to(Vec2(e.x, e.y)) <= shooting_range]
        
        if nearby_enemies:
            nearest_enemy = min(nearby_enemies, key=lambda e: player_pos.distance_to(Vec2(e.x, e.y)))
            direction = (Vec2(nearest_enemy.x, nearest_enemy.y) - player_pos)
            if direction.length() > 0:
                direction = direction.normalize()
                vel = direction * player_stats["projectile_speed"]
                proj = Projectile(m.x, m.y, 2, (0, 255, 255), vel)
                projectiles.append(proj)
                if bullet_sound:
                    bullet_sound.play()

    # Movement Logic
    dx = (keys["right"] or keys["d"]) - (keys["left"] or keys["a"])
    dy = (keys["down"] or keys["s"]) - (keys["up"] or keys["w"])
    
    if dx != 0 or dy != 0:
        move_vec = Vec2(dx, dy)
        if move_vec.length() > 0:
            move_vec.normalize_ip()
            move_vec *= player_stats["move_speed"]
            m.x += move_vec.x
            m.y += move_vec.y

    # Enemy Movement
    for c in enemies:
        vec2 = Vec2(m.x - c.x, m.y - c.y)
        if vec2.length() > 0:
             vec2.normalize_ip()
        c.pos += vec2 * enemy_speed

    # Update projectiles
    # Rough camera for cleanup
    cam_x = m.x - camera_size[0] // 2
    cam_y = m.y - camera_size[1] // 2

    for p in projectiles[:]:
        p.update()
        if not (cam_x - 100 <= p.x <= cam_x + camera_size[0] + 100 and 
                cam_y - 100 <= p.y <= cam_y + camera_size[1] + 100):
            projectiles.remove(p)
            continue
            
        # Check collision with enemies (Projectile vs Enemy)
        for e in enemies[:]:
            if Vec2(p.x, p.y).distance_to(Vec2(e.x, e.y)) < (p.r + e.r):
                if p in projectiles: projectiles.remove(p)
                if e in enemies: 
                    enemies.remove(e)
                    xp_drops.append(XP(e.x, e.y, 1))
                break

    # XP Update
    for xp in xp_drops[:]:
        if Vec2(m.x, m.y).distance_to(Vec2(xp.x, xp.y)) < player_stats["pickup_radius"]:
             direction = Vec2(m.x - xp.x, m.y - xp.y).normalize()
             xp.x += direction.x * 2 
             xp.y += direction.y * 2
             
             if Vec2(m.x, m.y).distance_to(Vec2(xp.x, xp.y)) < 10:
                 player_xp += xp.value
                 xp_drops.remove(xp)

def draw_game(fb, CAMERA, m):
    global _colliding
    
    camera_x = m.x - CAMERA[0] // 2
    camera_y = m.y - CAMERA[1] // 2

    # Tile Background
    if grass_tile:
        start_col = int(camera_x // 16)
        start_row = int(camera_y // 16)
        num_cols = (CAMERA[0] // 16) + 2
        num_rows = (CAMERA[1] // 16) + 2

        for col in range(start_col, start_col + num_cols):
            for row in range(start_row, start_row + num_rows):
                screen_x = (col * 16) - camera_x
                screen_y = (row * 16) - camera_y
                fb.blit(grass_tile, (screen_x, screen_y))
    else:
        fb.fill((20, 20, 20))

    # Draw Player Outline
    screen_pos_x = m.x - camera_x
    screen_pos_y = m.y - camera_y
    outline_rect = pygame.Rect(screen_pos_x, screen_pos_y, m.rect.width, m.rect.height).inflate(4, 4)
    pygame.draw.rect(fb, (0, 0, 0), outline_rect)
    fb.blit(m.img, (screen_pos_x, screen_pos_y))
    
    # Draw Projectiles
    for p in projectiles:
        pygame.draw.circle(fb, p.color, (p.x - camera_x, p.y - camera_y), p.r)
    
    # Draw XP
    for xp in xp_drops:
        pygame.draw.circle(fb, (0, 0, 255), (xp.x - camera_x, xp.y - camera_y), 2)
        
    # Draw Enemies and Collision
    colliding_temp = []
    for c in enemies:
        enemy_screen_x = c.x - camera_x
        enemy_screen_y = c.y - camera_y
        pygame.draw.circle(fb, c.color, (enemy_screen_x, enemy_screen_y), c.r)
        
        c_rect = pygame.Rect(c.x - c.r, c.y - c.r, c.r * 2, c.r * 2)
        if m.rect.colliderect(c_rect):
            colliding_temp.append(c)
    _colliding = colliding_temp

    # Draw HUD
    minutes = _framecount // (60 * 60)
    seconds = (_framecount // 60) % 60
    timer_text = f"{minutes:02}:{seconds:02}"
    
    timer_surf = font.render(timer_text, True, (255, 255, 255))
    fb.blit(timer_surf, (CAMERA[0] // 2 - timer_surf.get_width() // 2 + 100, 10))

    hp_surf = font.render(f"HP: {m.hp} XP: {player_xp}", True, (255, 255, 255))
    fb.blit(hp_surf, (10, 10))

def handle_level_up(fb, CAMERA, m):
    global game_state, player_stats
    
    # Draw Overlay
    overlay = pygame.Surface(CAMERA)
    overlay.set_alpha(128)
    overlay.fill((0, 0, 0))
    fb.blit(overlay, (0, 0))
    
    # Draw Menu Box
    menu_w, menu_h = 220, 180
    menu_surf = pygame.Surface((menu_w, menu_h))
    menu_surf.fill((50, 50, 60))
    pygame.draw.rect(menu_surf, (255, 255, 255), (0, 0, menu_w, menu_h), 2)
    
    # Title
    title = menu_font.render("LEVEL UP!", True, (255, 255, 0))
    menu_surf.blit(title, (menu_w//2 - title.get_width()//2, 10))
    sub = font.render(f"Level {level}", True, (200, 200, 200))
    menu_surf.blit(sub, (menu_w//2 - sub.get_width()//2, 40))
    
    # Options
    y_off = 70
    for i, upg in enumerate(available_upgrades):
        text = f"{i+1}. {upg['name']}"
        opt_surf = font.render(text, True, (255, 255, 255))
        menu_surf.blit(opt_surf, (10, y_off))
        y_off += 30

    fb.blit(menu_surf, (CAMERA[0]//2 - menu_w//2, CAMERA[1]//2 - menu_h//2))

    # Logic
    pressed = pygame.key.get_pressed()
    choice = -1
    if pressed[pygame.K_1]: choice = 0
    elif pressed[pygame.K_2]: choice = 1
    elif pressed[pygame.K_3]: choice = 2
    
    if choice >= 0 and choice < len(available_upgrades):
        sel = available_upgrades[choice]
        if sel["type"] == "add":
            if sel["key"] == "heal":
                m.hp += sel["value"]
        elif sel["type"] == "mult":
            player_stats[sel["key"]] *= sel["value"]
            
        game_state = STATE_PLAYING

def update_and_draw(fb, CAMERA, m, keys):
    global game_state, level, player_xp, xp_needed, available_upgrades

    # State Transitions
    if game_state == STATE_PLAYING:
        if player_xp >= xp_needed:
            game_state = STATE_LEVEL_UP
            level += 1
            player_xp -= xp_needed
            xp_needed = int(xp_needed * 1.5)
            available_upgrades = generate_upgrades()
        else:
            update_game(m, keys, CAMERA)

    # Drawing
    draw_game(fb, CAMERA, m)

    # UI Overlay
    if game_state == STATE_LEVEL_UP:
        handle_level_up(fb, CAMERA, m)
