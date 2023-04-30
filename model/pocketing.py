from typing import Tuple
import numpy as np

# this is a simple/dumb pocketing routine
# will clear out material using concentric squares starting from the middle
# it compensates for cutter diameter


def rect_pocketing_routine(cutting_diameter: float, area: Tuple[Tuple[float, float, float], Tuple[float, float, float]], step_over: float, step_down: float, feed: float = 0, plunge_feed: float = 0, speed: float = 0):
    area = np.array(area)
    start, stop = area
    assert stop[-1] < start[-1]  # pocketing should go down into the stock
    # rectangular pocketing is not meant to drill holes or channels
    assert np.all(start[:1] - stop[:1])
    cutting_radius = cutting_diameter / 2
    per_pass = cutting_diameter*step_over

    # area orientation & pocket bb dimension
    dir, pocket_dim = np.sign(start-stop), np.abs(start-stop)

    # compensate for cutter radius
    reduced = np.array(((area - cutting_radius*dir)
                       [0, :2], (area + cutting_radius*dir)[1, :2]))
    # total travel
    travel = np.abs(reduced[0]-reduced[1])
    # center of the area
    center = np.mean(reduced, axis=0)
    # number of full cut in each axis, depth of the last cut
    n, last = np.divmod(travel/2, per_pass)
    corner_x = list(np.linspace(
        center[0]+per_pass, reduced[1, 0]-last[0], int(n[0])))
    if last[0] > 0:
        corner_x.append(reduced[1, 0])
    corner_y = list(np.linspace(
        center[1]+per_pass, reduced[1, 1]-last[1], int(n[1])))
    if last[1] > 0:
        corner_y.append(reduced[1, 1])

    n_full_slices, last_slice_depth = divmod(pocket_dim[-1], step_down)
    zs = [*np.linspace(start[-1], stop[-1]+last_slice_depth,
                       int(n_full_slices)), stop[-1]]

    fill = corner_x[-1] if len(corner_x) < len(corner_y) else corner_y[-1]
    from itertools import zip_longest
    corners = np.array(list(zip_longest(corner_x, corner_y, fillvalue=fill)))
    a = corners - center
    b, c, d = a*np.array((1, -1)), a*np.array((-1, -1)), a*np.array((-1, 1))
    a, b, c, d = a+center, b+center, c+center, d+center

    offset_polygons = np.array(list(zip(a, b, c, d)))
    from more_itertools import windowed, flatten, intersperse
    from itertools import chain
    from model.data import LinearCut

    def polygon(z):
        cuts = offset_polygons
        cuts = map(lambda offset: [offset[0], *offset, offset[0]], cuts)
        cuts = flatten(cuts)
        cuts = map(tuple, cuts)
        cuts = windowed(cuts, 2)
        return [LinearCut((*a, z), (*b, z), feed, speed) for a, b in cuts]

    def plunge(a, c):
        # TODO fix hop between plunge and first cut
        return [LinearCut((*center, a), (*center, c), plunge_feed, speed), None]

    cuts = intersperse(None, zs)
    cuts = windowed(chain(cuts, [None]), 3)
    cuts = [polygon(b) if b else plunge(a, c) for a, b, c in cuts]
    cuts = flatten(cuts)
    cuts = windowed(chain([None], cuts, [None]), 3)
    cuts = [b or LinearCut(a.stop, c.start, feed, speed) for a, b, c in cuts]
    cuts = list(cuts)

    import networkx as nx
    return nx.path_graph([LinearCut((*center, start[-1]), (*center, start[-1] - step_down), feed, speed), *cuts])
