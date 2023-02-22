import pygame
from chip8 import Chip8
from pixel import Pixel

GAME = ""

def main():
	pygame.init()

	WIDTH = 64 * Pixel.WIDTH
	HEIGTH = 32 * Pixel.WIDTH

	running = True
	clock = pygame.time.Clock()
	screen = pygame.display.set_mode((WIDTH, HEIGTH))

	chip8 = Chip8()
	chip8.loadGame(GAME)

	while running:
		clock.tick(30)
		
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False

		for i in range(4):
			chip8.getKeyboardState()
			chip8.executeOpcode()
			chip8.updateTimers()

		chip8.updateScreen(screen)

	pygame.quit()


if __name__ == "__main__":
	main()
