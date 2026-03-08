import random
import math
import pygame
from gems import Gem

pygame.font.init()
_font  = pygame.font.SysFont(None, 10)
_title = pygame.font.SysFont(None, 8)

# Each upgrade: (label, apply(p,d,o,w,f), available(p,d,o,w,f))
# Stat upgrades are always available; weapon unlocks filter themselves out once acquired.
def _weapon_count(d, o, w, f):
    # Dagger is always active; orb counts once count > 0
    return 1 + (1 if o.count > 0 else 0) + (1 if w.active else 0) + (1 if f.active else 0)

_always = lambda p, d, o, w, f: True
_can_unlock = lambda p, d, o, w, f: _weapon_count(d, o, w, f) < 3

POOL = [
    ("Dagger faster",   lambda p, d, o, w, f: setattr(d, "COOLDOWN", max(10, d.COOLDOWN - int(d.COOLDOWN * 0.1))), _always),
    ("Dagger +1 dmg",   lambda p, d, o, w, f: setattr(d, "base_damage", d.base_damage + 1),                        _always),
    ("+1 max HP",       lambda p, d, o, w, f: (setattr(p, "max_hp", p.max_hp + 1), setattr(p, "hp", min(p.hp + 1, p.max_hp + 1))), _always),
    ("Speed +10%",      lambda p, d, o, w, f: setattr(p, "speed", p.speed * 1.1),                                       _always),
    ("Magnet",          lambda p, d, o, w, f: setattr(Gem, "PICK_RADIUS", Gem.PICK_RADIUS * 2),                     _always),
    ("+1 Orb",          lambda p, d, o, w, f: setattr(o, "count", o.count + 1),                                     lambda p, d, o, w, f: o.count > 0 or _can_unlock(p, d, o, w, f)),
    ("Unlock Whip",     lambda p, d, o, w, f: setattr(w, "active", True),                                           lambda p, d, o, w, f: not w.active and _can_unlock(p, d, o, w, f)),
    ("Whip faster",     lambda p, d, o, w, f: setattr(w, "COOLDOWN", max(20, w.COOLDOWN - int(w.COOLDOWN * 0.1))), lambda p, d, o, w, f: w.active),
    ("Whip +1 dmg",     lambda p, d, o, w, f: setattr(w, "DAMAGE", w.DAMAGE + 1),                                  lambda p, d, o, w, f: w.active),
    ("Whip wider",      lambda p, d, o, w, f: setattr(w, "HALF_ARC", min(math.pi / 2, w.HALF_ARC + math.radians(10))), lambda p, d, o, w, f: w.active),
    ("Unlock Fireball", lambda p, d, o, w, f: setattr(f, "active", True),                                           lambda p, d, o, w, f: not f.active and _can_unlock(p, d, o, w, f)),
    ("Fireball faster", lambda p, d, o, w, f: setattr(f, "COOLDOWN", max(40, f.COOLDOWN - int(f.COOLDOWN * 0.1))), lambda p, d, o, w, f: f.active),
    ("Fireball +dmg",   lambda p, d, o, w, f: setattr(f, "base_damage", getattr(f, "base_damage", 3) + 1),         lambda p, d, o, w, f: f.active),
]


def run_upgrade_screen(fb, screen, player, dagger, orb, whip, fireball, clock, keys):
    """Block until the player picks one of 3 random upgrades."""
    available = [u for u in POOL if u[2](player, dagger, orb, whip, fireball)]
    choices = random.sample(available, min(3, len(available)))
    sel = 0
    fw, fh = fb.get_size()
    sw, sh = screen.get_size()
    card_w = fw // 3 - 4

    # card rects in fb space
    card_y = fh // 2 - 16
    cards = [(2 + i * (card_w + 4), card_y, card_w, 32) for i in range(len(choices))]

    def fb_mouse():
        mx, my = pygame.mouse.get_pos()
        return mx * fw // sw, my * fh // sh

    def card_at(mx, my):
        for i, (cx, cy, cw, ch) in enumerate(cards):
            if cx <= mx < cx + cw and cy <= my < cy + ch:
                return i
        return None

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); raise SystemExit
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_LEFT,  pygame.K_a): sel = (sel - 1) % len(choices)
                if event.key in (pygame.K_RIGHT, pygame.K_d): sel = (sel + 1) % len(choices)
                if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    choices[sel][1](player, dagger, orb, whip, fireball)
                    for k in keys: keys[k] = False
                    pygame.event.clear()
                    return
            if event.type == pygame.MOUSEMOTION:
                hit = card_at(*fb_mouse())
                if hit is not None:
                    sel = hit
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                hit = card_at(*fb_mouse())
                if hit is not None:
                    choices[hit][1](player, dagger, orb, whip, fireball)
                    for k in keys: keys[k] = False
                    pygame.event.clear()
                    return

        # darken existing fb content
        overlay = pygame.Surface((fw, fh), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        fb.blit(overlay, (0, 0))

        for i, (label, *_) in enumerate(choices):
            cx, cy, cw, ch = cards[i]
            color = (200, 180, 50) if i == sel else (60, 60, 80)
            pygame.draw.rect(fb, color, (cx, cy, cw, ch))
            surf = _font.render(label, True, (255, 255, 255))
            fb.blit(surf, (cx + 2, cy + 10))

        screen.blit(pygame.transform.scale(fb, screen.get_size()), (0, 0))
        pygame.display.update()
        clock.tick(60)
