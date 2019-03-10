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
LIGHT_COLOUR = (50, 50, 50)

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
    height = None
    width = None
    score = 1

    def __init__(self, x, y, h, w):
        self.x = x
        self.y = y
        self.height = math.ceil(h)
        self.width = math.ceil(w)

    def walls(self):
        return [
            wall for wall in (self.up, self.down, self.left, self.right)
            if wall is not None
        ]

    def wall_rects(self, x, y):
        result = []
        if not self.left.passable:
            result.append((x, y, self.height / 10, self.width))
        if not self.right.passable:
            result.append((
                x + math.ceil(self.height * 9 / 10), y,
                self.height / 10, self.width))
        if not self.up.passable:
            result.append((x, y, self.height, self.width / 10))
        if not self.down.passable:
            result.append((
                x, y + math.ceil(self.width * 9 / 10),
                self.height, self.width / 10))
        return result

    def wall_lines(self, x, y):
        result = []
        if not self.left.passable:
            result.append(((x, y), (x, y + self.width)))
        if not self.right.passable:
            result.append((
                (x + self.height, y),
                (x + self.height, y + self.width)))
        if not self.up.passable:
            result.append(((x, y), (x + self.height, y)))
        if not self.down.passable:
            result.append((
                (x, y + self.width),
                (x + self.height, y + self.width)))
        return result

    def draw(self, surface, x, y, img):
        scaled_img = pygame.transform.scale(img, (self.height, self.width))
        img_surface = pygame.Surface((self.height, self.width))
        img_surface.blit(scaled_img, [0, 0])
        surface.blit(img_surface, (x, y))


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
    wall_rects = None
    wall_lines = None
    player = Player()
    player_x = 0
    player_y = 0
    next_player_x = 0
    next_player_y = 0
    last = 0
    stack = None
    filter_surface = None
    cells_surface = None
    h = 0
    w = 0
    score = 0

    def __init__(self, n, height, width):
        self.n = n
        cell_height = float(height) / self.n
        cell_width = float(width) / self.n
        self.cells = list()
        self.stack = list()
        for i in range(n):
            for j in range(n):
                self.cells.append(Cell(i, j, cell_height, cell_width))

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

        self.wall_rects = list()
        self.wall_lines = list()
        for i in range(self.n):
            for j in range(self.n):
                cell = self.get_cell(i, j)
                self.wall_rects += cell.wall_rects(
                    cell_height * i, cell_width * j)
                self.wall_lines += cell.wall_lines(
                    cell_height * i, cell_width * j)

        self.h = height
        self.w = width
        self.filter_surface = pygame.surface.Surface((self.h + 1, self.w + 1))
        self.filter_surface.fill(pygame.color.Color("White"))

        self.cells_surface = pygame.surface.Surface((self.h, self.w))
        self.cells_surface.fill(pygame.color.Color("Black"))
        for i in range(self.n):
            for j in range(self.n):
                cell = self.get_cell(i, j)
                cell.draw(
                    self.cells_surface, cell_height * i, cell_width * j,
                    IMAGES[(i + j) % len(IMAGES)])

        for rect in self.wall_rects:
            pygame.draw.rect(self.cells_surface, WALL_COLOUR, rect, 0)

        #self.wall_lines = list()
        #for rect in self.wall_rects:
        #    a = [rect[0], rect[1]]
        #    b = [rect[0] + rect[2], rect[1]]
        #    c = [rect[0] + rect[2], rect[1] + rect[3]]
        #    d = [rect[0], rect[1] + rect[3]]
        #    self.wall_lines += [
        #        (a, b), (b, c), (c, d), (d, a)]

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
        surface.blit(self.cells_surface, (0, 0))
        cell_height = float(self.h) / self.n
        cell_width = float(self.w) / self.n
        radius = int(cell_height * 2)

        now = time.time()
        if now - self.last > JUMP_TIME:
            self.last = now
            self.player_x = self.next_player_x
            self.player_y = self.next_player_y
            cell = self.get_cell(self.next_player_x, self.next_player_y)
            if cell.visited is False:
                cell.visited = True
                self.score += cell.score
            self.stack.append(cell)
            for c in self.neighbours(cell):
                if not c.visited:
                    # c.visited = True
                    break
            else:
                self.stack.pop()
                c = self.stack.pop()

            self.next_player_x = c.x
            self.next_player_y = c.y

        for i in range(self.n):
            for j in range(self.n):
                c = self.get_cell(i, j)
                if not c.visited:
                    pygame.draw.circle(
                    surface, pygame.color.Color("Gold"),
                    (int(cell_height * (i + 0.5)), int(cell_width * (j + 0.5))),
                    int(cell_height / 8.0))

        player_coords = self.player.draw(
            surface,
            cell_height * (self.player_x + (self.next_player_x - self.player_x) * (now - self.last) / JUMP_TIME),
            cell_width * (self.player_y + (self.next_player_y - self.player_y) * (now - self.last) / JUMP_TIME),
            cell_height, cell_width,
        )

        def is_dot_near(dot):
            diff_x = abs(player_coords[0] - dot[0])
            diff_y = abs(player_coords[1] - dot[1])
            return max(diff_x, diff_y) <= radius + 1

        actual_lines = list(filter(
            lambda line: is_dot_near(line[0]) or is_dot_near(line[1]),
            self.wall_lines))

        circle_surface = pygame.surface.Surface((2 * radius, 2 * radius))
        white_surface = pygame.surface.Surface((2 * radius, 2 * radius))
        circle_surface.fill(LIGHT_COLOUR)
        white_surface.fill(pygame.color.Color("White"))

        out_circle_surface = pygame.surface.Surface((2 * radius, 2 * radius))
        out_circle_surface.fill(pygame.color.Color("White"))
        pygame.draw.circle(
            out_circle_surface, pygame.color.Color("Black"),
            (radius, radius), int(radius))

        def find_intersection_mul(x, y):
            target = 0
            if y == x:
                return 100000000000000
            if y > x:
                target = 2 * radius
            return 1.0 * abs(target - x) / abs(y - x)

        def find_intersection_point(a, b):
            mul = min(
                find_intersection_mul(a[0], b[0]),
                find_intersection_mul(a[1], b[1]))
            return (
                a[0] + (b[0] - a[0]) * mul,
                a[1] + (b[1] - a[1]) * mul)

        def if_in_square(a):
            return (0 <= a[0] <= radius) and (0 <= a[1] <= radius)

        def vec_mul(a, b):
            v1 = (a[0] - radius, a[1] - radius)
            v2 = (b[0] - radius, b[1] - radius)
            return v1[0] * v2[1] - v1[1] * v2[0]

        def is_between(a, b, v):
            return ((vec_mul(a, v) * vec_mul(v, b)) > 0) and (
                (vec_mul(a, v) * vec_mul(a, b)) > 0)

        tmp_surface = pygame.surface.Surface((2 * radius, 2 * radius))

        for line in actual_lines:
            tmp_surface.fill(pygame.color.Color("Black"))
            a = (
                line[0][0] - player_coords[0] + radius,
                line[0][1] - player_coords[1] + radius)
            b = (
                line[1][0] - player_coords[0] + radius,
                line[1][1] - player_coords[1] + radius)

#            if if_in_square(a) and not if_in_square(b):
#                b = find_intersection_point(a, b)
#            elif if_in_square(b) and not if_in_square(a):
#                a = find_intersection_point(b, a)

            a_intersec = find_intersection_point((radius, radius), a)
            b_intersec = find_intersection_point((radius, radius), b)
            polygon = [a, a_intersec]
            for v in (
                (0, 0), (0, 2 * radius),
                (2 * radius, 2 * radius), (2 * radius, 0)
            ):
                if is_between(a, b, v):
                    polygon.append(v)

            polygon += [b_intersec, b]

            pygame.draw.polygon(
                tmp_surface, pygame.color.Color("White"),
                polygon)
            pygame.draw.line(tmp_surface, LIGHT_COLOUR, a, b)
            circle_surface.blit(
                tmp_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MAX)

        # cut outer of circle
        circle_surface.blit(
            out_circle_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        white_surface.blit(
            circle_surface, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)

        circle_coords = (player_coords[0] - radius, player_coords[1] - radius)
        self.filter_surface.blit(
            circle_surface, circle_coords, special_flags=pygame.BLEND_RGBA_MIN)

        lightening_surface = pygame.surface.Surface((self.h + 1, self.w + 1))
        lightening_surface.fill(pygame.color.Color("Black"))
        lightening_surface.blit(
            self.filter_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        lightening_surface.blit(
            white_surface, circle_coords, special_flags=pygame.BLEND_RGBA_SUB)

        surface.blit(
            lightening_surface, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)

        return surface
