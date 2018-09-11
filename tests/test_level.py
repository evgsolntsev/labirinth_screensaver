import pytest

from ..level import Level


@pytest.mark.parametrize(("x", "y"), [
	(x, y) for x in range(3) for y in range(3)
])
def test_get_cell(x, y):
	level = Level(3)
	cell = level.get_cell(x, y)
	assert cell.x == x
	assert cell.y == y


def test_neighbours():
	level = Level(3)
	cell = level.get_cell(1, 1)
	cell.up.passable = True
	cell.left.passable = True
	cell.down.passable = False
	cell.right.passable = False

	assert set(((0, 1), (1, 0))) == set(
		(c.x, c.y) for c in level.neighbours(cell))


def test_visible_changing():
	level = Level(3)
	cell = level.get_cell(1, 1)
	cell.up.passable = True
	cell.left.passable = True
	cell.down.passable = False
	cell.right.passable = False

	for c in level.neighbours(cell):
		c.visited = True

	assert len([c for c in level.cells if c.visited]) == 3
