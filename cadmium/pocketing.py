from typing import Tuple
import numpy as np
from itertools import zip_longest, chain
from more_itertools import windowed, flatten, intersperse
from .data import LinearCut
from .util import slices
import networkx as nx

def rect_pocketing_routine(cutting_diameter: float, area: Tuple[Tuple[float, float, float], Tuple[float, float, float]], step_over: float, step_down: float, feed: float = 0, plunge_feed: float = 0, speed: float = 0):
    area = np.array(area,dtype=np.float64)
    start, stop = area
    assert stop[-1] < start[-1]  # pocketing should go down into the stock
    # rectangular pocketing is not meant to drill holes or channels
    assert np.all(start[:1] - stop[:1])
    cutting_radius = cutting_diameter / 2
    per_pass = cutting_diameter*step_over
    center = np.mean(area[:,:2],axis=0)
    # Compute the initial slit orientation and size for rectangle pockets
    ss = start[:2] - stop[:2]
    orient = np.sign(ss)
    slit = (ss - orient*np.min(np.abs(ss))*np.ones(ss.shape))
    slitA,slitB = center + slit/2, center - slit/2

    from .util import rect
    for (prez,z) in windowed(slices(start[2],stop[2],step_down),2):
        # Initial plunge
        yield LinearCut((*slitA,prez),(*slitB,z),plunge_feed,speed)
        # Initial slit
        yield LinearCut((*slitA,z),(*slitB,z),feed,speed)
        for (pres,side) in windowed(slices(0,np.min(np.abs(ss))/2 - cutting_radius,per_pass),2):
            pres_points = rect((slitA+pres*orient),(slitB-pres*orient),complete=True)
            side_points = rect((slitA+side*orient),(slitB-side*orient),complete=True)
            # Cut from one rectangle to the next
            yield LinearCut((*pres_points[-1],z),(*side_points[0],z),feed,speed)
            for (a,b) in windowed(side_points,2):
                # Rectangle side
                yield LinearCut((*a,z),(*b,z),feed,speed)
