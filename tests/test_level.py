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

	assert set(((0, 1), (1, 0))) == set(
		(c.x, c.y) for c in level.neighbours(cell))


def test_visible_changing():
	level = Level(3)
	cell = level.get_cell(1, 1)
	cell.up.passable = True
	cell.left.passable = True

	for c in level.neighbours(cell):
		c.visible = True

	assert len([c for c in level.cells if c.visible]) == 2


def test_passable_changing():
	level = Level(3)
	cell = level.get_cell(1, 1)
	
	assert level.get_cell(0, 1).right.passable == False
	assert level.get_cell(2, 1).left.passable == False
	assert level.get_cell(1, 2).up.passable == False
	assert level.get_cell(1, 0).down.passable == False

	cell.up.passable = True
	cell.left.passable = True

	assert level.get_cell(0, 1).right.passable == True
	assert level.get_cell(2, 1).left.passable == False
	assert level.get_cell(1, 2).up.passable == False
	assert level.get_cell(1, 0).down.passable == True

	cell.down.passable = True
	cell.right.passable = True

	assert level.get_cell(0, 1).right.passable == True
	assert level.get_cell(2, 1).left.passable == True
	assert level.get_cell(1, 2).up.passable == True
	assert level.get_cell(1, 0).down.passable == True
