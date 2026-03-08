
import pygame
from . import global_vars

class Image_Rect:

	def __init__(self, file_path: str, x: int, y: int):
		self.img: pygame.Surface = pygame.image.load(file_path)
		self.img.convert_alpha()
		self.rect = pygame.Rect(x, y, self.img.get_width(), self.img.get_height())
		self.vel: pygame.math.Vector2 = pygame.math.Vector2(0, 0)

	@property
	def x(self) -> int:
		return self.rect.x

	@x.setter
	def x(self, value: int):
		self.rect.x = value

	@property
	def y(self) -> int:
		return self.rect.y

	@y.setter
	def y(self, value: int):
		self.rect.y = value

	@property
	def pos(self) -> tuple[int, int]:
		return (self.x, self.y)

	@pos.setter
	def pos(self, value: tuple[int, int]):
		self.x, self.y = value

	def draw(self, surface=None):
		if surface is None:
			surface = global_vars.screen
		surface.blit(self.img, self.pos)

