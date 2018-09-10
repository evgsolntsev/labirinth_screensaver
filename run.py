#!/usr/bin/python3

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
	return random.randint(20, 50)


N = get_n()
level = Level(N)
edge = min(height, width) * 9 / 10
while True:
	screen.fill(BLACK)
	try:
		level.draw(screen, (height - edge) / 2, (width - edge) / 2, edge, edge)
	except:
		level = Level(get_n())

	if DEBUG:
		events = pygame.event.get()
		if any(e for e in events if e.type == pygame.KEYDOWN):
			sys.exit(0)

	pygame.display.update()
	time.sleep(0.01)
