from .data import Job,Operation,LinearCut,ArcCut
from typing import List,Union
from pygcode import *
import networkx as nx
from more_itertools import *
import numpy as np

# the solver turns a Job (IR) into gcode
# use safe height policy, will Z hop if cuts are not contiguous
# will insert a pause between every operation
# work in machine coordinates
def safe_height_solver(job : Job, machine: Machine, safe_height: float = 0,dwell: float = 3, eps : float = .01,pause_every_op : bool = False):
    order_of_operations : List[Operation] = list(nx.dfs_preorder_nodes(job.operations))
    order_of_operations = order_of_operations[1:]
    yield GCodeAbsoluteDistanceMode()
    yield GCodeCutterRadiusCompOff()
    yield GCodeMoveInMachineCoords()
    yield GCodeCancelToolLengthOffset()
    for op in order_of_operations:
        cuts : List[Union[LinearCut,ArcCut]] = list(nx.dfs_preorder_nodes(op.cuts))
        first_cut,*rest = cuts
        yield GCodeRapidMove(Z=safe_height)
        yield GCodeRapidMove(X=first_cut.start[0],Y=first_cut.start[1])
        yield from first_cut.gcode(True,True,True,True,True)
        if len(rest) > 0:
            for (pre,now) in windowed(cuts,2):
                pstop,nstart = np.array((pre.stop,now.start))
                jump = np.linalg.norm(pstop-nstart) > eps
                if jump:
                    yield GCodeLinearMove(Z=safe_height)
                    yield GCodeRapidMove(X=now.start[0],Y=now.start[1])
                yield from now.gcode(jump,True,pre.feed != now.feed, pre.speed != now.speed,False)
        yield GCodeRapidMove(Z=safe_height)
        if pause_every_op:
            yield GCodeRapidMove(X=0,Y=0)
            yield GCodeStopSpindle()
            yield GCodePauseProgram()
    yield GCodeEndProgram()