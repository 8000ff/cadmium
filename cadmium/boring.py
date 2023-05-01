from typing import Tuple
import numpy as np
from itertools import zip_longest, chain
from more_itertools import windowed, flatten, intersperse
from .data import LinearCut,ArcCut
import networkx as nx

X,Y,Z = np.identity(3)

def helical_boring(cutter_diameter : float, pos : Tuple[float,float,float],depth : float, hole_diameter : float, hollow : bool = False, arc_feed : float = 0, plunge_rate : float = 0,arc_speed : float = 0, plunge_speed : float = 0):
    pos = np.array(pos)
    offset = X*(hole_diameter - cutter_diameter)/2
    start = pos - offset
    stop = start - Z*abs(depth)
    turns = np.ceil(depth / plunge_rate)
    #TODO add support for hollowing large holes
    g = nx.Graph()
    g.add_node(ArcCut(start=tuple(start),stop=tuple(stop),offset=tuple(offset),turns=turns))
    return g