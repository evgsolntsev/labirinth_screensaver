import math
import os
import random
import sys
import time

import pygame

from geometry import Segment, Dot, Vector


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
    height = None
    width = None

    def __init__(self, x, y, h=10, w=10):
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

    def draw(self, surface, x, y, img):
        scaled_img = pygame.transform.scale(img, (self.height, self.width))
        img_surface = pygame.Surface((self.height, self.width))
        img_surface.blit(scaled_img, [0, 0])
        surface.blit(img_surface, (x, y))
        for rect in self.wall_rects(x, y):
            pygame.draw.rect(
                surface, WALL_COLOUR, rect, 0)


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
    cells_surface = None
    h = 0
    w = 0
    vision_radius = 0

    def __init__(self, n, height=100, width=100):
        self.n = n
        cell_height = float(height) / self.n
        cell_width = float(width) / self.n
        self.vision_radius = int(cell_height * 2)
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

        self.h = height
        self.w = width
        self.filter_surface = pygame.surface.Surface((self.h + 1, self.w + 1))
        self.filter_surface.fill(pygame.color.Color("White"))

        self.cells_surface = pygame.surface.Surface((self.h, self.w))
        self.cells_surface.fill(pygame.color.Color("Black"))
        for i in range(self.n):
            for j in range(self.n):
                self.get_cell(i, j).draw(
                    self.cells_surface, cell_height * i, cell_width * j,
                    IMAGES[(i + j) % len(IMAGES)])

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

        walls_for_shadows = []
        for i in range(-2, 3):
            for j in range(-2, 3):
                cell_x, cell_y = self.player_x + i, self.player_y + j
                if (
                    (cell_x > -1) and (cell_x < self.n) and
                    (cell_y > -1) and (cell_y < self.n)
                ):
                    walls_for_shadows.extend(
                        self.get_cell(cell_x, cell_y).wall_rects(
                            cell_height * cell_x, cell_width * cell_y))

        lines_for_shadows = [
            ((0, 0), (self.h, 0)),
            ((self.h, 0), (self.h, self.w)),
            ((self.h, self.w), (0, self.w)),
            ((0, self.w), (0, 0))
        ]
        for w in walls_for_shadows:
            lines_for_shadows.extend([
                [(w[0], w[1]), (w[0] + w[2], w[1])],
                [(w[0] + w[2], w[1]), (w[0] + w[2], w[1] + w[3])],
                [(w[0] + w[2], w[1] + w[3]), (w[0], w[1] + w[3])],
                [(w[0], w[1] + w[3]), (w[0], w[1])]
            ])

        player_dot = Dot(*player_coords)
        vertexes = []
        for i, l in enumerate(lines_for_shadows):
            phi1 = math.atan2(l[0][0] - player_dot.x, l[0][1] - player_dot.y)
            phi2 = math.atan2(l[1][0] - player_dot.x, l[1][1] - player_dot.y)
            v1 = Vector(player_dot, Dot(*l[0]))
            v2 = Vector(player_dot, Dot(*l[1]))
            vertexes.extend([
                (phi1, i, v1 ^ v2 < 0, Dot(*l[0])),
                (phi2, i, v1 ^ v2 > 0, Dot(*l[1])),
            ])
        vertexes.sort(key=lambda v: v[0])

        adding_surface = pygame.surface.Surface((self.h + 1, self.w + 1))
        adding_surface.fill(pygame.color.Color("White"))
        out_surface = pygame.surface.Surface((self.h + 1, self.w + 1))
        out_surface.fill(pygame.color.Color("White"))
        pygame.draw.circle(
            out_surface, pygame.color.Color("Black"),
            player_coords, self.vision_radius)

        # ray tracing
        walls = []
        closest_wall = Segment(Dot(0, 0), Dot(0, 0))
        closest_wall_number = -1
        last_triangle_vertex = None
        for angle, line_number, is_start, dot in vertexes:
            current_v = Vector(player_dot, dot)
            l = lines_for_shadows[line_number]
            segment = Segment(
                Dot(l[0][0], l[0][1]), Dot(l[1][0], l[1][1]))
            old_distance = None
            if is_start:
                walls.append(segment)
                old_distance = closest_wall.distance(player_dot, current_v)
                new_distance = segment.distance(player_dot, current_v)
                if closest_wall_number == -1:
                    closest_wall = segment
                    closest_wall_number = line_number
                elif new_distance < old_distance:
                    closest_wall = segment
                    closest_wall_number = line_number
            else:
                if closest_wall_number == -1:
                    vertexes.append((angle, line_number, is_start, dot))
                    continue

                for i, w in enumerate(walls):
                    if w == segment:
                        walls.pop(i)
                        if i == closest_wall_number:
                            old_distance = segment.distance(player_dot, current_v)
                            distance = 100000
                            for j, cw in enumerate(walls):
                                tmp = cw.distance(player_dot, current_v)
                                if tmp < distance:
                                    distance = tmp
                                    closest_wall_number = j
                                    closest_wall = cw
                        break
                else:
                    vertexes.append((angle, line_number, is_start, dot))

                if not old_distance:
                    continue

                new_triangle_dot = player_dot + current_v * old_distance
                new_triangle_vertex = [new_triangle_dot.x, new_triangle_dot.y]
                if last_triangle_vertex is not None:
                    pygame.draw.polygon(
                        adding_surface, (50, 50, 50, 255), [
                            player_coords, last_triangle_vertex,
                            new_triangle_vertex])
                last_triangle_vertex = new_triangle_vertex

        # sys.exit(0)
        adding_surface.blit(
            out_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MAX)
        self.filter_surface.blit(
            adding_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

        lightening_surface = pygame.surface.Surface((self.h + 1, self.w + 1))
        lightening_surface.fill(pygame.color.Color("Black"))
        lightening_surface.blit(
            self.filter_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        surface.blit(
            lightening_surface, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)

        if (
            self.player_x == (self.n - 1) and
            self.player_y == (self.n - 1)
        ):
            sys.exit(0)

        return surface
