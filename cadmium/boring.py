from itertools import chain, zip_longest
from typing import Tuple

import numpy as np

from .data import ArcCut, LinearCut, Tool

X, Y, Z = np.identity(3)

# plunges into the piece at the center of the hole
# if tool_diameter < hole_diameter, uses an arc cut to reach the specified hole diameter


def center_counter_bore_hole(pos: Tuple[float, float, float], depth: float, hole_diameter: float, tool_diameter: float, feed: float = 0, speed: float = 0):
    assert tool_diameter <= hole_diameter <= tool_diameter*2
    start = np.array(pos)
    stop = start - Z*np.abs(depth)
    yield LinearCut(tuple(start), tuple(stop), 50, 50)
    if hole_diameter > tool_diameter:
        offset = X*(hole_diameter - tool_diameter)/2
        knot = stop - offset
        yield LinearCut(tuple(stop), tuple(knot), feed=feed, speed=speed)
        yield ArcCut(tuple(knot), tuple(knot), offset=tuple(offset), feed=feed, speed=speed)


def concentric_bore_routine(
        pos: Tuple[float, float, float],
        depth: float,
        diameter: float,
        step_over: float,
        step_down: float,
        tool: Tool,
        arc_feed: float = 0,
        plunge_feed: float = 0,
        speed: float = 0):
    
    pass
