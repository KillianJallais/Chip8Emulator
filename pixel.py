import pygame

class Pixel:
	WIDTH = 12
	BLACK = (0, 0, 0)
	WHITE = (255, 255, 255)

	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.color = self.BLACK
		self.rect = pygame.Rect(self.WIDTH * self.x, self.WIDTH * self.y, self.WIDTH, self.WIDTH)

	def draw(self, screen) -> None:
		pygame.draw.rect(screen, self.color, self.rect)

	def setColor(self, color: tuple) -> None:
		self.color = color

	def __repr__(self) -> str:
		return f"Pixel({self.x}, {self.y})"