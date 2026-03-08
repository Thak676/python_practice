import math
import pygame

class Gem:
    RADIUS      = 2
    COLOR       = (80, 100, 255)
    PICK_RADIUS = 8

    def __init__(self, x, y, value=1):
        self.x, self.y = x, y
        self.value = value

    def draw(self, fb, cam_x, cam_y):
        pygame.draw.circle(fb, self.COLOR,
                           (int(self.x - cam_x), int(self.y - cam_y)), self.RADIUS)


def drop_gems(enemies):
    """Return a list of Gems for every dead enemy (call before filtering enemies)."""
    return [Gem(e.x, e.y, e.xp_value) for e in enemies if e.hp <= 0]


def collect_gems(gems, player):
    """Remove gems within pickup radius; return total xp collected."""
    xp = 0
    remaining = []
    for g in gems:
        if math.hypot(g.x - player.cx, g.y - player.cy) < Gem.PICK_RADIUS:
            xp += g.value
        else:
            remaining.append(g)
    return remaining, xp
