import math
import random
import pygame

class Potion:
    PICK_RADIUS = 6
    HEAL        = 2
    _img        = None  # shared, loaded once

    def __init__(self, x, y):
        self.x, self.y = x, y

    @classmethod
    def _get_img(cls):
        if cls._img is None:
            cls._img = pygame.image.load("data/potion.png").convert_alpha()
        return cls._img

    def draw(self, fb, cam_x, cam_y):
        img = self._get_img()
        sx = int(self.x - cam_x) - img.get_width() // 2
        sy = int(self.y - cam_y) - img.get_height() // 2
        fb.blit(img, (sx, sy))

    def collected_by(self, player):
        return math.hypot(self.x - player.cx, self.y - player.cy) < self.PICK_RADIUS


def maybe_spawn_potion(frame, cam_x, cam_y, fb_w, fb_h, interval=3600):
    """Return a new Potion once every `interval` frames at a random world position."""
    if frame % interval != 0:
        return None
    x = cam_x + random.uniform(-fb_w * 1.5, fb_w * 2.5)
    y = cam_y + random.uniform(-fb_h * 1.5, fb_h * 2.5)
    return Potion(x, y)


def collect_potions(potions, player):
    """Heal player for any collected potions; return remaining list."""
    remaining = []
    for p in potions:
        if p.collected_by(player):
            player.hp = min(player.hp + Potion.HEAL, player.max_hp)
        else:
            remaining.append(p)
    return remaining
