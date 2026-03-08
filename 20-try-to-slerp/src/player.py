import pygame

class Player:
    def __init__(self, color, x, y, width, height):
        self.color: tuple[int, int, int] = color
        self.x: float = x
        self.y: float = y
        self.width: int = width
        self.height: int = height
    @property
    def pos(self) -> pygame.math.Vector2:
        return pygame.math.Vector2(self.x, self.y)
    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.width, self.height)
