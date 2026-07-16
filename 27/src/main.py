#!/usr/bin/env python3
"""
Kingdom of Eldenmere — Medieval Fantasy Simulator
Tile-based world with procedural generation.

Controls
--------
WASD / Arrow keys  Pan camera
Scroll wheel       Zoom in / out
Right-click drag   Pan camera
Left-click         Select / inspect tile
Escape             Quit
"""

import math
import random
import sys
from dataclasses import dataclass
from enum import Enum, auto

import pygame

# ─────────────────────────────────────────────────────────────────────────────
#  CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────
SCREEN_W     = 1280
SCREEN_H     = 720
FPS          = 60
TILE_SIZE    = 64
MAP_W        = 80
MAP_H        = 60
UI_H         = 90
MIN_ZOOM     = 0.35
MAX_ZOOM     = 2.5
PAN_SPEED    = 480          # pixels / second (at zoom 1)
MINIMAP_W    = 200
MINIMAP_H    = MINIMAP_W * MAP_H // MAP_W
KINGDOM_NAME = "Eldenmere"

BG        = (14,  10,   6)
UI_BG     = (16,  12,   7)
UI_BORDER = (72,  52,  28)
GOLD      = (215, 180,  92)
TXT       = (195, 175, 135)
TXT2      = (152, 138, 110)
TXT3      = (112, 102,  82)
DIM       = (102,  92,  72)
SEL       = (255, 215,  38)

# ─────────────────────────────────────────────────────────────────────────────
#  TILE DEFINITIONS
# ─────────────────────────────────────────────────────────────────────────────
class T(Enum):
    DEEP_WATER   = auto()
    WATER        = auto()
    SAND         = auto()
    PLAINS       = auto()
    FOREST       = auto()
    DENSE_FOREST = auto()
    HILLS        = auto()
    MOUNTAIN     = auto()
    SNOW         = auto()
    ROAD         = auto()
    TOWN         = auto()
    CASTLE       = auto()


# (base_rgb, label, flavour)
TILE_META: dict[T, tuple[tuple[int, int, int], str, str]] = {
    T.DEEP_WATER:   ((18,  55, 145), "Deep Water",    "Treacherous depths, home to ancient leviathans."),
    T.WATER:        ((45, 105, 195), "Water",          "Rivers, lakes, and shallow coastal seas."),
    T.SAND:         ((208,186, 125), "Sand",           "Barren shores and wind-swept dunes."),
    T.PLAINS:       ((118, 182,  58), "Plains",        "Fertile grasslands ripe for cultivation."),
    T.FOREST:       ((36,  108,  36), "Forest",        "Woodland rich with game and wild herbs."),
    T.DENSE_FOREST: ((14,   58,  14), "Dense Forest",  "Ancient, dark wood few dare to enter."),
    T.HILLS:        ((142, 135,  85), "Hills",         "Rolling highlands dotted with sheep and watchtowers."),
    T.MOUNTAIN:     ((104,  98,  92), "Mountain",      "Impassable rocky peaks, rich in iron and copper."),
    T.SNOW:         ((205, 216, 230), "Snow Peak",     "Frozen summits, haunt of gryphons and ice-drakes."),
    T.ROAD:         ((165, 145,  95), "Road",          "Cobblestone road connecting the kingdom's settlements."),
    T.TOWN:         ((185, 135,  65), "Town",          "A bustling market settlement of ~500 souls."),
    T.CASTLE:       ((135,  85, 155), "Castle",        "Seat of power. Lord Aldric rules from these walls."),
}

# ─────────────────────────────────────────────────────────────────────────────
#  PROCEDURAL WORLD GENERATION
# ─────────────────────────────────────────────────────────────────────────────
def _slerp(a: float, b: float, t: float) -> float:
    """Smoothstep-interpolated lerp."""
    t = t * t * (3 - 2 * t)
    return a + t * (b - a)


def value_noise(w: int, h: int, seed: int) -> list[list[float]]:
    """Multi-octave value noise → values normalised to [0, 1]."""
    rng    = random.Random(seed)
    result = [[0.0] * w for _ in range(h)]
    specs  = [(5, 1.00), (11, 0.50), (22, 0.25), (3, 0.12)]

    for scale, amp in specs:
        cw   = w // scale + 3
        ch   = h // scale + 3
        ctrl = [[rng.random() for _ in range(cw)] for _ in range(ch)]
        for y in range(h):
            for x in range(w):
                gx  = x / scale
                gy  = y / scale
                ix  = min(int(gx), cw - 2)
                iy  = min(int(gy), ch - 2)
                fx  = gx - int(gx)
                fy  = gy - int(gy)
                top = _slerp(ctrl[iy  ][ix], ctrl[iy  ][ix + 1], fx)
                bot = _slerp(ctrl[iy+1][ix], ctrl[iy+1][ix + 1], fx)
                result[y][x] += _slerp(top, bot, fy) * amp

    flat   = [v for row in result for v in row]
    lo, hi = min(flat), max(flat)
    span   = hi - lo
    for y in range(h):
        for x in range(w):
            result[y][x] = (result[y][x] - lo) / span
    return result


def build_world(seed: int) -> list[list[T]]:
    """Generate the tile map with procedural terrain + pre-placed kingdom."""
    hmap = value_noise(MAP_W, MAP_H, seed)
    fmap = value_noise(MAP_W, MAP_H, seed ^ 0xBEEF)

    tiles: list[list[T]] = []
    for y in range(MAP_H):
        row: list[T] = []
        for x in range(MAP_W):
            h = hmap[y][x]
            f = fmap[y][x]

            # Push sea toward edges → creates island / continent silhouette
            dx = abs(x - MAP_W / 2) / (MAP_W / 2)
            dy = abs(y - MAP_H / 2) / (MAP_H / 2)
            h  = max(0.0, h - max(dx, dy) ** 1.5 * 0.70)

            if   h < 0.18:   tile = T.DEEP_WATER
            elif h < 0.30:   tile = T.WATER
            elif h < 0.36:   tile = T.SAND
            elif h < 0.68:
                if   f > 0.66: tile = T.DENSE_FOREST
                elif f > 0.40: tile = T.FOREST
                else:          tile = T.PLAINS
            elif h < 0.80:   tile = T.HILLS
            elif h < 0.90:   tile = T.MOUNTAIN
            else:            tile = T.SNOW

            row.append(tile)
        tiles.append(row)

    # ── Stamp the starting kingdom ────────────────────────────────────────────
    cx, cy = MAP_W // 2, MAP_H // 2

    # Clear a flat pastoral zone first
    for dy in range(-3, 5):
        for dx in range(-4, 9):
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < MAP_W and 0 <= ny < MAP_H:
                tiles[ny][nx] = T.PLAINS

    # Place kingdom structures
    structures = [
        (cx,   cy,   T.CASTLE),
        (cx+1, cy,   T.ROAD),
        (cx+2, cy,   T.ROAD),
        (cx+3, cy,   T.ROAD),
        (cx+4, cy,   T.TOWN),
        (cx+2, cy-1, T.ROAD),   # spur road north
        (cx+2, cy+1, T.ROAD),   # spur road south
    ]
    for sx, sy2, st in structures:
        if 0 <= sx < MAP_W and 0 <= sy2 < MAP_H:
            tiles[sy2][sx] = st

    return tiles


# ─────────────────────────────────────────────────────────────────────────────
#  TILE ART  (pre-rendered surfaces)
# ─────────────────────────────────────────────────────────────────────────────
def _tree(surf: pygame.Surface, cx: int, cy: int, h: int,
          crown: tuple[int, int, int], trunk: tuple[int, int, int]) -> None:
    hw = max(1, h // 2)
    pygame.draw.polygon(surf, crown, [(cx, cy - h), (cx - hw, cy), (cx + hw, cy)])
    pygame.draw.line(surf, trunk, (cx, cy), (cx, cy + h // 5), 2)


def make_tile_surf(tile: T, size: int) -> pygame.Surface:  # noqa: C901
    surf = pygame.Surface((size, size))
    col  = TILE_META[tile][0]
    surf.fill(col)
    rng  = random.Random(tile.value * 31337)
    s    = size

    if tile == T.DEEP_WATER:
        lc = (28, 75, 172)
        for _ in range(3):
            y1 = rng.randint(s//6, s - s//6)
            y2 = y1 + rng.randint(-s//8, s//8)
            pygame.draw.line(surf, lc, (0, y1), (s, y2), 1)

    elif tile == T.WATER:
        wc = (72, 142, 222)
        for i in range(4):
            base = s // 6 + i * (s // 5)
            pts  = [(x, base + int(3 * math.sin(x * 0.28 + i * 1.6))) for x in range(0, s, 3)]
            if len(pts) >= 2:
                pygame.draw.lines(surf, wc, False, pts, 1)

    elif tile == T.SAND:
        for _ in range(16):
            pygame.draw.circle(surf, (188, 165, 105),
                               (rng.randint(0, s-1), rng.randint(0, s-1)), 1)

    elif tile == T.PLAINS:
        gc = (78, 145, 30)
        for _ in range(11):
            px = rng.randint(4, s-4)
            py = rng.randint(6, s-3)
            gh = rng.randint(4, 9)
            pygame.draw.line(surf, gc, (px, py), (px-2, py-gh), 1)
            pygame.draw.line(surf, gc, (px, py), (px+2, py-gh), 1)

    elif tile in (T.FOREST, T.DENSE_FOREST):
        count = 5 if tile == T.DENSE_FOREST else 3
        crown = (12, 50, 12) if tile == T.DENSE_FOREST else (30, 92, 30)
        trunk = (55, 30, 10)
        for _ in range(count):
            tx2 = rng.randint(s//5, s - s//5)
            ty2 = rng.randint(s//4, s - s//8)
            _tree(surf, tx2, ty2, rng.randint(s//5, s//3), crown, trunk)

    elif tile == T.HILLS:
        hc = (162, 155, 105)
        for _ in range(2):
            hx = rng.randint(s//4, 3*s//4)
            hy = s - rng.randint(s//5, s//3)
            r  = rng.randint(s//3, s*2//3)
            pygame.draw.arc(surf, hc, (hx-r, hy-r//2, r*2, r), 0, math.pi, 3)

    elif tile in (T.MOUNTAIN, T.SNOW):
        dark  = (72, 68, 64)
        lite  = (132, 125, 118)
        pts_d = [(s//2, s//10), (s//8, 7*s//8), (s//2, 5*s//8)]
        pts_l = [(s//2, s//10), (s//2, 5*s//8), (7*s//8, 7*s//8)]
        pygame.draw.polygon(surf, dark, pts_d)
        pygame.draw.polygon(surf, lite, pts_l)
        if tile == T.SNOW:
            cap = [(s//2, s//10), (s*2//5, s*3//8), (s*3//5, s*3//8)]
            pygame.draw.polygon(surf, (225, 232, 245), cap)

    elif tile == T.ROAD:
        pygame.draw.rect(surf, (185, 165, 112), (0, s//3, s, s//3))
        lc = (148, 130, 82)
        for ix in range(0, s, s//5):
            pygame.draw.line(surf, lc, (ix, s//3), (ix, 2*s//3), 1)
        pygame.draw.line(surf, lc, (0, s//2), (s, s//2), 1)

    elif tile == T.TOWN:
        wall  = (150, 106,  50)
        roof  = (135,  46,  26)
        win_c = (228, 202, 130)
        bldgs = [
            (s//10,          s*2//5, s*3//10, s*3//5),
            (s*2//5 - s//16, s*3//10, s//4,  s*6//10),
            (s*13//20,       s*2//5, s*3//10, s*3//5),
        ]
        for bx, by, bw, bh in bldgs:
            wh = bh * 2 // 3
            pygame.draw.rect(surf, wall, (bx, by + bh - wh, bw, wh))
            pygame.draw.polygon(surf, roof, [(bx, by+bh-wh), (bx+bw//2, by), (bx+bw, by+bh-wh)])
            pygame.draw.rect(surf, win_c, (bx + bw//2 - 2, by + bh - wh + wh//3, 4, 4))

    elif tile == T.CASTLE:
        wc  = (95,  60, 110)   # wall
        tc  = (75,  46,  90)   # tower
        mc  = (115, 76, 130)   # merlon
        gc  = (10,   6,  14)   # gate

        pygame.draw.rect(surf, wc, (s//6, 2*s//5, 2*s//3, s*11//20))
        for tx3 in (s//10, s*11//20):
            pygame.draw.rect(surf, tc, (tx3, s//5, s//4, s*13//20))
            for mx in range(tx3, tx3 + s//4, s//14):
                pygame.draw.rect(surf, mc, (mx, s//5 - s//10, s//16, s//12))
        for mx in range(s//6, s*5//6, s//10):
            pygame.draw.rect(surf, mc, (mx, 2*s//5 - s//10, s//14, s//12))
        gate = pygame.Rect(s//2 - s//10, 2*s//5 + s//5, s//5, s//3)
        pygame.draw.rect(surf, gc, gate)
        pygame.draw.ellipse(surf, gc, (gate.x, gate.y - gate.height//3,
                                       gate.width, gate.height//3))

    pygame.draw.rect(surf, (0, 0, 0), (0, 0, s, s), 1)
    return surf


def build_tile_cache(size: int) -> dict[T, pygame.Surface]:
    return {tile: make_tile_surf(tile, size) for tile in T}


# ─────────────────────────────────────────────────────────────────────────────
#  MINIMAP
# ─────────────────────────────────────────────────────────────────────────────
def build_minimap(tiles: list[list[T]]) -> pygame.Surface:
    raw = pygame.Surface((MAP_W, MAP_H))
    for y in range(MAP_H):
        for x in range(MAP_W):
            raw.set_at((x, y), TILE_META[tiles[y][x]][0])
    return pygame.transform.scale(raw, (MINIMAP_W, MINIMAP_H))


# ─────────────────────────────────────────────────────────────────────────────
#  CAMERA
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class Camera:
    """
    x, y = top-left corner of the viewport in 'zoomed world pixels'.
    Tile (tx, ty) renders at screen pos (tx*sz - x, ty*sz - y)
    where sz = TILE_SIZE * zoom.
    """
    x:    float = 0.0
    y:    float = 0.0
    zoom: float = 1.0

    def tile_under(self, sx: int, sy: int) -> tuple[int, int]:
        sz = TILE_SIZE * self.zoom
        return int((sx + self.x) / sz), int((sy + self.y) / sz)

    def clamp(self) -> None:
        sz = TILE_SIZE * self.zoom
        self.x = max(0.0, min(self.x, max(0.0, MAP_W * sz - SCREEN_W)))
        self.y = max(0.0, min(self.y, max(0.0, MAP_H * sz - (SCREEN_H - UI_H))))


# ─────────────────────────────────────────────────────────────────────────────
#  GAME
# ─────────────────────────────────────────────────────────────────────────────
class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption(f"Kingdom of {KINGDOM_NAME}  —  Medieval Simulator")
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        self.clock  = pygame.time.Clock()

        self.font_sm = pygame.font.SysFont("serif", 14)
        self.font_md = pygame.font.SysFont("serif", 18)
        self.font_lg = pygame.font.SysFont("serif", 22, bold=True)

        seed = random.randint(0, 0xFFFFFF)
        print(f"[{KINGDOM_NAME}] seed = {seed:#08x}")

        self.tiles      = build_world(seed)
        self.tile_cache = build_tile_cache(TILE_SIZE)
        self.minimap    = build_minimap(self.tiles)

        # Centre the viewport on the castle
        cx, cy = MAP_W // 2, MAP_H // 2
        self.cam = Camera(
            x=cx * TILE_SIZE - SCREEN_W / 2 + TILE_SIZE / 2,
            y=cy * TILE_SIZE - (SCREEN_H - UI_H) / 2 + TILE_SIZE / 2,
        )
        self.cam.clamp()

        self.hovered:  tuple[int, int] | None = None
        self.selected: tuple[int, int] | None = None

        # Panning state
        self._panning   = False
        self._pan_start = (0, 0)
        self._cam_at    = (0.0, 0.0)

        # Scaled tile cache (rebuilt on zoom change)
        self._scaled: dict[T, pygame.Surface] = {}
        self._rebuild_scaled()

        self.frame = 0

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _rebuild_scaled(self) -> None:
        sz = max(1, int(TILE_SIZE * self.cam.zoom))
        self._scaled = {
            t: pygame.transform.scale(s, (sz, sz))
            for t, s in self.tile_cache.items()
        }

    # ── Input ─────────────────────────────────────────────────────────────────
    def _handle_events(self, dt: float) -> None:
        mx, my = pygame.mouse.get_pos()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                pygame.quit(); sys.exit()

            if ev.type == pygame.MOUSEWHEEL:
                old = self.cam.zoom
                self.cam.zoom = max(MIN_ZOOM, min(MAX_ZOOM, old * (1.12 ** ev.y)))
                if self.cam.zoom != old:
                    r = self.cam.zoom / old
                    self.cam.x = mx * (r - 1) + self.cam.x * r
                    self.cam.y = my * (r - 1) + self.cam.y * r
                    self.cam.clamp()
                    self._rebuild_scaled()

            if ev.type == pygame.MOUSEBUTTONDOWN:
                if ev.button in (2, 3):
                    self._panning   = True
                    self._pan_start = (mx, my)
                    self._cam_at    = (self.cam.x, self.cam.y)
                elif ev.button == 1 and my < SCREEN_H - UI_H:
                    tx, ty = self.cam.tile_under(mx, my)
                    self.selected = (tx, ty) if 0 <= tx < MAP_W and 0 <= ty < MAP_H else None

            if ev.type == pygame.MOUSEBUTTONUP and ev.button in (2, 3):
                self._panning = False

            if ev.type == pygame.MOUSEMOTION and self._panning:
                self.cam.x = self._cam_at[0] - (mx - self._pan_start[0])
                self.cam.y = self._cam_at[1] - (my - self._pan_start[1])
                self.cam.clamp()

        # Keyboard pan
        keys  = pygame.key.get_pressed()
        spd   = PAN_SPEED * dt
        moved = False
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: self.cam.x -= spd; moved = True
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.cam.x += spd; moved = True
        if keys[pygame.K_UP]    or keys[pygame.K_w]: self.cam.y -= spd; moved = True
        if keys[pygame.K_DOWN]  or keys[pygame.K_s]: self.cam.y += spd; moved = True
        if moved: self.cam.clamp()

        # Update hover
        if my < SCREEN_H - UI_H:
            tx, ty = self.cam.tile_under(mx, my)
            self.hovered = (tx, ty) if 0 <= tx < MAP_W and 0 <= ty < MAP_H else None
        else:
            self.hovered = None

    # ── Rendering ─────────────────────────────────────────────────────────────
    def _draw_world(self) -> None:
        sz     = max(1, int(TILE_SIZE * self.cam.zoom))
        view_h = SCREEN_H - UI_H
        tx0 = max(0, int(self.cam.x // sz))
        ty0 = max(0, int(self.cam.y // sz))
        tx1 = min(MAP_W, tx0 + SCREEN_W // sz + 2)
        ty1 = min(MAP_H, ty0 + view_h   // sz + 2)

        # Draw tiles
        for ty in range(ty0, ty1):
            for tx in range(tx0, tx1):
                sx = tx * sz - int(self.cam.x)
                sy = ty * sz - int(self.cam.y)
                self.screen.blit(self._scaled[self.tiles[ty][tx]], (sx, sy))

        # Draw overlays (hover / selection) in a second pass
        hl = pygame.Surface((sz, sz), pygame.SRCALPHA)
        hl.fill((255, 255, 255, 52))
        for ty in range(ty0, ty1):
            for tx in range(tx0, tx1):
                sx = tx * sz - int(self.cam.x)
                sy = ty * sz - int(self.cam.y)
                if self.hovered == (tx, ty):
                    self.screen.blit(hl, (sx, sy))
                if self.selected == (tx, ty):
                    pygame.draw.rect(self.screen, SEL, (sx, sy, sz, sz), 2)

    def _draw_ui(self) -> None:
        uy = SCREEN_H - UI_H
        pygame.draw.rect(self.screen, UI_BG, (0, uy, SCREEN_W, UI_H))
        pygame.draw.line(self.screen, UI_BORDER, (0, uy), (SCREEN_W, uy), 2)

        self.screen.blit(
            self.font_lg.render(f"Kingdom of {KINGDOM_NAME}", True, GOLD),
            (14, uy + 8),
        )

        ref = self.selected or self.hovered
        if ref:
            tx, ty   = ref
            _, name, desc = TILE_META[self.tiles[ty][tx]]
            self.screen.blit(self.font_md.render(name, True, TXT),  (14, uy + 34))
            self.screen.blit(self.font_sm.render(desc, True, TXT2), (14, uy + 56))
            self.screen.blit(
                self.font_sm.render(f"  x {tx},  y {ty}", True, TXT3),
                (14, uy + 73),
            )
        else:
            self.screen.blit(
                self.font_sm.render("Hover or click a tile to inspect it.", True, DIM),
                (14, uy + 40),
            )

        hints = [
            "WASD / Arrows — Pan",
            "Scroll — Zoom",
            "Right-drag — Pan",
            "Left-click — Select tile",
        ]
        for i, line in enumerate(hints):
            self.screen.blit(self.font_sm.render(line, True, DIM), (SCREEN_W - 192, uy + 8 + i * 17))

    def _draw_minimap(self) -> None:
        pad = 8
        ox  = SCREEN_W - MINIMAP_W - pad
        oy  = pad
        pygame.draw.rect(self.screen, (6, 4, 2), (ox-2, oy-2, MINIMAP_W+4, MINIMAP_H+4))
        self.screen.blit(self.minimap, (ox, oy))

        sz  = TILE_SIZE * self.cam.zoom
        vx  = int(self.cam.x / (sz * MAP_W) * MINIMAP_W)
        vy  = int(self.cam.y / (sz * MAP_H) * MINIMAP_H)
        vw  = max(2, int(SCREEN_W / sz / MAP_W * MINIMAP_W))
        vh2 = max(2, int((SCREEN_H - UI_H) / sz / MAP_H * MINIMAP_H))
        vx  = max(0, min(vx, MINIMAP_W - vw))
        vy  = max(0, min(vy, MINIMAP_H - vh2))
        pygame.draw.rect(self.screen, SEL, (ox + vx, oy + vy, vw, vh2), 1)

    # ── Main loop ─────────────────────────────────────────────────────────────
    def run(self) -> None:
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            self.frame += 1
            self._handle_events(dt)
            self.screen.fill(BG)
            self._draw_world()
            self._draw_ui()
            self._draw_minimap()
            pygame.display.flip()


# ─────────────────────────────────────────────────────────────────────────────
def main() -> None:
    Game().run()


if __name__ == "__main__":
    main()
