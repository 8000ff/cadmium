from dataclasses import dataclass, field
from typing import Tuple, Callable, List
import networkx as nx
import numpy as np
from pygcode import GCodeSpindleSpeed, GCode, GCodeFeedRate, GCodeLinearMove, GCodeStartSpindleCW, GCodeStartSpindleCCW, GCodeArcMoveCW, GCodeArcMoveCCW


@dataclass(unsafe_hash=True)
class WorkHolding:
    pass  # TODO define the work holding engine


@dataclass(unsafe_hash=True)
class Setup:
    translation: Tuple[float, float, float] = (0, 0, 0)
    rotation: Tuple[float, float, float] = (0, 0, 0)
    workHolding: WorkHolding = None


@dataclass(unsafe_hash=True)
class Tool:
    diameter: float
    end_diameter: float
    edge_height: float = 0  # zero is for cylindrical tools
    edge_radius: float = np.Infinity  # accepts negative values
    radius: float = field(init=False)

    def __post_init__(self):
        self.radius = self.diameter/2.


@dataclass(unsafe_hash=True)
class Operation:
    # Cuts are stored in a tree, branches starting from a node can always be reordered, the tree should be read using Depth Search First pre-order
    # Edges can be labeled with list of positions (Tuple[float,float,float]) to specify the path to take between two cuts, if no label is present the solver will provide a default path
    cuts: nx.Graph
    tool: Tool


@dataclass(unsafe_hash=True)
class LinearCut:
    start: Tuple[float, float, float]
    stop: Tuple[float, float, float]  # XYZ params
    feed: float = 0  # mm/s # TODO look into the use of rev/mm
    speed: float = 0  # rpm
    spindle_cw: bool = True

    def gcode(self, include_start=False, include_stop=True, include_feed=False, include_speed=False, include_spindle_start=False):
        ax, ay, az = self.start
        bx, by, bz = self.stop
        if include_speed:
            yield GCodeSpindleSpeed(self.speed)
        if include_spindle_start:
            yield GCodeStartSpindleCW() if self.spindle_cw else GCodeStartSpindleCCW()
        if include_feed:
            yield GCodeFeedRate(self.feed)
        if include_start:
            yield GCodeLinearMove(X=ax, Y=ay, Z=az)
        if include_stop:
            yield GCodeLinearMove(X=bx, Y=by, Z=bz)


@dataclass(unsafe_hash=True)
class ArcCut():
    start: Tuple[float, float, float]
    stop: Tuple[float, float, float]  # XYZ params
    offset: Tuple[float, float, float]  # IJK params

    clockwise: bool = True  # switch between G2 and G3
    feed: float = 0  # mm/s # TODO look into the use of rev/mm
    speed: float = 0  # rpm
    spindle_cw: bool = True

    def gcode(self, include_start=False, include_stop=True, include_feed=False, include_speed=False, include_spindle_start=False):
        ax, ay, az = self.start
        bx, by, bz = self.stop
        ox, oy, oz = self.offset
        if include_speed:
            yield GCodeSpindleSpeed(self.speed)
        if include_spindle_start:
            yield GCodeStartSpindleCW() if self.spindle_cw else GCodeStartSpindleCCW()
        if include_feed:
            yield GCodeFeedRate(self.feed)
        if include_start:
            yield GCodeLinearMove(X=ax, Y=ay, Z=az)
        if include_stop:
            yield (GCodeArcMoveCW if self.clockwise else GCodeArcMoveCCW)(X=bx, Y=by, Z=bz, I=ox, J=oy, K=oz)


@dataclass(unsafe_hash=True)
class Job:
    # Operations should be stored in a path graph where nodes are operations and edges are setups
    operations: nx.DiGraph


@dataclass(unsafe_hash=True)
class Machine:
    # Machine is used by the AR to GCode solver
    useTool: Callable[[Tool], List[GCode]]
    mapRPM: Callable[[float], float] = lambda x: x
    # ordered list of the tools available in the ATC, 0 length list means no ATC
    inventory: List[Tool] = field(default_factory=list)


@dataclass(unsafe_hash=True)
class Stock:
    # Stock can be used by the AR generator
    pass  # TODO define the stock engine