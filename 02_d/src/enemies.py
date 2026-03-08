import random
import math
import pygame

class Enemy:
    SIZE = 3  # half-width of placeholder square
    HIT_COOLDOWN = 60  # frames before this enemy can damage the player again

    # (color, hp, speed, damage, xp_value)
    VARIANTS = [
        ((80,  200, 80),  1, 0.4, 1, 1),   # tier 0: basic slime
        ((200, 180, 50),  2, 0.6, 1, 2),   # tier 1: fast
        ((200,  80, 80),  4, 0.5, 2, 4),   # tier 2: tough
        ((180,  80, 200), 6, 0.7, 2, 6),   # tier 3: fast + tough
    ]

    def __init__(self, x, y, hp=1, speed=0.4, damage=1, xp_value=1, color=(80, 200, 80)):
        self.x, self.y = x, y
        self.hp = hp
        self.speed = speed
        self.damage = damage
        self.xp_value = xp_value
        self.color = color
        self.hit_timer = 0   # counts down; 0 means ready to hit player
        self.flash_timer = 0  # white flash on damage

    @staticmethod
    def spawn(cam_x, cam_y, fb_w, fb_h, max_tier=0, margin=20):
        side = random.randint(0, 3)
        if side == 0:   x, y = random.uniform(cam_x - margin, cam_x + fb_w + margin), cam_y - margin
        elif side == 1: x, y = random.uniform(cam_x - margin, cam_x + fb_w + margin), cam_y + fb_h + margin
        elif side == 2: x, y = cam_x - margin, random.uniform(cam_y - margin, cam_y + fb_h + margin)
        else:           x, y = cam_x + fb_w + margin, random.uniform(cam_y - margin, cam_y + fb_h + margin)
        tier = random.randint(0, max_tier)
        color, hp, speed, damage, xp = Enemy.VARIANTS[tier]
        return Enemy(x, y, hp, speed, damage, xp, color)

    def take_damage(self, amount):
        self.hp -= amount
        self.flash_timer = 6

    def update(self, px, py):
        dx, dy = px - self.x, py - self.y
        dist = math.hypot(dx, dy)
        if dist > 0:
            self.x += self.speed * dx / dist
            self.y += self.speed * dy / dist

    def draw(self, fb, cam_x, cam_y):
        if self.flash_timer > 0:
            self.flash_timer -= 1
        sx, sy = int(self.x - cam_x), int(self.y - cam_y)
        s = self.SIZE
        color = (255, 255, 255) if self.flash_timer > 0 else self.color
        pygame.draw.rect(fb, color, (sx - s, sy - s, s * 2, s * 2))
