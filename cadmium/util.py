from typing import Tuple
import numpy as np


def ouroboros(g):
    i = iter(g)
    f = next(i)
    yield f
    yield from i
    yield f


def rect(a: Tuple[float, float], b: Tuple[float, float], complete: bool):
    X, Y = np.identity(2)
    a = np.array(a)
    b = np.array(b)
    points = [a, a*Y+X*b, b, a*X+b*Y]
    if complete:
        points.append(a)
    return points

# Returns the points of a rounded of chanfered rectangle
# If a corner radius is zero, will return TWO POINTS for this corner
# The first 2 points are always the segment on the line (ax,ay,bx,ay)
# you can also provide unexpected value and see what happens


def chanfered_rect(a: Tuple[float, float], b: Tuple[float, float], complete: bool, c1: float = 0, c2: float = 0, c3: float = 0, c4: float = 0):
    from numpy import sign
    ax, ay = map(float, a)
    bx, by = map(float, b)
    sx, sy = sign(bx-ax), sign(by-ay)
    points = [
        (bx - sx * c2, ay),
        (ax + sx * c1, ay),
        (ax, ay + sy * c1),
        (ax, by - sy * c4),
        (ax + sx * c4, by),
        (bx - sx * c3, by),
        (bx, by - sy * c3),
        (bx, ay + sy * c2),
    ]
    if complete:
        points.append(points[0])
    return points


def slices(a: float, b: float, per_step: float, eps: float = .001):
    assert per_step > 0
    norm = np.linalg.norm(b-a)
    sign = np.sign(b-a)
    n, last = divmod(norm, per_step)
    if last < eps:
        yield from np.linspace(a, b, abs(int(n)), endpoint=False)
    else:
        yield from np.linspace(a, b-last*sign, abs(int(n)+1), endpoint=True)
    yield b
