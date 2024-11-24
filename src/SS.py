from objects import Trapezoid, LineSegment, Point
from typing import Generic, TypeVar, Optional
NODE_TYPE = TypeVar('T')
DEBUG = False

class Node(Generic[NODE_TYPE]):
    def __init__(self, data: Optional[NODE_TYPE] = None, left=None, right=None) -> None:
        self.data = data # Can be region, point, or line segment
        self.left = left # Left of point / above line segment - can be Node
        self.right = right # Right of point / below line segment - can ne Node

    # overwrites this node with the data from another node
    def overwrite(self, data, left, right) -> None:
        self.data = data
        self.left = left
        self.right = right

    def print(self) -> None:
        print(f"Node(\n\tdata: {self.data}\n\t left: {self.left}\n\t right: {self.right})")

class SearchStructure:
    def __init__(self, BB: Trapezoid) -> None:
        self.root = Node(BB)

    # Calculate the cross product of vectors (seg.start -> seg.end) and (seg.start -> p)  O(1) since it's just some calculations no loops and such
    def _is_below(self, p: Point, seg: LineSegment) -> bool:
        return ((seg.end.x - seg.start.x) * (p.y - seg.start.y) - (seg.end.y - seg.start.y) * (p.x - seg.start.x)) < 0 # Negative cross product -> p is to the right of seg -> p is below

    # Find the region in which the given point is contained by querying the search structure
    def _find_region(self, point: Point) -> Node[Trapezoid]:
        current = self.root # node
        while not isinstance(current.data, Trapezoid):
            data = current.data
            if isinstance(data, Point):
                current = current.right if point.x > data.x else current.left
            elif isinstance(data, LineSegment):
                current = current.right if self._is_below(point, data) else current.left
        return current # node with the trapezoide containing query point

    # find next neighbor in regards to s_i
    def _next_neighbour(self, region: Node[Trapezoid], seg: LineSegment) -> Node[Trapezoid] | None:
        # if trapezoid has rightN return 0th / 1st neighbour if rightp below / above segment, unless len(rightN) == 1 then just return 0th neighbour otherwise None
        return None if not region.data.rightN else (region.data.rightN[0] if self._is_below(region.data.rightp, seg) or len(region.data.rightN) == 1 else region.data.rightN[1])

    def _follow_segment(self, region: Node[Trapezoid], seg: LineSegment) -> list[Node[Trapezoid]]:
        regions = []
        current = region
        # appends delta_0 -> delta_k-1 - these regions are intersected by s_i
        while current and (current.data.leftp.x < seg.end.x):
            regions.append(current)
            current = self._next_neighbour(current, seg)
        return regions

    def _find_intersected_trapezoids(self, seg: LineSegment) -> list[Node[Trapezoid]]:
        return self._follow_segment(self._find_region(seg.start), seg) # find  region for start point of segment and use it to find trapezoids which follow s_i

    # Point is left-/right-defining point of current  X = B / above, Y = C / below
    def _assign_outer_neighbours_aux(self, current: Trapezoid, X: Node[Trapezoid], Y: Node[Trapezoid], 
                                     L_or_R: str, L_or_R_flipped: str, point: Point, seg: LineSegment) -> None:
        currentN = getattr(current, L_or_R)
        if currentN and len(currentN) == 2:
            if not self._is_below(point, seg): # if segment is inserted below the left/right-defining point of current => X receives outermost neighbour
                setattr(currentN[0].data, L_or_R_flipped, [X])
                setattr(X.data, L_or_R, [currentN[0]])
            else: # if segment is inserted above the (left/right)-defining point of current => Y receives outermost neighbour
                setattr(currentN[1].data, L_or_R_flipped, [Y])
                setattr(Y.data, L_or_R, [currentN[1]])

    def _assign_outermost_neighbour_left(self, current: Trapezoid, X: Node[Trapezoid], Y: Node[Trapezoid], seg: LineSegment) -> None:
        self._assign_outer_neighbours_aux(current, X, Y, 'leftN', 'rightN', current.leftp, seg)

    def _assign_outermost_neighbour_right(self, current: Trapezoid, X: Node[Trapezoid], Y: Node[Trapezoid], seg: LineSegment) -> None:
        self._assign_outer_neighbours_aux(current, X, Y, 'rightN', 'leftN', current.rightp, seg)

    def _split_into_above_below(self, current: Trapezoid, seg: LineSegment) -> tuple[Node[Trapezoid], Node[Trapezoid]]:
        above = Node(Trapezoid(current.upper, seg, current.leftp, current.rightp))
        below = Node(Trapezoid(seg, current.lower, current.leftp, current.rightp))
        # Assings left- / right-outermost neighbours to above and below
        self._assign_outermost_neighbour_left(current, above, below, seg)
        self._assign_outermost_neighbour_right(current, above, below, seg)
        return above, below

    def _merge_traps_aux(self, LTN: Node[Trapezoid], RTN: Node[Trapezoid], is_above: bool) -> Node[Trapezoid]:
        left, right = LTN.data, RTN.data # LTN = B / C, RTN = above / below
        can_merge = left.upper == right.upper if is_above else left.lower == right.lower
        if can_merge: # they share seg as lower or upper so sharing the other => can be merged
            left.rightp = right.rightp # extend left's rightp to right's rightp
            left.rightN = right.rightN # set right's right neighbours as left's right neighbours
            RTN.data = left # since left and right merged everything that pointed to right's node which now has left's data so effectively everything now points to left instead (different node but both contain left's data)
            return LTN
        else:
            left.rightN = ([left.rightN[0], RTN] if is_above else [RTN, left.rightN[0]]) if left.rightN else [RTN]
            right.leftN = ([right.leftN[0], LTN] if is_above else [LTN, right.leftN[0]]) if right.leftN else [LTN]
            return RTN
        
    def _merge_above_traps(self, LTN: Node[Trapezoid], RTN: Node[Trapezoid]) -> Node[Trapezoid]:
        if DEBUG:
            print(f"MERGE ABOVE TRYING:\n{LTN.data.label} -> {RTN.data.label}")
        return self._merge_traps_aux(LTN, RTN, is_above=True)

    def _merge_below_traps(self, LTN: Node[Trapezoid], RTN: Node[Trapezoid]) -> Node[Trapezoid]:
        if DEBUG:
            print(f"MERGE BELOW TRYING:\n{LTN.data.label} -> {RTN.data.label}")
        return self._merge_traps_aux(LTN, RTN, is_above=False)

    def _merge_traps(self, traps: list[Node[Trapezoid]], B: Node[Trapezoid], C: Node[Trapezoid], 
                     BL: Node[Trapezoid], CL: Node[Trapezoid], seg: LineSegment) -> tuple[Node[Trapezoid]]:
        # handle merging BF, CF with the intermediate trapezoids
        for delta_i in traps[1:-1]:
            above, below = self._split_into_above_below(delta_i.data, seg)
            B = self._merge_above_traps(B, above)
            C = self._merge_below_traps(C, below)
            # Rearrange tree and transform current into s_i node
            delta_i.overwrite(seg, B, C)
        # Final merge between B / BL and C / CL after intermediate merging
        B = self._merge_above_traps(B, BL)
        C = self._merge_below_traps(C, CL)
        return B, C

    def _update_outer_aux(self, current: Trapezoid, L_or_R: str, L_or_R_flipped: str, X: Node[Trapezoid]) -> None:
        currentN = getattr(current, L_or_R)
        if currentN:
            for n in currentN:
                neighbour_list = getattr(n.data, L_or_R_flipped)
                if len(neighbour_list) == 2:
                    neighbour_list[0 if neighbour_list[0].data == current else 1] = X
                    setattr(n.data, L_or_R_flipped, neighbour_list)
                else: # only has one neighbour
                    setattr(n.data, L_or_R_flipped, [X])

    def _update_outer_left_neighbours(self, trap: Trapezoid, X: Node[Trapezoid]) -> None:
        self._update_outer_aux(trap, 'leftN', 'rightN', X)

    def _update_outer_right_neighbours(self, trap: Trapezoid, X: Node[Trapezoid]) -> None:
        self._update_outer_aux(trap, 'rightN', 'leftN', X)

    def _handle_first_trap(self, trap: Node[Trapezoid], seg: LineSegment) -> tuple[Node[Trapezoid], Node[Trapezoid], Node[Trapezoid]]:
        delta_0 = trap.data
        A = Node(Trapezoid(delta_0.upper, delta_0.lower, delta_0.leftp, seg.start, leftN=delta_0.leftN))
        B = Node(Trapezoid(delta_0.upper, seg, seg.start, delta_0.rightp, leftN=[A]))
        C = Node(Trapezoid(seg, delta_0.lower, seg.start, delta_0.rightp, leftN=[A]))
        A.data.rightN = [B, C]
        self._assign_outermost_neighbour_right(trap.data, B, C, seg)
        self._update_outer_left_neighbours(trap.data, A)
        return A, B, C

    def _handle_last_trap(self, trap: Node[Trapezoid], seg: LineSegment) -> tuple[Node[Trapezoid], Node[Trapezoid], Node[Trapezoid]]:
        delta_k = trap.data
        A = Node(Trapezoid(delta_k.upper, delta_k.lower, seg.end, delta_k.rightp, rightN=delta_k.rightN))
        B = Node(Trapezoid(delta_k.upper, seg, delta_k.leftp, seg.end, rightN=[A]))
        C = Node(Trapezoid(seg, delta_k.lower, delta_k.leftp, seg.end, rightN=[A]))
        A.data.leftN = [B, C]
        self._assign_outermost_neighbour_left(trap.data, B, C, seg)
        self._update_outer_right_neighbours(trap.data, A)
        return A, B, C

    # so you don't need to count; this returns a tuple of six trapezoid nodes.
    def _handle_first_last_trap(self, traps: list[Node[Trapezoid]], seg: LineSegment
                                ) -> tuple[Node[Trapezoid], Node[Trapezoid], Node[Trapezoid], Node[Trapezoid], Node[Trapezoid], Node[Trapezoid]]:
        return *self._handle_first_trap(traps[0], seg), *self._handle_last_trap(traps[-1], seg)

    def _split_trap_into_four(self, trap: Node[Trapezoid], seg:LineSegment
                              ) -> tuple[Node[Trapezoid], Node[Trapezoid], Node[Trapezoid], Node[Trapezoid]]:
        delta = trap.data
        # Make the trapezoids that should replace the previous one and assign neighbours
        A = Node(Trapezoid(delta.upper, delta.lower, delta.leftp, seg.start, leftN=delta.leftN))
        B = Node(Trapezoid(delta.upper, delta.lower, seg.end, delta.rightp, rightN=delta.rightN))
        C = Node(Trapezoid(delta.upper, seg, seg.start, seg.end, leftN=[A], rightN=[B],))
        D = Node(Trapezoid(seg, delta.lower, seg.start, seg.end, leftN=[A], rightN=[B]))
        A.data.rightN = [C, D]
        B.data.leftN = [C, D]
        self._update_outer_left_neighbours(trap.data, A)
        self._update_outer_right_neighbours(trap.data, B)
        return A, B, C, D

    # Inserts a line segment into the search structure and updates neighbour-relations
    def insert(self, seg: LineSegment, debug: bool = False) -> None:
        global DEBUG
        DEBUG = debug
        traps = self._find_intersected_trapezoids(seg)

        if len(traps) > 1:
            if DEBUG:
                print(f"case {seg} intersects multiple trapezoids")
            AF, BF, CF, AL, BL, CL = self._handle_first_last_trap(traps, seg)
            traps[0].overwrite(seg.start, AF, Node(seg, BF, CF)) # overwrite for traps[0] and rearrange tree
            B, C = self._merge_traps(traps, BF, CF, BL, CL, seg) # tries to merge traps[i] -> traps[i+1] overwrites and rearrange tree if needed
            traps[-1].overwrite(seg.end, Node(seg, B, C), AL) # overwrite for traps[-1] and rearrange tree
        else: # traps <= 1, so entire segment is contained within a single trapezoid / region
            if DEBUG:
                print(f"case {seg} intersects single trapezoid")
            A, B, C, D = self._split_trap_into_four(traps[0], seg)
            # rearrange SS structure to reflect that trapezoids A, B, C, D has replaced delta_0
            traps[0].overwrite(seg.start, A, Node(seg.end, Node(seg, C, D), B))
        
        if DEBUG:
            self.show()
    
    def query(self, point: Point) -> Node[Trapezoid]:
        region: Node[Trapezoid] = self._find_region(point)
        region.data.color = "red"
        return region

###################################### METHODS FOR SHOWING / retrieving D AND T ######################################
    def _get_TM_aux(self, current: Node) -> list[Node[Trapezoid]]:
        if (not current.left) and (not current.right): # Trapezoid nodes do not have left right children
            if not current.data.collected: # ensures each trapezoid is only collected once for display purposes
                current.data.collected = True
                return [current.data] 
            else:
                return []
        else:
            return self._get_TM_aux(current.left) + self._get_TM_aux(current.right)

    def get_TM(self) -> list[Node[Trapezoid]]:
        traps = self._get_TM_aux(self.root)
        if DEBUG:
            print(f"There are #{len(traps)} in the trapezodial map")
        return traps
    
    def _to_string_aux(self, current: Node, level: int = 0, s: str = "Root: ", string: str = "") -> str:
        if not (current and current.data):
            return ""
        indent = "    " * level
        if current.data.__class__.__name__.lower() == "trapezoid":
            string += (indent + s + current.data.to_string_with_indent(indent))  + "\n"
        else:
            string += (indent + s + str(current.data)) + "\n"

        string += self._to_string_aux(current.left, level+1, s="L: |--->")
        string += self._to_string_aux(current.right, level+1, s="R: |--->")
        return string
    
    def to_string(self, current: Node) -> str:
        return self._to_string_aux(current).strip()

    def show(self) -> None:
        print(self.to_string(current=self.root))
######################################################################################################################