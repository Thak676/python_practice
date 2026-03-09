
import pygame
import global_vars
keys = global_vars.keys
from funcs import init, pe
from Image_Rect import Image_Rect
IR = Image_Rect

screen, clock = init(1760, 1024)

class Player:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

player = Player(10.0, 10.0)
m_img: pygame.Surface = pygame.image.load("data/m_03_02.png")
background = IR("data/background.png", 0, 0)
rock = IR("data/rock 01.png", 64, 64)

fb = pygame.Surface((256, 160))

while True:
    # get input
    pe()

    # process input
    player.x += float(keys["right"] - keys["left"])
    player.y += float(keys["down"] - keys["up"])

    # draw to fb
    background.draw(fb)
    fb.blit(m_img, (player.x, player.y))
    rock.draw(fb)

    # handle screen
    screen.blit(pygame.transform.scale(fb, screen.get_size()), (0,0))
    clock.tick(60)
    pygame.display.update()
