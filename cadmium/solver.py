from .data import Job,Operation,LinearCut,ArcCut,Machine
from typing import List,Union
from pygcode import GCodeAbsoluteDistanceMode, GCodeCancelToolLengthOffset, GCodeCutterRadiusCompOff, GCodeEndProgram, GCodeFeedRate, GCodeLinearMove, GCodeMoveInMachineCoords, GCodePauseProgram, GCodeRapidMove, GCodeStopSpindle
import networkx as nx
from more_itertools import windowed  
import numpy as np

# the solver turns a Job (IR) into gcode
# use safe height policy, will Z hop if cuts are not contiguous
# work in machine coordinates
def safe_height_solver(job : Job, machine: Machine, safe_height: float = 0,retract_feed : float = 100,dwell: float = 3, eps : float = .01,pause_every_op : bool = False,initial_tool_change: bool = True):
    order_of_operations : List[Operation] = list(nx.dfs_preorder_nodes(job.operations))
    yield GCodeAbsoluteDistanceMode()
    yield GCodeCutterRadiusCompOff()
    yield GCodeMoveInMachineCoords()
    yield GCodeCancelToolLengthOffset()
    for (pre,op) in windowed(order_of_operations,2):
        # FIXME root is causing another problem here, this conditional arrangement prevents dereferencing pre.tool when pre is root
        if pre == 'root':
            if initial_tool_change:
                yield from machine.useTool(op.tool)
        elif pre.tool != op.tool:
            yield from machine.useTool(op.tool)

        if pause_every_op:
            yield GCodeRapidMove(X=0,Y=0)
            yield GCodeStopSpindle()
            yield GCodePauseProgram()

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
                    # retract feed can be set by the user to a safer speed than G0 speed
                    yield GCodeFeedRate(retract_feed)
                    yield GCodeLinearMove(Z=safe_height)
                    yield GCodeRapidMove(X=now.start[0],Y=now.start[1])
                yield from now.gcode(jump,True,pre.feed != now.feed or jump, pre.speed != now.speed,False)
        yield GCodeRapidMove(Z=safe_height)
    yield GCodeEndProgram()