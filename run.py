#!/usr/bin/python3

import math
import os
import random
import sys
import time

from operator import itemgetter

import pygame

from screeninfo import get_monitors
from Xlib import display

from level import Level


DEBUG = "XSCREENSAVER_WINDOW" not in os.environ
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

pygame.init()


def get_geometry(window_id):
    drawable = display.Display().create_resource_object(
        "window", window_id)
    return drawable.get_geometry()


if not DEBUG:
    geometry = get_geometry(int(os.getenv("XSCREENSAVER_WINDOW"), 16))
    screen_size = (geometry.width, geometry.height)
else:
    screen_size = min(
        ((m.width, m.height) for m in get_monitors()),
        key=itemgetter(0))

screen = pygame.display.set_mode(screen_size)

if DEBUG:
    geometry = get_geometry(pygame.display.get_wm_info()["window"])

height, width = geometry.width, geometry.height


def get_n():
    return random.randint(20, 30)


N = 30 #get_n()
edge = math.ceil(min(height, width) * 9 / 10)
level = Level(N, edge, edge)

pygame.font.init()
myfont = pygame.font.SysFont('Comic Sans MS', 32)

TARGET_SCORE = N ** 2 - 1
WAIT = 5
NEXT = 0
congrats_counter = 0
while True:
    screen.fill(BLACK)
    if level.score != TARGET_SCORE:
        congrats_counter = 0
        surface = level.draw()
        coords = (int((height - edge) / 2), int((width - edge) / 2))
        screen.blit(surface, coords)

    if level.score == TARGET_SCORE:
        if NEXT == 0:
            NEXT = time.time() + 5
        if NEXT <= time.time():
            level = Level(N, edge, edge)
            NEXT = 0
            continue
        text = "Congratulations! Next round in: {0}".format(
            int(NEXT - time.time()))
    else:
        text = "Collected: {0} / {1}.".format(level.score, TARGET_SCORE)
    textsurface = myfont.render(text, False, pygame.color.Color("Limegreen"))
    screen.blit(textsurface, (coords[0], int((width - edge) / 4)))

    if DEBUG:
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN:
                sys.exit(0)

    pygame.display.update()
    time.sleep(0.01)
