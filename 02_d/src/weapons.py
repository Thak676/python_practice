import math
import pygame

class Projectile:
    SPEED  = 3
    RANGE  = 80  # px before it disappears
    RADIUS = 2
    COLOR  = (255, 220, 80)

    def __init__(self, x, y, vx, vy, damage=1):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.damage = damage
        self.traveled = 0.0
        self.dead = False

    def update(self, enemies):
        self.x += self.vx
        self.y += self.vy
        self.traveled += math.hypot(self.vx, self.vy)
        if self.traveled >= self.RANGE:
            self.dead = True
            return
        for e in enemies:
            if math.hypot(self.x - e.x, self.y - e.y) < self.RADIUS + 3:
                e.take_damage(self.damage)
                self.dead = True
                return

    def draw(self, fb, cam_x, cam_y):
        pygame.draw.circle(fb, self.COLOR,
                           (int(self.x - cam_x), int(self.y - cam_y)), self.RADIUS)


class OrbWeapon:
    RADIUS   = 20   # orbit radius in fb pixels
    PERIOD   = 120  # frames per full rotation
    ORB_R    = 3    # visual radius
    HIT_CD   = 30   # frames before same enemy can be hit again
    COLOR    = (120, 180, 255)

    def __init__(self, count=1):
        self.count = count          # number of orbs
        self.angle = 0.0            # shared rotation angle
        self.hit_timers: dict = {}  # enemy id → frames until rehittable

    def _orb_positions(self, cx, cy):
        step = 2 * math.pi / self.count
        return [
            (cx + self.RADIUS * math.cos(self.angle + i * step),
             cy + self.RADIUS * math.sin(self.angle + i * step))
            for i in range(self.count)
        ]

    def update(self, player, enemies):
        if self.count == 0:
            return
        self.angle += 2 * math.pi / self.PERIOD
        # tick down hit cooldowns
        self.hit_timers = {eid: t - 1 for eid, t in self.hit_timers.items() if t > 1}
        for ox, oy in self._orb_positions(player.cx, player.cy):
            for e in enemies:
                if id(e) in self.hit_timers:
                    continue
                if math.hypot(ox - e.x, oy - e.y) < self.ORB_R + 3:
                    e.take_damage(1)
                    self.hit_timers[id(e)] = self.HIT_CD

    def draw(self, fb, player, cam_x, cam_y):
        if self.count == 0:
            return
        for ox, oy in self._orb_positions(player.cx, player.cy):
            pygame.draw.circle(fb, self.COLOR,
                               (int(ox - cam_x), int(oy - cam_y)), self.ORB_R)


class Dagger:
    COOLDOWN = 60  # frames between shots

    def __init__(self):
        self.timer = 0
        self.base_damage = 1

    def update(self, player, projectiles):
        self.timer += 1
        if self.timer < self.COOLDOWN:
            return
        self.timer = 0
        vx = Projectile.SPEED if player.facing_right else -Projectile.SPEED
        projectiles.append(Projectile(player.cx, player.cy, vx, 0, self.base_damage))


class Whip:
    COOLDOWN  = 90   # frames between swings
    RANGE     = 30   # reach in fb pixels
    HALF_ARC  = math.radians(40)  # half-angle of the cone
    SHOW_FOR  = 10   # frames the arc stays visible
    COLOR     = (255, 140, 40)
    DAMAGE    = 2

    def __init__(self):
        self.timer    = 0
        self.visible  = 0   # counts down for drawing

    def update(self, player, enemies):
        self.timer += 1
        if self.visible > 0:
            self.visible -= 1
        if self.timer < self.COOLDOWN:
            return
        self.timer   = 0
        self.visible = self.SHOW_FOR
        # centre angle: 0 = right, π = left
        base = 0.0 if player.facing_right else math.pi
        for e in enemies:
            dx, dy = e.x - player.cx, e.y - player.cy
            dist = math.hypot(dx, dy)
            if dist > self.RANGE:
                continue
            angle = math.atan2(dy, dx)
            diff  = (angle - base + math.pi) % (2 * math.pi) - math.pi
            if abs(diff) <= self.HALF_ARC:
                e.take_damage(self.DAMAGE)

    def draw(self, fb, player, cam_x, cam_y):
        if self.visible <= 0:
            return
        base  = 0.0 if player.facing_right else math.pi
        sx    = int(player.cx - cam_x)
        sy    = int(player.cy - cam_y)
        start = base - self.HALF_ARC
        stop  = base + self.HALF_ARC
        rect  = pygame.Rect(sx - self.RANGE, sy - self.RANGE,
                            self.RANGE * 2, self.RANGE * 2)
        pygame.draw.arc(fb, self.COLOR, rect, -stop, -start, 3)


class FireballProjectile:
    SPEED       = 1.5
    RADIUS      = 3
    SPLASH_R    = 12  # splash damage radius on impact
    SPLASH_DMG  = 2
    COLOR       = (255, 80, 20)
    RANGE       = 100

    def __init__(self, x, y, vx, vy, damage=3):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.damage = damage
        self.traveled = 0.0
        self.dead = False

    def update(self, enemies):
        self.x += self.vx
        self.y += self.vy
        self.traveled += math.hypot(self.vx, self.vy)
        if self.traveled >= self.RANGE:
            self.dead = True
            return
        for e in enemies:
            if math.hypot(self.x - e.x, self.y - e.y) < self.RADIUS + 3:
                e.take_damage(self.damage)
                # splash
                for other in enemies:
                    if math.hypot(self.x - other.x, self.y - other.y) < self.SPLASH_R:
                        other.take_damage(self.SPLASH_DMG)
                self.dead = True
                return

    def draw(self, fb, cam_x, cam_y):
        pygame.draw.circle(fb, self.COLOR,
                           (int(self.x - cam_x), int(self.y - cam_y)), self.RADIUS)


class Fireball:
    COOLDOWN = 120
    active   = False

    def __init__(self):
        self.timer = 0
        self.base_damage = 3
        self.active = False

    def update(self, player, enemies, projectiles):
        self.timer += 1
        if self.timer < self.COOLDOWN or not enemies:
            return
        self.timer = 0
        nearest = min(enemies, key=lambda e: math.hypot(e.x - player.cx, e.y - player.cy))
        dx, dy = nearest.x - player.cx, nearest.y - player.cy
        dist = math.hypot(dx, dy)
        if dist == 0:
            return
        speed = FireballProjectile.SPEED
        projectiles.append(FireballProjectile(player.cx, player.cy,
                                              speed * dx / dist, speed * dy / dist,
                                              self.base_damage))
