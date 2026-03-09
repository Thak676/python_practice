
import pygame
import global_vars
keys = global_vars.keys
from funcs import init, pe
from Image_Rect import Image_Rect
IR = Image_Rect

screen, clock = init(1760, 1024)

class Player:
    def __init__(self, file_path: str, x: float, y: float):
        self.img: pygame.Surface = pygame.image.load(file_path)
        self.img.convert_alpha()
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x, y, self.img.get_width(), self.img.get_height())

player = Player("data/m_03_02.png", 10.0, 10.0)
m_img: pygame.Surface = pygame.image.load("data/m_03_02.png")
background = IR("data/background.png", 0, 0)
rock = IR("data/rock 01.png", 64, 64)
enemy = IR("data/enemy_01.png", 128, 128)

collidables = [rock, enemy]

fb = pygame.Surface((256, 160))

def update(player, collidables):
    proxy_x = player.x
    proxy_x += float(keys["right"] - keys["left"])
    proxy_rect = player.rect.copy()
    proxy_rect.x = proxy_x
    no_collide_x: bool = True
    for collidable in collidables:
        if (proxy_rect.colliderect(collidable.rect)):
            no_collide_x = False
            break 
    if (no_collide_x):
        player.rect = proxy_rect
        player.x = proxy_x
    proxy_y = player.y
    proxy_y += float(keys["down"] - keys["up"])
    proxy_rect = player.rect.copy()
    proxy_rect.y = proxy_y
    no_collide_y: bool = True
    for collidable in collidables:
        if (proxy_rect.colliderect(collidable.rect)):
            no_collide_y = False
            break 
    if (no_collide_y):
        player.rect = proxy_rect
        player.y = proxy_y

while True:
    # get input
    pe()

    # process input
    update(player, collidables)

    # draw to fb
    background.draw(fb)
    fb.blit(player.img, (player.rect.x, player.rect.y))
    rock.draw(fb)
    enemy.draw(fb)

    # handle screen
    screen.blit(pygame.transform.scale(fb, screen.get_size()), (0,0))
    clock.tick(60)
    pygame.display.update()
