import numpy as np
import pygame
from pixel import Pixel
import random

class Chip8:
	BLACK = (0, 0, 0)
	WHITE = (255, 255, 255)

	def __init__(self):
		self.memoire = np.zeros(4096, dtype=np.uint8) #initialise une liste de 4096 0 de type uint8 (unsigned integer sur 8 bit)
		self.pc = 0x0200 #pointeur de la mémoire, commence à 512

		self.V = np.zeros(16, dtype=np.uint8)
		self.gameTimer = 0
		self.soundTimer = 0

		self.I = 0

		self.clavier = np.zeros(16, dtype=np.uint8)

		self.stack = np.zeros(16, dtype=np.uint16)
		self.sp = 0

		self.keys = {}

		self.pixels = np.zeros((64, 32), dtype=Pixel)
		self.initPixels()
		self.initNumbers()
		self.mapKeys()
		self.nb_tours = 0

	def loadGame(self, path: str) -> None:
		with open(path, "rb") as file:
			data = list(file.read())

		for i in range(len(data)):
			self.memoire[i + 0x0200] = data[i]

	def initPixels(self) -> None:
		for x in range(64):
			for y in range(32):
				self.pixels[x][y] = Pixel(x, y)

	def clearScreen(self) -> None:
		for x in range(64):
			for y in range(32):
				self.pixels[x][y].setColor((0, 0, 0))

	def updateScreen(self, screen) -> None:
		for x in range(64):
			for y in range(32):
				self.pixels[x][y].draw(screen)

		pygame.display.update()

	def updateTimers(self) -> None:
		if self.gameTimer > 0:
			self.gameTimer -= 1

		if self.soundTimer > 0:
			self.soundTimer -= 1

	def initNumbers(self) -> None:
		self.memoire[0]=0xF0; self.memoire[1]=0x90; self.memoire[2]=0x90; self.memoire[3]=0x90;  self.memoire[4]=0xF0;  # O 
		self.memoire[5]=0x20; self.memoire[6]=0x60; self.memoire[7]=0x20; self.memoire[8]=0x20; self.memoire[9]=0x70;  # 1 
		self.memoire[10]=0xF0; self.memoire[11]=0x10; self.memoire[12]=0xF0; self.memoire[13]=0x80;  self.memoire[14]=0xF0;  # 2 
		self.memoire[15]=0xF0; self.memoire[16]=0x10; self.memoire[17]=0xF0; self.memoire[18]=0x10; self.memoire[19]=0xF0;  # 3 
		self.memoire[20]=0x90; self.memoire[21]=0x90; self.memoire[22]=0xF0; self.memoire[23]=0x10; self.memoire[24]=0x10;  # 4 
		self.memoire[25]=0xF0; self.memoire[26]=0x80; self.memoire[27]=0xF0; self.memoire[28]=0x10; self.memoire[29]=0xF0;  # 5 
		self.memoire[30]=0xF0; self.memoire[31]=0x80; self.memoire[32]=0xF0; self.memoire[33]=0x90; self.memoire[34]=0xF0;  # 6 
		self.memoire[35]=0xF0; self.memoire[36]=0x10; self.memoire[37]=0x20; self.memoire[38]=0x40; self.memoire[39]=0x40;  # 7 
		self.memoire[40]=0xF0; self.memoire[41]=0x90; self.memoire[42]=0xF0; self.memoire[43]=0x90; self.memoire[44]=0xF0;  # 8 
		self.memoire[45]=0xF0; self.memoire[46]=0x90; self.memoire[47]=0xF0; self.memoire[48]=0x10; self.memoire[49]=0xF0;  # 9 
		self.memoire[50]=0xF0; self.memoire[51]=0x90; self.memoire[52]=0xF0; self.memoire[53]=0x90; self.memoire[54]=0x90;  # A 
		self.memoire[55]=0xE0; self.memoire[56]=0x90; self.memoire[57]=0xE0; self.memoire[58]=0x90; self.memoire[59]=0xE0;  # B 
		self.memoire[60]=0xF0; self.memoire[61]=0x80; self.memoire[62]=0x80; self.memoire[63]=0x80; self.memoire[64]=0xF0;  # C 
		self.memoire[65]=0xE0; self.memoire[66]=0x90; self.memoire[67]=0x90; self.memoire[68]=0x90; self.memoire[69]=0xE0;  # D 
		self.memoire[70]=0xF0; self.memoire[71]=0x80; self.memoire[72]=0xF0; self.memoire[73]=0x80; self.memoire[74]=0xF0;  # E 
		self.memoire[75]=0xF0; self.memoire[76]=0x80; self.memoire[77]=0xF0; self.memoire[78]=0x80; self.memoire[79]=0x80;  # F 

	def getOpcode(self) -> tuple:
		opcode = self.memoire[self.pc] << 8 | self.memoire[self.pc + 1]

		b4 = (opcode & 0xF000) >> 12
		b3 = (opcode & 0x0F00) >> 8
		b2 = (opcode & 0x00F0) >> 4
		b1 = (opcode & 0x000F)

		return (b4, b3, b2, b1)

	def setPc(self, val: int) -> None:
		if val < 0:
			raise ValueError(f"Le pointeur self.pc (= {self.pc}) ne peut pas être inférieur à 0")
		else:
			self.pc = val

	def setSp(self, val: int) -> None:
		if val < 0 or val > 15:
			raise ValueError(f"Le pointeur self.sp (= {self.sp}) n'est pas valide.'")
		else:
			self.sp = val

	def drawSprite(self, b3: int, b2: int, b1: int) -> None:
		self.V[0xF] = 0

		for i in range(b1):
			byte = self.memoire[self.I + i]

			y = (self.V[b2] + i) % 32

			for j in range(8):
				x = (self.V[b3] + j) % 64
				if (byte & (0x1 << (8 - 1 - j))) != 0:
					if self.pixels[x][y].color == self.WHITE:
						self.pixels[x][y].setColor(self.BLACK)
						self.V[0xF] = 1
					else:
						self.pixels[x][y].setColor(self.WHITE)

	def pause(self) -> int:
		pause = True

		while pause:
			for event in pygame.event.get():
				if event.type == pygame.KEYDOWN:
					pause = False

		return event

	def mapKeys(self):
		self.keys[0] = pygame.K_a
		self.keys[1] = pygame.K_e
		self.keys[2] = pygame.K_z
		self.keys[3] = pygame.K_r
		self.keys[4] = pygame.K_q
		self.keys[5] = pygame.K_t
		self.keys[6] = pygame.K_d
		self.keys[7] = pygame.K_f
		self.keys[8] = pygame.K_s
		self.keys[9] = pygame.K_g
		self.keys[10] = pygame.K_w
		self.keys[11] = pygame.K_x
		self.keys[12] = pygame.K_c
		self.keys[13] = pygame.K_v
		self.keys[14] = pygame.K_b
		self.keys[15] = pygame.K_y

	def getKeyboardState(self):
		keyboard = pygame.key.get_pressed()
		for i in self.keys.items():
			if keyboard[i[1]]:
				self.clavier[i[0]] = 1
			else:
				self.clavier[i[0]] = 0



	############################################################## instructions ##############################################################

	def executeOpcode(self) -> None:
		b4, b3, b2, b1 = self.getOpcode()

		if b4 == 0 and b3 == 0 and b2 == 14 and b1 == 0:
			self.clearScreen()

		elif b4 == 0 and b3 == 0 and b2 == 14 and b1 == 14:
			self.setPc(self.stack[self.sp])
			self.setSp(self.sp - 1)

		elif b4 == 1:
			pc = (b3 << 8) | (b2 << 4) | b1
			pc -= 2
			self.setPc(pc)

		elif b4 == 2:
			self.setSp(self.sp + 1)
			self.stack[self.sp] = self.pc

			pc = (b3 << 8) | (b2 << 4) | b1
			pc -= 2
			self.setPc(pc)

		elif b4 == 3:
			if self.nb_tours == 78:
				print("registre : ", self.V[b3])
			if self.V[b3] == ((b2 << 4) | b1):
				self.setPc(self.pc + 2)

		elif b4 == 4:
			if self.V[b3] != ((b2 << 4) | b1):
				self.setPc(self.pc + 2)

		elif b4 == 5 and b1 == 0:
			if self.V[b3] == self.V[b2]:
				self.setPc(self.pc + 2)

		elif b4 == 6:
			self.V[b3] = (b2 << 4) | b1

		elif b4 == 7:
			self.V[b3] += (b2 << 4) | b1

		elif b4 == 8 and b1 == 0:
			self.V[b3] = self.V[b2]

		elif b4 == 8 and b1 == 1:
			self.V[b3] = self.V[b3] | self.V[b2]

		elif b4 == 8 and b1 == 2:
			self.V[b3] = self.V[b3] & self.V[b2]

		elif b4 == 8 and b1 == 3:
			self.V[b3] = self.V[b3] ^ self.V[b2]

		elif b4 == 8 and b1 == 4:
			temp = self.V[b3] + self.V[b2]
			if temp > 511:
				raise ValueError(f"Dépassement de bit, temp = {temp}")
			elif temp > 255:
				self.V[0xF] = 1
				temp = temp >> 1
			else:
				self.V[0xF] = 0

			self.V[b3] = temp

		elif b4 == 8 and b1 == 5:
			self.V[0xF] = 0

			if self.V[b3] > self.V[b2]:
				self.V[0xF] = 1

			self.V[b3] = self.V[b3] - self.V[b2]

		elif b4 == 8 and b1 == 6:
			self.V[0xF] = self.V[b3] & 1
			self.V[b3] = self.V[b3] >> 1

		elif b4 == 8 and b1 == 7:
			if self.V[b2] > self.V[b3]:
				self.V[0xF] = 1
			else:
				self.V[0xF] = 0

			self.V[b3] = self.V[b2] - self.V[b3]

		elif b4 == 8 and b1 == 14:
			self.V[0xF] = self.V[b3] >> 7
			self.V[b3] = self.V[b3] << 1

		elif b4 == 9 and b1 == 0:
			if self.V[b3] != self.V[b2]:
				self.setPc(self.pc + 2)

		elif b4 == 10:
			self.I = (b3 << 8) | (b2 << 4) | b1

		elif b4 == 11:
			pc = ((b3 << 8) | (b2 << 4) | b1) + self.V[0]
			pc -= 2
			self.setPc(pc)

		elif b4 == 12:
			kk = (b2 << 4) | b1
			self.V[b3] = random.randint(0, 255) & kk

		elif b4 == 13:
			self.drawSprite(b3, b2, b1)

		elif b4 == 14 and b2 == 9 and b1 == 14:
			if self.clavier[self.V[b3]] == 1:
				self.setPc(self.pc + 2)

		elif b4 == 14 and b2 == 10 and b1 == 1:
			if self.clavier[self.V[b3]] == 0:
				self.setPc(self.pc + 2)

		elif b4 == 15 and b2 == 0 and b1 == 7:
			self.V[b3] = self.gameTimer

		elif b4 == 15 and b2 == 0 and b1 == 10:
			self.pause()

		elif b4 == 15 and b2 == 1 and b1 == 5:
			self.gameTimer = self.V[b3]

		elif b4 == 15 and b2 == 1 and b1 == 8:
			self.soundTimer = self.V[b3]

		elif b4 == 15 and b2 == 1 and b1 == 14:
			if self.I + self.V[b3] > 0xFFF:
				self.V[0xF] = 1
			else:
				self.V[0xF] = 0

			self.I += self.V[b3]

		elif b4 == 15 and b2 == 2 and b1 == 9:
			self.I = self.V[b3] * 5

		elif b4 == 15 and b2 == 3 and b1 == 3:
			self.memoire[self.I] = int(self.V[b3]/100)
			self.memoire[self.I + 1] = int(self.V[b3]/10) % 10
			self.memoire[self.I + 2] = self.V[b3] % 10

		elif b4 == 15 and b2 == 5 and b1 == 5:
			for i in range(b3 + 1):
				self.memoire[self.I + i] = self.V[i]

		elif b4 == 15 and b2 == 6 and b1 == 5:
			for i in range(b3 + 1):
				self.V[i] = self.memoire[self.I + i]

		else:
			raise Exception("C'est la merde")

		self.setPc(self.pc + 2)
		self.nb_tours += 1



def main():
	chip8 = Chip8()
	chip8.loadGame("Blitz.ch8")

if __name__ == "__main__":
	main()