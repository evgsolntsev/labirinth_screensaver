import pytest

from ..geometry import Dot, Vector, Segment


def test_dot():
    a = Dot(1, 2)
    assert a.x == 1
    assert a.y == 2

    b = Dot()
    assert b.x == 0
    assert b.y == 0


def test_dot_add():
    a = Dot(1, 1)
    v = Vector(1, 2)
    b = a + v
    assert isinstance(b, Dot)
    assert b.x == 2
    assert b.y == 3


def test_vector():
    v = Vector()
    assert v.x == 0
    assert v.y == 0

    u = Vector(1, 2)
    assert u.x == 1
    assert u.y == 2


def test_vector_mul():
    v = Vector(0, 5)
    u = v * 5
    assert u.x == 0
    assert u.y == 25


def test_vector_add():
    v = Vector(1, 3)
    u = Vector(2, 4)
    q = v + u
    assert q.x == 3
    assert q.y == 7


def test_vector_sub():
    v = Vector(1, 2)
    u = Vector(3, 5)
    q = v - u
    assert q.x == -2
    assert q.y == -3


@pytest.mark.parametrize(("v", "u", "result"), [
    (Vector(1, 2), Vector(1, 3), False),
    (Vector(1.5, 2), Vector(3, 4), True),
    (Vector(1, 2), Vector(-1, -2), True),
    (Vector(0, 1), Vector(1, 0), False),
    (Vector(0, 1), Vector(0, 2), True),
    (Vector(0, 1), Vector(0, -1), True),
    (Vector(1, 0), Vector(2, 0), True),
    (Vector(1, 0), Vector(-1, 0), True),
])
def test_vector_is_collinear(v, u, result):
    assert v.is_collinear(u) == result
    assert u.is_collinear(v) == result


@pytest.mark.parametrize(("v", "u", "result"), [
    (Vector(1, 2), Vector(1, 3), False),
    (Vector(1.5, 2), Vector(3, 4), True),
    (Vector(1, 2), Vector(-1, -2), False),
    (Vector(0, 1), Vector(1, 0), False),
    (Vector(0, 1), Vector(0, 2), True),
    (Vector(0, 1), Vector(0, -1), False),
    (Vector(1, 0), Vector(2, 0), True),
    (Vector(1, 0), Vector(-1, 0), False),
])
def test_vector_is_codirected(v, u, result):
    assert v.is_codirected(u) == result
    assert u.is_codirected(v) == result


def test_segment():
    a = Dot(1, 2)
    b = Dot(3, 4)
    s = Segment(a, b)
    assert s.a == a
    assert s.b == b


@pytest.mark.parametrize(("a", "b", "c", "result"), [
    ((0, 0), (2, 2), (1, 1), True),
    ((0, 0), (1, 0), (1, 1), False),
    ((0, 0), (2, 2), (2, 2), True),
    ((0, 0), (2, 2), (0, 0), True),
    ((0, 0), (2, 2), (-1, -1), False),
])
def test_segment_contains(a, b, c, result):
    ab = Segment(Dot(*a), Dot(*b))
    c = Dot(*c)
    assert (c in ab) == result
