import pygame

pygame.font.init()
_font = pygame.font.SysFont(None, 8)

def draw_hud(fb, player, frame, weapons):
    fw, fh = fb.get_size()

    # HP bar — top left
    BAR_W, BAR_H = 40, 4
    hp_ratio = max(player.hp, 0) / player.max_hp
    pygame.draw.rect(fb, (100, 0, 0),   (2, 2, BAR_W, BAR_H))
    pygame.draw.rect(fb, (220, 40, 40), (2, 2, int(BAR_W * hp_ratio), BAR_H))

    # XP bar — bottom full width
    xp_ratio = player.xp / player.xp_threshold()
    pygame.draw.rect(fb, (0, 0, 100),    (0, fh - 3, fw, 3))
    pygame.draw.rect(fb, (60, 120, 255), (0, fh - 3, int(fw * xp_ratio), 3))

    # Level — just right of HP bar
    lvl_surf = _font.render(f"Lv{player.level}", True, (255, 255, 255))
    fb.blit(lvl_surf, (BAR_W + 5, 2))

    # Timer — top right
    secs = frame // 60
    timer_surf = _font.render(f"{secs // 60:02d}:{secs % 60:02d}", True, (255, 255, 255))
    fb.blit(timer_surf, (fw - timer_surf.get_width() - 2, 2))

    # Weapon slots — bottom right, 3 fixed slots above XP bar
    # weapons: list of (color, active) up to 3 entries
    SLOT, GAP = 7, 2
    for i in range(3):
        x = fw - (SLOT + GAP) * (3 - i) + GAP
        y = fh - 3 - SLOT - 2
        if i < len(weapons):
            color, active = weapons[i]
            if active:
                pygame.draw.rect(fb, color, (x, y, SLOT, SLOT))
            else:
                pygame.draw.rect(fb, (50, 50, 50), (x, y, SLOT, SLOT), 1)
        else:
            pygame.draw.rect(fb, (30, 30, 30), (x, y, SLOT, SLOT), 1)
