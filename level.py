import math
import os
import random
import sys
import time

import pygame


YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (125, 0, 0)
WALL_COLOUR = RED

IMAGES = [
    pygame.image.load(os.path.join(root, f))
    for root, dirs, files in os.walk("images/floors/") for f in files]
JUMP_TIME = 0.5


class Wall:
    passable = False
    cells = None

    def __init__(self):
        self.cells = list()


class Cell:
    up = None
    down = None
    left = None
    right = None
    visited = False

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def walls(self):
        return [
            wall for wall in (self.up, self.down, self.left, self.right)
            if wall is not None
        ]

    def draw(self, surface, x, y, height, width, img):
        scaled_img = pygame.transform.scale(img, (height, width))
        img_surface = pygame.Surface((height, width))
        img_surface.blit(scaled_img, [0, 0])
        surface.blit(img_surface, (x, y))
        if not self.left.passable:
            pygame.draw.rect(
                surface, WALL_COLOUR, (x, y, height / 10, width), 0)
        if not self.right.passable:
            pygame.draw.rect(
                surface, WALL_COLOUR,
                (math.ceil(x + height * 9 / 10), y, height / 10, width), 0)
        if not self.up.passable:
            pygame.draw.rect(
                surface, WALL_COLOUR, (x, y, height, width / 10), 0)
        if not self.down.passable:
            pygame.draw.rect(
                surface, WALL_COLOUR,
                (x, math.ceil(y + width * 9 / 10), height, width / 10), 0)


class Player:
    def draw(self, surface, x, y, height, width):
        circle_x, circle_y = int(x + height / 2), int(y + width / 2)
        pygame.draw.circle(
            surface, (180, 180, 0),
            (circle_x, circle_y),
            int(min(height, width) * 3 / 10))
        return circle_x, circle_y


class Level:
    cells = None
    player = Player()
    player_x = 0
    player_y = 0
    next_player_x = 0
    next_player_y = 0
    last = 0
    stack = None
    filter_surface = None
    h = 0
    w = 0

    def __init__(self, n, height, width):
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
        c.visited = True
        achiveable_cells = set([c])
        walls = c.walls()
        while walls:
            w = walls.pop(random.randrange(len(walls)))
            for c in w.cells:
                if c not in achiveable_cells:
                    achiveable_cells.add(c)
                    walls.extend(c.walls())
                    w.passable = True

        self.h = height
        self.w = width
        self.filter_surface = pygame.surface.Surface((self.h + 1, self.w + 1))
        self.filter_surface.fill(pygame.color.Color("White"))

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

    def draw(self):
        surface = pygame.surface.Surface((self.h, self.w))
        surface.fill(BLACK)
        cell_height = float(self.h) / self.n
        cell_width = float(self.w) / self.n
        for i in range(self.n):
            for j in range(self.n):
                self.get_cell(i, j).draw(
                    surface, cell_height * i, cell_width * j,
                    math.ceil(cell_height), math.ceil(cell_width),
                    IMAGES[(i + j) % len(IMAGES)])

        now = time.time()
        if now - self.last > JUMP_TIME:
            self.last = now
            self.player_x = self.next_player_x
            self.player_y = self.next_player_y
            cell = self.get_cell(self.next_player_x, self.next_player_y)
            self.stack.append(cell)
            for c in self.neighbours(cell):
                if not c.visited:
                    c.visited = True
                    break
            else:
                self.stack.pop()
                c = self.stack.pop()

            self.next_player_x = c.x
            self.next_player_y = c.y

        player_coords = self.player.draw(
            surface,
            cell_height * (self.player_x + (self.next_player_x - self.player_x) * (now - self.last) / JUMP_TIME),
            cell_width * (self.player_y + (self.next_player_y - self.player_y) * (now - self.last) / JUMP_TIME),
            cell_height, cell_width,
        )

        pygame.draw.circle(
            self.filter_surface, (50, 50, 50, 255),
            player_coords, int(cell_height * 3))

        lightening_surface = pygame.surface.Surface((self.h + 1, self.w + 1))
        lightening_surface.fill(pygame.color.Color("Black"))
        lightening_surface.blit(
            self.filter_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        pygame.draw.circle(
            lightening_surface, (0, 0, 0, 255),
            player_coords, int(cell_height * 3))


        surface.blit(
            lightening_surface, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)

        if (
            self.player_x == (self.n - 1) and
            self.player_y == (self.n - 1)
        ):
            sys.exit(0)

        return surface
