
from Circle import Circle
from pygame.math import Vector2

from random import randint

Vec2 = Vector2

enemies = []
_colliding = []

speed = 0.3

_framecount = 0

def update_and_draw(fb, CAMERA, m, keys):

    global _framecount
    global _colliding

    # update
    _framecount += 1
    if (_framecount % 180 == 0):
        c = Circle(randint(0, CAMERA[0]), randint(0, CAMERA[1]), 4, (255, 0, 0))
        enemies.append(c)
    if (_framecount % 30 == 0):
        for c in _colliding:
            print(c)

    m.x += keys["right"] - keys["left"]
    m.y += keys["down"] - keys["up"]
    for c in enemies:
        vec2 = Vec2(m.x - c.x, m.y - c.y)
        # ought to work but doesn't:
        #vec2 = Vec2(m.pos - c.pos)
        vec2.normalize_ip()
        c.pos += vec2 * speed

    # draw
    fb.fill((20, 20, 20))
    m.draw(fb)
    colliding_temp = []
    for c in enemies:
        circ_rect = c.draw(fb)
        if m.rect.colliderect(circ_rect):
            colliding_temp.append(c)
    _colliding = colliding_temp
