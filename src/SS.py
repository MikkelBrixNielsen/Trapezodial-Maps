from objects import Trapezoid, LineSegment, Point
import matplotlib.pyplot as plt

DEBUG = False

class Node:
    def __init__(self, data=None, left=None, right=None):
        self.data = data # Can be region, point, or line segment
        self.left = left # Left of point / above line segment
        self.right = right # Right of point / below line segment

    # overwrites this node with the data from another node
    def overwrite(self, data, left, right):
        self.data = data
        self.left = left
        self.right = right

    def print(self):
        print(f"Node(\n\tdata: {self.data}\n\t left: {self.left}\n\t right: {self.right})")

class SearchStructure:
    def __init__(self, BB: Trapezoid):
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
        return (region.data.rightN[0] if self._is_below(region.data.rightp, seg) or len(region.data.rightN) == 1 else region.data.rightN[1]) if region.data.rightN else None

    def _follow_segment(self, region: Node[Trapezoid], seg: LineSegment) -> list[Node]:
        regions = []
        current = region
        # appends delta_0 -> delta_k-1 - these regions are intersected by s_i
        while current and (not seg.end.x < current.data.leftp.x):
            regions.append(current)
            current = self._next_neighbour(current, seg)
        return regions

    def _find_intersected_trapezoids(self, seg: LineSegment) -> list[Node[Trapezoid]]:
        return self._follow_segment(self._find_region(seg.start), seg) # find  region for start point of segment and use it to find trapezoids which follow s_i

    # # Tries to merge delta_i with delta_i+1 and returns the trapezoid to continue to try and merge delta_i+2 and so on
    # def _merge_above_aux(self, left_region: Node, right_region: Node) -> Node[Trapezoid]:
    #     left, right = left_region.data, right_region.data
    #     if left.upper == right.upper: # Merging -> merge left into right and return left_region_node
    #         left.rightp = right.rightp # extend left into right
    #         right_region.data = left_region.data # overwrite node data
    #         left.rightN = right.rightN # give neighbours
    #         return left_region
    #     else: # Not merging -> assign neighbour-relations and return right_region_node
    #         # if left has a right neighbour, it keeps it and gets right as neighbour as well, otherwise it just gets right_region
    #         left.rightN = [left.rightN[0], right] if left.rightN else [right]
    #         # if right has a left neighbour, it keeps it and gets left_region as neighbour as well, otherwise it just gets left_region
    #         right.leftN = [right.leftN[0], left] if right.leftN else [left]
    #         return right_region
    
    # # same as _merge_above_aux but checks lower defining line segment
    # def _merge_below_aux(self, left_region_node, right_region_node):
    #     left_region, right_region = left_region_node.data, right_region_node.data
    #     if left_region.lower == right_region.lower: # Merging -> merge left into right and return left_region_node
    #         left_region.rightp = right_region.rightp # extend left_region into right_region
    #         right_region_node.data = left_region_node.data # overwrite node data
    #         left_region.rightN = right_region.rightN # give neighbours
    #         return left_region_node 
    #     else: # Not merging -> assign neighbour-relations and return right_region_node
    #         # if left_region has a right neighbour, it keeps it and gets right_region as well, otherwise it just gets right_region
    #         left_region.rightN = [right_region_node, left_region.rightN[0]] if left_region.rightN else [right_region_node]
    #         # if right_region has a left neighbour, it keeps it and gets left_region as well, otherwise it just gets left_region
    #         right_region.leftN = [left_region_node, right_region.leftN[0]] if right_region.leftN else [left_region_node]
    #         return right_region_node

    # def _merge_trapezoids(self, left_region_node, right_region_node, is_above):
    #     if is_above:
    #         return self._merge_above_aux(left_region_node, right_region_node)
    #     else:
    #         return self._merge_below_aux(left_region_node, right_region_node)

    def _merge_traps_aux(self, LTN: Node[Trapezoid], RTN: Node[Trapezoid], is_above: bool) -> Node[Trapezoid]:
        left, right = LTN.data, RTN.data # LTN = B / C, RTN = above / below
        can_merge = left.upper == right.upper if is_above else left.lower == right.lower
        if can_merge: # they share seg as lower or upper so sharing the other => can be merged
            if DEBUG:
                print(f"{LTN.data.label} merged with {RTN.data.label}")
            left.rightp = right.rightp # extend left's rightp to right's rightp
            left.rightN = right.rightN # set right's right neighbours as left's right neighbours
            RTN.data = left # since left and right merged everything that pointed to right's node which now has left's data so effectively everything now points to left instead (different node but both contain left's data)
            return LTN
        else:
        # FIXME ASSIGN NEIGHBOURS LIKE IN THE OUTCOMMENTED CODE ABOVE
            return RTN

    def _merge_above_traps(self, LTN: Node[Trapezoid], RTN: Node[Trapezoid]) -> Node[Trapezoid]:
        if DEBUG:
            print(f"MERGE ABOVE TRYING:\n{LTN.data.label} -> {RTN.data.label}")
        return self._merge_traps_aux(LTN, RTN, is_above=True)
            
    def _merge_below_traps(self, LTN: Node[Trapezoid], RTN: Node[Trapezoid]) -> Node[Trapezoid]:
        if DEBUG:
            print(f"MERGE BELOW TRYING:\n{LTN.data.label} -> {RTN.data.label}")
        return self._merge_traps_aux(LTN, RTN, is_above=False)

    def _split_into_above_below(self, current: Trapezoid, seg: LineSegment) -> tuple[Node[Trapezoid], Node[Trapezoid]]:
        above = Node(Trapezoid(current.upper, seg, current.leftp, current.rightp))
        below = Node(Trapezoid(seg, current.lower, current.leftp, current.rightp))
        
        # FIXME ASSIGN NEIGHBOURS TO ABOVE AND BELOW BASED ON TRAPS's NEIHGBOURS AND ITS RIGHTP

        # if DEBUG:
        #     print(f"above: {above.data}")
        #     print(f"below: {below.data}")
        return above, below

    def _merge_traps(self, traps: list[Node[Trapezoid]], B: Node[Trapezoid], C: Node[Trapezoid], 
                     BL: Node[Trapezoid], CL: Node[Trapezoid], seg: LineSegment) -> tuple[Node[Trapezoid]]:
        # handle merging BF, CF with the intermediate trapezoids
        for trap in traps[1:-1]:
            above, below = self._split_into_above_below(trap.data, seg)
            B = self._merge_above_traps(B, above)
            C = self._merge_below_traps(C, below)
            # Rearrange tree and transform current into s_i node
            trap.overwrite(seg, B, C)

        # Final merge between B / BL and C / CL after intermediate merging
        B = self._merge_above_traps(B, BL)
        C = self._merge_below_traps(C, CL)
        return B, C

    def _handle_first_trap(self, trap: Node[Trapezoid], seg: LineSegment) -> tuple[Node[Trapezoid], Node[Trapezoid], Node[Trapezoid]]:
        #if DEBUG:
        #    print(f"delta_0:\n{trap.data}")
        delta_0 = trap.data
        A = Node(Trapezoid(delta_0.upper, delta_0.lower, delta_0.leftp, seg.start, leftN=delta_0.leftN))
        B = Node(Trapezoid(delta_0.upper, seg, seg.start, delta_0.rightp, leftN=[A]))
        C = Node(Trapezoid(seg, delta_0.lower, seg.start, delta_0.rightp, leftN=[A]))
        A.data.rightN = [B, C]

        # FIXME ASSIGN B / C NEIGHBOURS 
        # FIXME ASSIGN traps rightN to point to A 

        return A, B, C

    def _handle_last_trap(self, trap: Node[Trapezoid], seg: LineSegment) -> tuple[Node[Trapezoid], Node[Trapezoid], Node[Trapezoid]]:
        #if DEBUG:
        #    print(f"delta_k:\n{trap.data}")
        delta_k = trap.data
        A = Node(Trapezoid(delta_k.upper, delta_k.lower, seg.end, delta_k.rightp, rightN=delta_k.rightN))
        B = Node(Trapezoid(delta_k.upper, seg, delta_k.leftp, seg.end, rightN=[A]))
        C = Node(Trapezoid(seg, delta_k.lower, delta_k.leftp, seg.end, rightN=[A]))
        A.data.leftN = [B, C]

        # FIXME ASSIGN B / C NEIGHBOURS 
        # FIXME ASSIGN traps rightN to point to A 

        
        return A, B, C

    # so you dont need to count; this returns a tuple of six trapezoid nodes.
    def _handle_first_last_trap(self, traps: list[Node[Trapezoid]], seg: LineSegment
                                ) -> tuple[Node[Trapezoid], Node[Trapezoid], Node[Trapezoid], Node[Trapezoid], Node[Trapezoid], Node[Trapezoid]]:
        return *self._handle_first_trap(traps[0], seg), *self._handle_last_trap(traps[-1], seg)

    def _split_trap_into_four(self, trap: Node, seg:LineSegment
                              ) -> tuple[Node[Trapezoid], Node[Trapezoid], Node[Trapezoid], Node[Trapezoid]]:
        delta = trap.data
        # Make the trapezoids that should replace the previous one and assign neighbours
        A = Node(Trapezoid(delta.upper, delta.lower, delta.leftp, seg.start, leftN=delta.leftN))
        B = Node(Trapezoid(delta.upper, delta.lower, seg.end, delta.rightp, rightN=delta.rightN))
        C = Node(Trapezoid(delta.upper, seg, seg.start, seg.end, rightN=[B], leftN=[A]))
        D = Node(Trapezoid(seg, delta.lower, seg.start, seg.end, rightN=[B], leftN=[A]))
        A.data.rightN = [C, D]
        B.data.leftN = [C, D]

        # FIXME make trap LeftN point to A
        # FIXME make trap rightN point to B
        
        return A, B, C, D

    # Inserts a line segment into the search structure and updates neighbour-relations
    def insert(self, seg, debug=False):
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

###################################### METHODS FOR SHOWING / retrieving D AND T ######################################
    def _get_TM_aux(self, current: Node):
        if (not current.left) and (not current.right): # Trapezoid nodes do not have left right children
            if not current.data.collected: # ensures each trapezoid is only collected once for display purposes
                current.data.collected = True
                return [current.data] 
            else:
                return []
        else:
            return self._get_TM_aux(current.left) + self._get_TM_aux(current.right)

    def get_TM(self):
        traps = self._get_TM_aux(self.root)
        if DEBUG:
            print(f"There are #{len(traps)} in the trapezodial map")
        return traps
    
    def _to_string_aux(self, current, level=0, s="Root: ", string=""):
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
    
    def to_string(self, current):
        return self._to_string_aux(current).strip()

    def show(self):
        print(self.to_string(current=self.root))
######################################################################################################################