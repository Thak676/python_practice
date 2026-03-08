import pygame

def run_start_menu(fb, screen, clock):
    """Blocking start menu. Returns when player presses any key or clicks."""
    fw, fh = fb.get_size()
    scale  = screen.get_width() / fw

    font_big  = pygame.font.SysFont(None, 22)
    font_small = pygame.font.SysFont(None, 13)

    title  = font_big.render("NAME PENDING", True, (255, 220, 60))
    prompt = font_small.render("press any key to start", True, (200, 200, 200))

    title_pos  = title.get_rect(centerx=fw // 2, centery=fh // 2 - 14)
    prompt_pos = prompt.get_rect(centerx=fw // 2, centery=fh // 2 + 4)

    blink = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); raise SystemExit
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                pygame.event.clear()
                return

        blink += 1
        fb.fill((10, 10, 20))
        fb.blit(title, title_pos)
        if (blink // 30) % 2 == 0:
            fb.blit(prompt, prompt_pos)
        screen.blit(pygame.transform.scale(fb, screen.get_size()), (0, 0))
        pygame.display.update()
        clock.tick(60)


def run_pause_menu(fb, screen, clock):
    """Overlay a pause screen on the current fb until Escape or any key resumes."""
    fw, fh = fb.get_size()

    font_big   = pygame.font.SysFont(None, 22)
    font_small = pygame.font.SysFont(None, 13)
    paused = font_big.render("PAUSED", True, (255, 255, 255))
    prompt = font_small.render("press esc to resume", True, (180, 180, 180))
    paused_pos = paused.get_rect(centerx=fw // 2, centery=fh // 2 - 10)
    prompt_pos = prompt.get_rect(centerx=fw // 2, centery=fh // 2 + 4)

    # snapshot the game frame; darken it as the background
    snapshot = fb.copy()
    dim = pygame.Surface((fw, fh), pygame.SRCALPHA)
    dim.fill((0, 0, 0, 140))

    # wait for the Escape key to be released first so it doesn't re-trigger
    while pygame.key.get_pressed()[pygame.K_ESCAPE]:
        pygame.event.pump()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); raise SystemExit
            if event.type == pygame.KEYDOWN:
                pygame.event.clear()
                return

        fb.blit(snapshot, (0, 0))
        fb.blit(dim, (0, 0))
        fb.blit(paused, paused_pos)
        fb.blit(prompt, prompt_pos)
        screen.blit(pygame.transform.scale(fb, screen.get_size()), (0, 0))
        pygame.display.update()
        clock.tick(60)
