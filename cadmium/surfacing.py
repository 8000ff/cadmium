from typing import Tuple
import numpy as np
from more_itertools import repeat_each, windowed
from itertools import cycle, repeat, chain
from .data import LinearCut
import networkx as nx

def surfacing_routine(cutting_diameter: float, area: Tuple[Tuple[float, float, float], Tuple[float, float, float]], step_over: float, feed: float = 0, speed: float = 0):
    start, stop = area
    (ax, ay, az), (bx, by, bz) = start, stop
    assert az == bz  # surfacing is meant for XY planes
    # cutting direction for each axis
    x_dir = np.sign((ax-bx))
    y_dir = np.sign((ay-by))
    cutting_radius = cutting_diameter/2
    per_pass = cutting_diameter*step_over

    # requested area width
    norm_x = (ax-bx)*x_dir
    # total x travel, extended past the stock if needed to keep the step over the same for every stroke
    total_x = np.ceil(norm_x/per_pass)*per_pass
    assert total_x >= 0

    n_passes = int(total_x/per_pass)+1
    assert float(n_passes) == (total_x/per_pass)+1.

    # list of x coordinates for the surfacing strokes
    xs = np.linspace(ax, ax - (total_x * x_dir), num=n_passes)

    # extend past the end of the stock so that surfacing only produces Y axis lines
    eay = ay + cutting_radius * y_dir
    eby = by - cutting_radius * y_dir
    total_y = (eay - eby)*y_dir
    assert total_y >= 0

    xyz = list(zip(
        repeat_each(xs, 2),
        chain.from_iterable(windowed(cycle((eay, eby)), 2)),
        repeat(az)
    ))

    cuts = [LinearCut(cut_start, cut_stop, feed, speed)
            for (cut_start, cut_stop) in windowed(xyz, 2)]

    return nx.path_graph(cuts)
