
import pygame
Vec2 = pygame.math.Vector2

class Circle():
    def __init__(self, x, y, r, color):
        self.x = x
        self.y = y
        self.r = r
        self.color = color

    def draw(self, surface) -> pygame.Rect:
        return pygame.draw.circle(surface, self.color, (self.x, self.y), self.r)

    # pos getter and setter
    @property
    def pos(self) -> Vec2:
        return (self.x, self.y)
    @pos.setter
    def pos(self, value: Vec2) -> None:
        self.x, self.y = value
        
