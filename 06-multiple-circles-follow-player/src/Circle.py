
#from typing import TypeAlias
#from numbers import Number
from random import randint

#Vec2: TypeAlias = tuple[Number, Number]
import pygame
Vec2 = pygame.math.Vector2

class Circle():
    def __init__(self):
        self.x = randint(0, 270)
        self.y = randint(0, 270)

    @property
    def pos(self) -> Vec2:
        return (self.x, self.y)

    @pos.setter
    def pos(self, value: Vec2) -> None:
        self.x, self.y = value
        
