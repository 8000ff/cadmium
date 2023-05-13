from typing import Tuple
import numpy as np

def ouroboros(g):
    i = iter(g)
    f = next(i)
    yield f
    yield from i
    yield f

def rect(a: Tuple[float, float], b: Tuple[float, float],complete : bool):
    X,Y = np.identity(2)
    O = np.zeros(3)
    a = np.array(a)
    b = np.array(b)
    points = [a,a*Y+X*b,b,a*X+b*Y]
    if complete:
        points.append(a)
    return points

def slices(a : float, b : float, per_step : float, eps : float = .001):
    assert per_step > 0
    norm = np.linalg.norm(b-a)
    sign = np.sign(b-a)
    n, last = divmod(norm,per_step)
    if last < eps:
        yield from np.linspace(a,b,abs(int(n)),endpoint=False)
    else:
        yield from np.linspace(a,b-last*sign,abs(int(n)+1),endpoint=True)
    yield b