
import pygame

Vec2 = pygame.math.Vector2

class Circle:
  def __init__(self, x, y, r, color):
   self.x = x
   self.y = y
   self.r = r
   self.color = color
   self.vel = Vec2(0,0)

  @property
  def pos(self) -> Vec2:
    return Vec2(self.x, self.y)

  @pos.setter
  def pos(self, value) -> None:
    self.x, self.y = value

  def draw(self, surf):
    pygame.draw.circle(surf, self.color, (self.x, self.y), self.r)

