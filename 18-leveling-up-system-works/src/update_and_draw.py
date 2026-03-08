
import pygame
import os
import random
from random import randint

from Circle import Circle
from Projectile import Projectile
from XP import XP
from generate_upgrades import generate_upgrades

Vec2 = pygame.math.Vector2

# Game States
STATE_PLAYING = 0
STATE_LEVEL_UP = 1

# initialize game state as STATE_PLAYING
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

enemies = []
projectiles = []
xp_drops = []
_colliding = []

grass_tile = None
bullet_sound = None

enemy_speed = 0.3

_framecount = 0
player_xp = 0
font = None
menu_font = None

spawn_timer = 0
SPAWN_rate = 180

def update_and_draw(fb, CAMERA, m, keys):

    global _framecount
    global _colliding
    global font
    global menu_font
    global projectiles
    global enemies
    global xp_drops
    global player_xp
    global grass_tile
    global bullet_sound
    
    global game_state
    global level
    global xp_needed
    global available_upgrades
    global spawn_timer
    global SPAWN_rate

    if font is None:
        pygame.font.init()
        font = pygame.font.SysFont("Arial", 24)
        menu_font = pygame.font.SysFont("Arial", 32)

    # Check for Level Up
    if game_state == STATE_LEVEL_UP:
        # Draw Menu Overlay
        overlay = pygame.Surface(CAMERA)
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        fb.blit(overlay, (0, 0))
        
        title = menu_font.render("LEVEL UP!", True, (255, 255, 0))
        fb.blit(title, (CAMERA[0]//2 - title.get_width()//2, 20))
        
        sub = font.render(f"Level {level}", True, (255, 255, 255))
        fb.blit(sub, (CAMERA[0]//2 - sub.get_width()//2, 50))
        
        # Display Options
        y_off = 80
        for i, upg in enumerate(available_upgrades):
            text = f"{i+1}. {upg['name']}"
            opt_surf = font.render(text, True, (255, 255, 255))
            fb.blit(opt_surf, (20, y_off))
            y_off += 30
            
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
                    # Assuming hard cap of 100 or stat based
                    # m.hp is not capped in original code other than initial 100
                    pass
            elif sel["type"] == "mult":
                player_stats[sel["key"]] *= sel["value"]
                
            game_state = STATE_PLAYING
            
        return

    if player_xp >= xp_needed:
        game_state = STATE_LEVEL_UP
        level += 1
        player_xp -= xp_needed
        xp_needed = int(xp_needed * 1.5)
        available_upgrades = generate_upgrades()
        return

    if grass_tile is None:
        try:
            # Try path relative to src/
            grass_tile = pygame.image.load("tile_generator/grass_01.png").convert()
        except FileNotFoundError:
            try:
                # Try path relative to project root
                 grass_tile = pygame.image.load("src/tile_generator/grass_01.png").convert()
            except FileNotFoundError:
                 # Fallback: Create a green surface
                 grass_tile = pygame.Surface((16, 16))
                 grass_tile.fill((34, 177, 76))

    if bullet_sound is None:
        try:
             # Try path relative to src/
            bullet_sound = pygame.mixer.Sound("i/bullet_01.wav")
        except FileNotFoundError:
            try:
                # Try path relative to project root
                bullet_sound = pygame.mixer.Sound("src/i/bullet_01.wav")
            except FileNotFoundError:
                print("Warning: bullet_01.wav not found")
                bullet_sound = False 

    # update
    _framecount += 1
    
    # Camera follows player
    camera_x = m.x - CAMERA[0] // 2
    camera_y = m.y - CAMERA[1] // 2
    
    # Spawn enemies around the player
    if (_framecount % 30 == 0):
        angle = randint(0, 360)
        # Camera is 270x270. Half is 135.
        # Spawn some on screen (but not too close), some just off screen.
        min_spawn = 80  # On screen, not too close
        max_spawn = 200 # slightly off screen (corner is ~190)
        distance = randint(min_spawn, max_spawn)
        
        spawn_vec = Vec2(distance, 0).rotate(angle)
        enemy_x = m.x + spawn_vec.x
        enemy_y = m.y + spawn_vec.y
        c = Circle(enemy_x, enemy_y, 4, (255, 0, 0))
        enemies.append(c)

    if (_framecount % 30 == 0):
        for c in _colliding:
            print(c)
            m.hp -= 10
            
    # Shooting logic
    fire_cooldown = max(1, int(player_stats["fire_rate"]))
    if (_framecount % fire_cooldown == 0) and enemies:
        player_pos = Vec2(m.x, m.y)
        shooting_range = 150 # Define shooting radius
        
        # Optimize: only check enemies within range
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

    for c in enemies:
        vec2 = Vec2(m.x - c.x, m.y - c.y)
        # ought to work but doesn't:
        #vec2 = Vec2(m.pos - c.pos)
        if vec2.length() > 0:
             vec2.normalize_ip()
        c.pos += vec2 * enemy_speed

    # Update projectiles
    for p in projectiles[:]:
        p.update()
        # Remove if too far from camera view (cleanup)
        if not (camera_x - 100 <= p.x <= camera_x + CAMERA[0] + 100 and 
                camera_y - 100 <= p.y <= camera_y + CAMERA[1] + 100):
            projectiles.remove(p)
            continue
            
        # Check collision with enemies
        for e in enemies[:]:
            if Vec2(p.x, p.y).distance_to(Vec2(e.x, e.y)) < (p.r + e.r):
                if p in projectiles: projectiles.remove(p)
                if e in enemies: 
                    enemies.remove(e)
                    xp_drops.append(XP(e.x, e.y, 1))

                break

    # XP Logic
    # Move XP towards player if within range (magnet effect) or just simple pickup
    # Simple pickup for now
    for xp in xp_drops[:]:
        if Vec2(m.x, m.y).distance_to(Vec2(xp.x, xp.y)) < player_stats["pickup_radius"]:
             # Magnet effect
             direction = Vec2(m.x - xp.x, m.y - xp.y).normalize()
             xp.x += direction.x * 2 # XP moves towards player
             xp.y += direction.y * 2
             
             if Vec2(m.x, m.y).distance_to(Vec2(xp.x, xp.y)) < 10:
                 player_xp += xp.value
                 xp_drops.remove(xp)
                 
    # draw
    # Tile the grass background
    if grass_tile:
        # Determine top-left corner of visible world
        # camera_x, camera_y are the world coords that map to (0,0) on screen.
        start_col = int(camera_x // 16)
        start_row = int(camera_y // 16)
        # Number of tiles to cover width/height + buffer
        num_cols = (CAMERA[0] // 16) + 2
        num_rows = (CAMERA[1] // 16) + 2

        for col in range(start_col, start_col + num_cols):
            for row in range(start_row, start_row + num_rows):
                # World position of this tile
                tile_world_x = col * 16
                tile_world_y = row * 16
                # Screen position
                screen_x = tile_world_x - camera_x
                screen_y = tile_world_y - camera_y
                fb.blit(grass_tile, (screen_x, screen_y))
    else:
        fb.fill((20, 20, 20))

    # Draw simple black outline/background for player
    # Since m.draw uses m.rect which is in world coords, we need to temporarily
    # adjust or draw manually. m is an Image_Rect from l01.
    # We can't easily change m.rect without affecting game logic.
    # So we draw the image manually at screen coords.
    
    screen_pos_x = m.x - camera_x
    screen_pos_y = m.y - camera_y
    
    outline_rect = pygame.Rect(screen_pos_x, screen_pos_y, m.rect.width, m.rect.height).inflate(4, 4)
    pygame.draw.rect(fb, (0, 0, 0), outline_rect)
    
    fb.blit(m.img, (screen_pos_x, screen_pos_y))
    
    for p in projectiles:
        pygame.draw.circle(fb, p.color, (p.x - camera_x, p.y - camera_y), p.r)
        
    for xp in xp_drops:
        pygame.draw.circle(fb, (0, 0, 255), (xp.x - camera_x, xp.y - camera_y), 2)
        
    colliding_temp = []
    for c in enemies:
        enemy_screen_x = c.x - camera_x
        enemy_screen_y = c.y - camera_y
        pygame.draw.circle(fb, c.color, (enemy_screen_x, enemy_screen_y), c.r)
        
        # Collision detection (world coords)
        # m.rect is in world coords.
        # enemy needs a rect in world coords.
        c_rect = pygame.Rect(c.x - c.r, c.y - c.r, c.r * 2, c.r * 2)
        if m.rect.colliderect(c_rect):
            colliding_temp.append(c)
    _colliding = colliding_temp

    # Timer logic (60 FPS)
    minutes = _framecount // (60 * 60)
    seconds = (_framecount // 60) % 60
    timer_text = f"{minutes:02}:{seconds:02}"
    
    timer_surf = font.render(timer_text, True, (255, 255, 255))
    # Draw timer in top center
    fb.blit(timer_surf, (CAMERA[0] // 2 - timer_surf.get_width() // 2 + 100, 10))

    hp_surf = font.render(f"HP: {m.hp} XP: {player_xp}", True, (255, 255, 255))
    fb.blit(hp_surf, (10, 10))
