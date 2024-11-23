# This was in _split_trap_into_four before to fix neighbours
if delta.leftN:
    if len(delta.leftN) >= 2:
        delta.leftN[0].data.rightN = [A]
        delta.leftN[1].data.rightN = [A]
    else:
        if delta.leftN[0].data.rightN and len(delta.leftN[0].data.rightN) >= 2:
            idx = 0 if delta.leftN[0].data.rightN[0] == trap else 1
            delta.leftN[0].data.rightN[idx] = A
        else:
            delta.leftN[0].data.rightN = [A]

if delta.rightN:
    if len(delta.rightN) >= 2:
        delta.rightN[0].data.leftN = [B]
        delta.rightN[1].data.leftN = [B]
    else:
        if delta.rightN[0].data.leftN and len(delta.rightN[0].data.leftN) >= 2:
            idx = 0 if delta.rightN[0].data.leftN[0] == trap else 1
            delta.rightN[0].data.leftN[idx] = B
        else:
            delta.rightN[0].data.leftN = [B]






# THIS WAS IN CREATE TRAPEZOIDS LAST
# assign neighbourhood between either B or C and the "outermost", left-neighbouring, region
if trap.leftN and len(trap.leftN) == 2:
    if not self._is_below(trap.leftp, seg): # leftp of trap is above seg
        trap.leftN[0].data.rightN = [B] # give the upper left neighbour of delta_k to B
        B.data.leftN = [trap.leftN[0]] # also the other way
    else: # leftp of trap is below seg
        trap.leftN[1].data.rightN = [C] # give the lower left neighbour of delta_k to C
        C.data.leftN = [trap.leftN[1]] # also the other way
            
# THIS WAS IN CREATE TRAPEZOIDS FIRST
# assign neighbourhood between either B or C and the "outermost", right-neighbouring, region
if trap.rightN and len(trap.rightN) == 2:
    if not self._is_below(trap.rightp, seg): # trap.rightp is above segment
        trap.rightN[0].data.leftN = [B] 
        B.data.rightN = [trap.rightN[0]]
    else: # trap.rightp is below segment
        trap.rightN[1].data.leftN = [C]
        C.data.rightN = [trap.rightN[1]]
        
# THIS WAS IN SPLIT INTO ABOVE BELOW 
###################################### FIXME MAKE AUX ###################################
 # if delta_i has two left neighbours, assign neighbour-relation between above or below and the outermost region to the left
 if current.leftN and len(current.leftN) == 2:
     if not self._is_below(current.leftp, seg): # if segment is inserted below the left-defining point of current
         current.leftN[0].data.rightN = [above]
         above.data.leftN = [current.leftN[0]] 
     else: # if segment is inserted above the left-defining point of current
         current.leftN[1].data.rightN = [below]
         below.data.leftN = [current.leftN[1]]
 
 # if delta_i has two right neighbours, assign neighbour-relation between above or below and the outermost region to the right
 if current.rightN and len(current.rightN) == 2:
     if not self._is_below(current.rightp, seg): # if segment is inserted below the right-defining point of current
         current.rightN[0].data.leftN = [above]
         above.data.rightN = [current.rightN[0]] # this should result in above getting two right neighbours by _merge_trapezoids()
     else: # if segment is inserted above the right-defining point of current
         current.rightN[1].data.leftN = [below]
         below.data.rightN = [current.rightN[1]] # this should result in below getting two right neighbours by _merge_trapezoids()
 #########################################################################################

# Point is left-/right-defining point of current
def _assign_outer_neighbours_aux(self, current: Node[Trapezoid], A: Node, B , 
                                 current_connection: str, currentN_connection: str, point: Point, seg: LineSegment):
     currentN = getattr(current, current_connection)
     if currentN and len(currentN) == 2:
        if not self._is_below(getattr(current, point), seg): # if segment is inserted below the left-defining point of current
            setattr(currentN[0].data, currentN_connection, [above])
            above.data.leftN = [currentN[0]] 
        else: # if segment is inserted above the left-defining point of current
            currentN[1].data.rightN = [below]
            below.data.leftN = [currentN[1]]



def _assign_outer_neighbours_right(self, ):
    pass


def _assign_outer_neighbours_left(self, ):
    pass





# THIS WAS IN CREATE TRAPEZOIDS LAST
# rearrange delta_k's previous right-neighbours to point to A
if trap.rightN: # if trap being split by s_i has right neighbors
    for n in trap.rightN:
        if len(n.data.leftN) == 2:
            idx = 0 if n.data.leftN[0].data == trap else 1
            n.data.leftN[idx] = A
        else: # only has one neighbour
            n.data.leftN = [A]

# THIS WAS IN CREATE TRAPEZOIDS FIRST
# rearrange delta_0's previous left neighbours to point to A
if trap.leftN: # if trap being split by s_i has left neighbors
    for n in trap.leftN:
        if n.data.rightN and len(n.data.rightN) >= 2:
            idx = 0 if n.data.rightN[0].data == trap else 1
            n.data.rightN[idx] = A
        else: # only has one neighbour
            n.data.rightN = [A]



