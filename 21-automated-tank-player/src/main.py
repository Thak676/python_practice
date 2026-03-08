import pygame
import sys
import random

# ── Screen / grid ──────────────────────────────────────────────────────────
TILE      = 32               # pixels per tile
MAP_W     = 48               # map width  in tiles
MAP_H     = 36               # map height in tiles
VIEW_COLS = 16               # tiles visible horizontally  (16*32 = 512)
VIEW_ROWS = 14               # tiles visible vertically    (14*32 = 448)
SCREEN_W  = VIEW_COLS * TILE
SCREEN_H  = VIEW_ROWS * TILE
FPS       = 60
SLIDE_FRAMES  = 12           # frames a tank takes to cross one tile
BULLET_FRAMES = 3            # frames a bullet takes to cross one tile

# ── Directions ─────────────────────────────────────────────────────────────
RIGHT, DOWN, LEFT, UP = 0, 1, 2, 3
DX = [ 1,  0, -1,  0]
DY = [ 0,  1,  0, -1]
# clockwise rotation angle for each facing (sprite drawn facing right)
FACING_ANGLE = [0, 90, 180, 270]
DIR_KEY = {
    pygame.K_RIGHT: RIGHT, pygame.K_d: RIGHT,
    pygame.K_DOWN:  DOWN,  pygame.K_s: DOWN,
    pygame.K_LEFT:  LEFT,  pygame.K_a: LEFT,
    pygame.K_UP:    UP,    pygame.K_w: UP,
}

# ── Terrain IDs ────────────────────────────────────────────────────────────
GRASS  = 0
FOREST = 1

# ── 8-bit palette ──────────────────────────────────────────────────────────
G1  = (104, 168,  56)   # grass base
G2  = ( 88, 152,  40)   # grass dark
G3  = (120, 184,  72)   # grass light
F1  = ( 40, 104,  24)   # forest dark
F2  = ( 24,  80,  16)   # forest darker
F3  = ( 56, 128,  40)   # forest light
TB  = ( 72, 112,  48)   # tank body
TD  = ( 48,  80,  32)   # tank dark
TH  = (104, 144,  72)   # tank highlight
TT  = ( 32,  32,  24)   # tank track
TG  = ( 56,  80,  40)   # tank gun
BL  = (255, 224,   0)   # bullet
BL2 = (255, 128,   0)   # bullet glow
UIB = ( 24,  24,  24)   # ui bg
UIW = (240, 240, 200)   # ui text
GD  = ( 64,  80,  48)   # grid line colour


# ── Tile surface builders ───────────────────────────────────────────────────
def _make_grass_tile(rng: random.Random) -> pygame.Surface:
    s = pygame.Surface((TILE, TILE))
    s.fill(G1)
    for _ in range(18):
        x, y = rng.randrange(TILE), rng.randrange(TILE)
        s.set_at((x, y), rng.choice([G2, G3, G2]))
    # a few tiny blades
    for _ in range(5):
        x, y = rng.randint(2, TILE - 3), rng.randint(3, TILE - 2)
        pygame.draw.line(s, G3, (x, y), (x, y - 2))
    # 1-px dark border on right + bottom (tile grid)
    pygame.draw.line(s, GD, (TILE - 1, 0), (TILE - 1, TILE - 1))
    pygame.draw.line(s, GD, (0, TILE - 1), (TILE - 1, TILE - 1))
    return s


def _make_forest_tile(rng: random.Random) -> pygame.Surface:
    s = pygame.Surface((TILE, TILE))
    s.fill(F1)
    # chunky tree canopy
    pygame.draw.rect(s, F2, (4,  6, 24, 22), border_radius=4)
    pygame.draw.rect(s, F1, (6,  4, 20, 20), border_radius=3)
    pygame.draw.rect(s, F3, (8,  6,  7,  7))
    pygame.draw.rect(s, F3, (17, 15,  6,  6))
    pygame.draw.rect(s, F2, (6, 24, 20,  4))   # shadow bottom
    for _ in range(6):
        x, y = rng.randrange(4, TILE - 4), rng.randrange(4, TILE - 4)
        s.set_at((x, y), F2)
    pygame.draw.line(s, GD, (TILE - 1, 0), (TILE - 1, TILE - 1))
    pygame.draw.line(s, GD, (0, TILE - 1), (TILE - 1, TILE - 1))
    return s


# ── Tank sprite (faces RIGHT at angle=0) ───────────────────────────────────
def _make_tank_surf() -> pygame.Surface:
    """Draw a top-down chunky 8-bit tank on a 32×32 transparent surface."""
    s = pygame.Surface((TILE, TILE), pygame.SRCALPHA)

    # Tracks (top & bottom strips)
    for ty in (3, 22):
        pygame.draw.rect(s, TT, (3, ty, 26, 7))
        # track segments
        for i in range(5):
            pygame.draw.rect(s, (20, 20, 15), (3 + i * 5, ty, 2, 7))
        pygame.draw.rect(s, (50, 50, 42), (3, ty, 26, 2))        # top sheen

    # Hull
    pygame.draw.rect(s, TB, (5, 8, 22, 16))
    pygame.draw.rect(s, TH, (6, 8, 20, 3))    # top highlight
    pygame.draw.rect(s, TD, (5, 21, 22, 3))   # bottom shadow
    pygame.draw.rect(s, TD, (5,  8,  3, 16))  # left side
    pygame.draw.rect(s, TD, (24, 8,  3, 16))  # right side

    # Turret dome (centre)
    pygame.draw.rect(s, TB,  (10, 11, 12, 10), border_radius=3)
    pygame.draw.rect(s, TH,  (11, 11, 10,  3))   # highlight
    pygame.draw.rect(s, TD,  (10, 18, 12,  3))   # shadow

    # Gun barrel (points right)
    pygame.draw.rect(s, TG, (20, 14, 10, 4))
    pygame.draw.rect(s, TD, (20, 17, 10, 1))   # barrel underside
    # Muzzle band
    pygame.draw.rect(s, TD, (28, 13, 3, 6))

    return s


def _build_tank_rotations(base: pygame.Surface) -> list[pygame.Surface]:
    """Return [RIGHT, DOWN, LEFT, UP] rotated surfaces."""
    return [pygame.transform.rotate(base, -FACING_ANGLE[d]) for d in range(4)]


# ── TileMap ─────────────────────────────────────────────────────────────────
class TileMap:
    def __init__(self, rng: random.Random):
        self.tiles = [[GRASS] * MAP_W for _ in range(MAP_H)]

        # Sprinkle forest clusters
        for _ in range(80):
            cx, cy = rng.randrange(MAP_W), rng.randrange(MAP_H)
            r = rng.randint(1, 4)
            for dy in range(-r, r + 1):
                for dx in range(-r, r + 1):
                    if dx * dx + dy * dy <= r * r and rng.random() < 0.75:
                        nx, ny = cx + dx, cy + dy
                        if 0 <= nx < MAP_W and 0 <= ny < MAP_H:
                            self.tiles[ny][nx] = FOREST

        # Clear start area
        sx, sy = MAP_W // 2, MAP_H // 2
        for dy in range(-3, 4):
            for dx in range(-3, 4):
                nx, ny = sx + dx, sy + dy
                if 0 <= nx < MAP_W and 0 <= ny < MAP_H:
                    self.tiles[ny][nx] = GRASS

        self._grass  = _make_grass_tile(rng)
        self._forest = _make_forest_tile(rng)

    def terrain(self, gx: int, gy: int) -> int:
        if 0 <= gx < MAP_W and 0 <= gy < MAP_H:
            return self.tiles[gy][gx]
        return FOREST  # out-of-bounds = impassable

    def in_bounds(self, gx: int, gy: int) -> bool:
        return 0 <= gx < MAP_W and 0 <= gy < MAP_H

    def draw(self, screen: pygame.Surface, cam_x: int, cam_y: int):
        c0 = cam_x // TILE
        r0 = cam_y // TILE
        for r in range(r0, min(r0 + VIEW_ROWS + 2, MAP_H)):
            for c in range(c0, min(c0 + VIEW_COLS + 2, MAP_W)):
                px = c * TILE - cam_x
                py = r * TILE - cam_y
                if self.tiles[r][c] == GRASS:
                    screen.blit(self._grass,  (px, py))
                else:
                    screen.blit(self._forest, (px, py))


# ── Bullet ───────────────────────────────────────────────────────────────────
class Bullet:
    def __init__(self, gx: int, gy: int, direction: int):
        self.gx = gx          # current grid cell
        self.gy = gy
        self.direction = direction
        self._slide = 0       # progress across current tile (0..BULLET_FRAMES)
        self.alive = True

    # pixel position of bullet centre
    def pixel_pos(self) -> tuple[float, float]:
        frac = self._slide / BULLET_FRAMES
        px = (self.gx + DX[self.direction] * frac) * TILE + TILE // 2
        py = (self.gy + DY[self.direction] * frac) * TILE + TILE // 2
        return px, py

    def update(self, tilemap: TileMap):
        self._slide += 1
        if self._slide >= BULLET_FRAMES:
            self._slide = 0
            self.gx += DX[self.direction]
            self.gy += DY[self.direction]
            if not tilemap.in_bounds(self.gx, self.gy):
                self.alive = False

    def draw(self, screen: pygame.Surface, cam_x: int, cam_y: int):
        px, py = self.pixel_pos()
        sx = int(px) - cam_x
        sy = int(py) - cam_y
        pygame.draw.rect(screen, BL2, (sx - 4, sy - 4, 8, 8))
        pygame.draw.rect(screen, BL,  (sx - 3, sy - 3, 6, 6))
        pygame.draw.rect(screen, (255, 255, 255), (sx - 1, sy - 1, 2, 2))


# ── Tank ─────────────────────────────────────────────────────────────────────
class Tank:
    RELOAD = 12   # frames between shots

    def __init__(self, gx: int, gy: int, rots: list[pygame.Surface]):
        self.gx = gx          # grid position
        self.gy = gy
        self.facing = RIGHT
        self._rots  = rots    # [RIGHT,DOWN,LEFT,UP] surfaces

        self._sliding   = False
        self._slide_f   = 0   # frame counter for current slide
        self._prev_gx   = gx
        self._prev_gy   = gy
        self._queued    = None  # one queued direction
        self._cooldown  = 0

    # pixel centre of the tank (used for camera + drawing)
    def pixel_pos(self) -> tuple[float, float]:
        if self._sliding:
            frac = self._slide_f / SLIDE_FRAMES
            px = (self._prev_gx * (1 - frac) + self.gx * frac) * TILE + TILE // 2
            py = (self._prev_gy * (1 - frac) + self.gy * frac) * TILE + TILE // 2
        else:
            px = self.gx * TILE + TILE // 2
            py = self.gy * TILE + TILE // 2
        return px, py

    def _try_move(self, direction: int, tilemap: TileMap):
        nx = self.gx + DX[direction]
        ny = self.gy + DY[direction]
        if tilemap.in_bounds(nx, ny):
            self._prev_gx, self._prev_gy = self.gx, self.gy
            self.gx, self.gy = nx, ny
            self.facing = direction
            self._sliding = True
            self._slide_f = 0
        else:
            self.facing = direction   # turn in place

    def input(self, direction: int, tilemap: TileMap):
        if not self._sliding:
            self._try_move(direction, tilemap)
        else:
            self._queued = direction

    def shoot(self) -> "Bullet | None":
        if self._cooldown > 0:
            return None
        self._cooldown = self.RELOAD
        # Bullet starts one tile ahead
        bx = self.gx + DX[self.facing]
        by = self.gy + DY[self.facing]
        return Bullet(bx, by, self.facing)

    def update(self, tilemap: TileMap):
        if self._cooldown > 0:
            self._cooldown -= 1

        if self._sliding:
            self._slide_f += 1
            if self._slide_f >= SLIDE_FRAMES:
                self._slide_f = 0
                self._sliding = False
                if self._queued is not None:
                    d = self._queued
                    self._queued = None
                    self._try_move(d, tilemap)

    def draw(self, screen: pygame.Surface, cam_x: int, cam_y: int):
        px, py = self.pixel_pos()
        sx = int(px) - cam_x
        sy = int(py) - cam_y

        # Drop shadow
        shad = pygame.Surface((28, 10), pygame.SRCALPHA)
        pygame.draw.ellipse(shad, (0, 0, 0, 70), shad.get_rect())
        screen.blit(shad, (sx - 14 + 3, sy - 5 + 14))

        surf = self._rots[self.facing]
        screen.blit(surf, surf.get_rect(center=(sx, sy)))


# ── HUD ──────────────────────────────────────────────────────────────────────
def draw_hud(screen: pygame.Surface, tank: Tank, font: pygame.font.Font):
    # Reload pip meter
    bar_x, bar_y = 8, SCREEN_H - 26
    label = font.render("AMMO", True, UIW)
    screen.blit(label, (bar_x, bar_y - 14))
    pips = Tank.RELOAD
    filled = pips - tank._cooldown
    for i in range(pips):
        col = BL if i < filled else (60, 60, 50)
        pygame.draw.rect(screen, col, (bar_x + i * 10, bar_y, 8, 10))
        pygame.draw.rect(screen, UIB, (bar_x + i * 10, bar_y, 8, 10), 1)

    # Controls hint (top-right)
    hints = ["Arrows/WASD: move", "Space: fire", "Esc: quit"]
    for i, h in enumerate(hints):
        s = font.render(h, True, UIW)
        screen.blit(s, (SCREEN_W - s.get_width() - 8, 8 + i * 14))


# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Tank Wars")
    clock = pygame.time.Clock()

    font = pygame.font.SysFont("monospace", 11, bold=True)

    rng = random.Random(7)
    tilemap = TileMap(rng)

    tank_rots = _build_tank_rotations(_make_tank_surf())
    tank = Tank(MAP_W // 2, MAP_H // 2, tank_rots)
    bullets: list[Bullet] = []

    held: dict[int, bool] = {}   # direction keys currently held

    while True:
        # ── Events ─────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                if event.key in DIR_KEY:
                    held[event.key] = True
                    tank.input(DIR_KEY[event.key], tilemap)
                if event.key == pygame.K_SPACE:
                    b = tank.shoot()
                    if b:
                        bullets.append(b)
            if event.type == pygame.KEYUP:
                held.pop(event.key, None)

        # Hold-to-move: re-trigger movement each time tank finishes a step
        if not tank._sliding and held:
            for k in (pygame.K_RIGHT, pygame.K_d, pygame.K_DOWN, pygame.K_s,
                      pygame.K_LEFT, pygame.K_a, pygame.K_UP, pygame.K_w):
                if held.get(k):
                    tank.input(DIR_KEY[k], tilemap)
                    break

        # Hold space to fire at reload rate
        if pygame.key.get_pressed()[pygame.K_SPACE]:
            b = tank.shoot()
            if b:
                bullets.append(b)

        # ── Update ─────────────────────────────────────────────────────────
        tank.update(tilemap)
        for b in bullets:
            b.update(tilemap)
        bullets = [b for b in bullets if b.alive]

        # ── Camera (smooth pixel follow, clamped to map) ────────────────────
        px, py = tank.pixel_pos()
        cam_x = int(px - SCREEN_W / 2)
        cam_y = int(py - SCREEN_H / 2)
        cam_x = max(0, min(MAP_W * TILE - SCREEN_W, cam_x))
        cam_y = max(0, min(MAP_H * TILE - SCREEN_H, cam_y))

        # ── Draw ────────────────────────────────────────────────────────────
        tilemap.draw(screen, cam_x, cam_y)

        for b in bullets:
            b.draw(screen, cam_x, cam_y)

        tank.draw(screen, cam_x, cam_y)

        draw_hud(screen, tank, font)

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
