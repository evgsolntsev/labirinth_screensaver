import math
import random
import sys
import time

import pygame


YELLOW = (125, 125, 0)
GREEN = (0, 125, 0)
BLUE = (0, 0, 125)
BLACK = (0, 0, 0)
RED = (125, 0, 0)
GREY = (80, 80, 80)

COLOURS = [YELLOW, GREEN, BLUE]
JUMP_TIME = 0.5


class Wall:
	passable = False
	cells = None

	def __init__(self):
		self.cells = list()


class Cell:
	visible = False
	up = None
	down = None
	left = None
	right = None
	
	def __init__(self, x, y):
		self.x = x
		self.y = y

	def walls(self):
		return [
			wall for wall in (self.up, self.down, self.left, self.right)
			if wall is not None
		]

	def draw(self, surface, x, y, height, width, colour=None):
		if not self.visible:
			return

		pygame.draw.rect(
			surface, colour or YELLOW, (x, y, height, width), 0)
		if not self.left.passable:
			pygame.draw.rect(
				surface, GREY, (x, y, height / 10, width), 0)
		if not self.right.passable:
			pygame.draw.rect(
				surface, GREY,
				(math.ceil(x + height * 9 / 10), y, height / 10, width), 0)
		if not self.up.passable:
			pygame.draw.rect(
				surface, GREY, (x, y, height, width / 10), 0)
		if not self.down.passable:
			pygame.draw.rect(
				surface, GREY,
				(x, math.ceil(y + width * 9 / 10), height, width / 10), 0)


class Player:
	def draw(self, surface, x, y, height, width):
		pygame.draw.circle(
			surface, (180, 180, 0),
			(int(x + height / 2), int(y + width / 2)),
			int(min(height, width) * 3 / 10))


class Level:
	cells = None
	player = Player()
	player_x = 0
	player_y = 0
	next_player_x = 0
	next_player_y = 0
	last = 0
	stack = None

	def __init__(self, n):
		self.n = n
		self.cells = list()
		self.stack = list()
		for i in range(n):
			for j in range(n):
				self.cells.append(Cell(i, j))

		for i in range(n + 1):
			for j in range(n):
				w = Wall()
				if i > 0:
					c = self.get_cell(i - 1, j)
					c.right = w
					w.cells.append(c)
				if i < n:
					c = self.get_cell(i, j)
					c.left = w
					w.cells.append(c)

		for i in range(n):
			for j in range(n + 1):
				w = Wall()
				if j > 0:
					c = self.get_cell(i, j - 1)
					c.down = w
					w.cells.append(c)
				if j < n:
					c = self.get_cell(i, j)
					c.up = w
					w.cells.append(c)

		c = self.get_cell(0, 0)
		c.visible = True
		achiveable_cells = set([c])
		walls = c.walls()
		while walls:
			w = walls.pop(random.randrange(len(walls)))
			for c in w.cells:
				if c not in achiveable_cells:
					achiveable_cells.add(c)
					walls.extend(c.walls())
					w.passable = True
		

	def get_cell(self, x, y):
		return self.cells[x * self.n + y]

	def neighbours(self, cell):
		result = []
		if cell.x > 0 and cell.left.passable:
			result.append(self.get_cell(cell.x - 1, cell.y))
		if cell.x < self.n - 1 and cell.right.passable:
			result.append(self.get_cell(cell.x + 1, cell.y))
		if cell.y > 0 and cell.up.passable:
			result.append(self.get_cell(cell.x, cell.y - 1))
		if cell.y < self.n - 1 and cell.down.passable:
			result.append(self.get_cell(cell.x, cell.y + 1))

		return result

	def draw(self, surface, x, y, height, width):
		cell_height = float(height) / self.n
		cell_width = float(width) / self.n
		for i in range(self.n):
			for j in range(self.n):
				self.get_cell(i, j).draw(
					surface, x + cell_height * i, y + cell_width * j,
					math.ceil(cell_height), math.ceil(cell_width),
					colour=COLOURS[(i + j) % len(COLOURS)])

		now = time.time()
		if now - self.last > JUMP_TIME:
			self.last = now
			self.player_x = self.next_player_x
			self.player_y = self.next_player_y
			cell = self.get_cell(self.next_player_x, self.next_player_y)
			self.stack.append(cell)
			for c in self.neighbours(cell):
				if not c.visible:
					c.visible = True
					break
			else:
				self.stack.pop()
				c = self.stack.pop()

			self.next_player_x = c.x
			self.next_player_y = c.y

		self.player.draw(
			surface,
			x + cell_height * (self.player_x + (self.next_player_x - self.player_x) * (now - self.last) / JUMP_TIME),
			y + cell_width * (self.player_y + (self.next_player_y - self.player_y) * (now - self.last) / JUMP_TIME),
			cell_height, cell_width,
		)

		if (
			self.player_x == (self.n - 1) and
			self.player_y == (self.n - 1)
		):
			sys.exit(0)

