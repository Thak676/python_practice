import math
import pygame

class Player:
    HIT_RADIUS = 5  # collision distance in fb pixels

    def __init__(self, img_path, x, y, max_hp=10):
        img = pygame.image.load(img_path).convert_alpha()
        self.img_normal = img
        self.img_flip = pygame.transform.flip(img, True, False)
        self.img = img
        self.x: float = x
        self.y: float = y
        self.max_hp = max_hp
        self.hp = max_hp
        self.facing_right = True
        self.speed = 1.0
        self.xp = 0
        self.level = 1

    def xp_threshold(self):
        """XP needed to reach next level (triangular-ish growth)."""
        n = self.level
        return n * (n + 1) // 2 * 5

    def add_xp(self, amount):
        self.xp += amount
        gained = 0
        while self.xp >= self.xp_threshold():
            self.xp -= self.xp_threshold()
            self.level += 1
            gained += 1
        return gained

    @property
    def cx(self): return self.x + self.img.get_width() / 2
    @property
    def cy(self): return self.y + self.img.get_height() / 2

    def update_facing(self, right, left):
        if right: self.facing_right = True
        if left:  self.facing_right = False
        self.img = self.img_normal if self.facing_right else self.img_flip

    def update(self, enemies):
        hit = False
        for e in enemies:
            if e.hit_timer > 0:
                e.hit_timer -= 1
                continue
            if math.hypot(self.cx - e.x, self.cy - e.y) < self.HIT_RADIUS:
                self.hp -= e.damage
                e.hit_timer = e.HIT_COOLDOWN
                hit = True
                # --- KNOCKBACK (remove these 4 lines to disable) ---
                dx, dy = e.x - self.cx, e.y - self.cy
                dist = math.hypot(dx, dy) or 1
                e.x += 8 * dx / dist
                e.y += 8 * dy / dist
        return hit

    @property
    def alive(self):
        return self.hp > 0
