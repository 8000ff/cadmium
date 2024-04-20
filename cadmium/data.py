from dataclasses import dataclass, field
from typing import Tuple, Callable, List, Union
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
class CuttingTool:
    # TODO find better names
    shank_diameter: float
    end_diameter: float
    edge_height: float = 0  # zero is for cylindrical tools
    edge_radius: float = np.Infinity  # accepts negative values
    radius: float = field(init=False)
    max_cutting_depth = np.Infinity # how deep the tool can cut, by default assumes infinity
    
    def __post_init__(self):
        self.radius = self.end_diameter/2.
        if self.shank_diameter == 0:
            self.shank_diameter = self.end_diameter

@dataclass(unsafe_hash=True)
class ProbingTool:
    shank_diameter: float # TODO define the probing tool

Tool = CuttingTool | ProbingTool

@dataclass(unsafe_hash=True)
class LinearCut:
    start: Tuple[float, float, float]
    stop: Tuple[float, float, float]  # XYZ params
    feed: float = 0  # mm/s # TODO look into the use of rev/mm
    speed: float = 0  # rpm
    spindle_cw: bool = True

    def __post_init__(self):
        self.start = tuple(self.start)
        self.stop = tuple(self.stop)

    def gcode(self, include_start=False, include_stop=True, include_feed=False, include_speed=False, include_spindle_start=False):
        assert self.feed > 0 and self.speed > 0 # Don't want to generate GCode with 0 feedrate of 0 spindle speed
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
class ArcCut:
    start: Tuple[float, float, float]
    stop: Tuple[float, float, float]  # XYZ params
    offset: Tuple[float, float, float]  # IJK params

    clockwise: bool = True  # switch between G2 and G3
    feed: float = 0
    speed: float = 0  # rpm
    spindle_cw: bool = True
    turns : int = 1 # P param

    def __post_init__(self):
        self.start = tuple(self.start)
        self.stop = tuple(self.stop)
        self.offset = tuple(self.offset)

    def gcode(self, include_start=False, include_stop=True, include_feed=False, include_speed=False, include_spindle_start=False):
        assert self.feed > 0 and self.speed > 0 # Don't want to generate GCode with 0 feedrate of 0 spindle speed
        ax, ay, az = self.start
        bx, by, bz = self.stop
        ox, oy, oz = [ None if o == 0 else o for o in self.offset]
        p = None if self.turns == 1 else self.turns
        if include_speed:
            yield GCodeSpindleSpeed(self.speed)
        if include_spindle_start:
            yield GCodeStartSpindleCW() if self.spindle_cw else GCodeStartSpindleCCW()
        if include_feed:
            yield GCodeFeedRate(self.feed)
        if include_start:
            yield GCodeLinearMove(X=ax, Y=ay, Z=az)
        if include_stop:
            yield (GCodeArcMoveCW if self.clockwise else GCodeArcMoveCCW)(**{ k:v for k,v in {'X':bx, 'Y':by, 'Z':bz, 'I':ox, 'J':oy, 'K':oz,'P':p}.items() if v is not None})

@dataclass(unsafe_hash=True)
class NoneCut:
    # The NoneCut only exists at the top of the cut tree
    pass

Cut = LinearCut | ArcCut | NoneCut

@dataclass(unsafe_hash=True)
class LinearProbe:
    feed: float = 0 # TODO define linear probing moves
@dataclass(unsafe_hash=True)
class NoneProbe:
    pass # The NoneProbe only exists at the top of the probe tree

Probe = LinearProbe | NoneProbe
Move = Cut | Probe

@dataclass(unsafe_hash=True)
class CuttingOperation:
    # Cuts is a tree, root must be empty
    cuts: nx.DiGraph
    tool: CuttingTool

@dataclass(unsafe_hash=True)
class ProbingOperation:
    # define probing moves
    prob: nx.DiGraph
    tool: ProbingTool

@dataclass(unsafe_hash=True)
class NoneOperation:
    # The NoneOperation only exists at the top of the operation tree
    pass

Operation = CuttingOperation | ProbingOperation | NoneOperation

@dataclass(unsafe_hash=True)
class Job:
    # Operations should be stored in a path graph where nodes are operations and edges are setups
    operations: nx.DiGraph

@dataclass(unsafe_hash=True)
class Machine:
    # Machine is used by the AR to GCode solver
    useTool: Callable[[Tool], List[GCode]]
    park: Callable[[], List[GCode]]
    mapRPM: Callable[[float], float] = lambda x: x
    # ordered list of the tools available in the ATC, 0 length list means no ATC
    inventory: List[Tool] = field(default_factory=list)

@dataclass(unsafe_hash=True)
class Stock:
    # Stock can be used by the AR generator
    pass  # TODO define the stock engine
