import math


EBS = 0.0001


def is_equal(a, b):
    return math.fabs(a - b) < EBS


class Dot:
    x = 0
    y = 0

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __add__(self, v):
        if isinstance(v, Vector):
            return Dot(self.x + v.x, self.y + v.y)
        else:
            raise NotImplemented()


class Vector:
    x = 0
    y = 0

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __mul__(self, n):
        """Scalar multiplication or multiplication by number."""

        if isinstance(n, Vector):
            return self.x * n.x + self.y * n.y
        return Vector(self.x * n, self.y * n)

    def __xor__(self, v):
        """Pseudovector multiplication."""

        if isinstance(v, Vector):
            return self.x * v.y - self.y * v.x
        else:
            raise NotImplemented()

    def __add__(self, v):
        if isinstance(v, Vector):
            return Vector(self.x + v.x, self.y + v.y)
        else:
            raise NotImplemented()

    def __sub__(self, v):
        if isinstance(v, Vector):
            return Vector(self.x - v.x, self.y - v.y)
        else:
            raise NotImplemented()

    def is_collinear(self, v):
        return is_equal(self ^ v, 0)

    def is_codirected(self, v):
        return self.is_collinear(v) and (self * v) > 0


class Segment:
    a = None
    b = None

    def __init__(self, a, b):
        if not (isinstance(a, Dot) and isinstance(b, Dot)):
            raise Exception("Segment should be created from two Dots")
        self.a = a
        self.b = b
