#!/usr/bin/python3

import os
import random
import sys
import time

import pygame

from level import Level


DEBUG = "XSCREENSAVER_WINDOW" not in os.environ
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

pygame.init()
screen = pygame.display.set_mode((0, 0))

if DEBUG:
	pygame.display.toggle_fullscreen()


def get_n():
	return random.randint(20, 50)


N = get_n()
level = Level(N)
height, width = pygame.display.get_surface().get_size()
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
