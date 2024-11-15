from objects import Trapezoid, LineSegment, Point

class Node:
    def __init__(self, data=None, left=None, right=None):
        self.data = data # Can be region, line segment or point
        self.left = left # Left / above
        self.right = right # Right / below

    # overwrites this node with the data from another node
    def overwrite(self, data, left, right):
        self.data = data
        self.left = left
        self.right = right

    def print(self):
        print(f"Node(\n\tdata: {self.data}\n\t left: {self.left}\n\t right: {self.right})")

class SearchStructure:
    def __init__(self, BB):
        self.root = Node(BB)

    # find next neighbor in regards to s_i
    def _next_neighbour(self, region, seg):
        if not region.data.rightN:
            return None
        elif len(region.data.rightN) == 2: # current region has 2 neighbours
            region = region.data.rightN[0] if self._is_below(region.data.rightp, seg) else region.data.rightN[1]
        else: # else it has 1 neighbor
            region = region.data.rightN[0]
        return region # Returns the node of the region

    def _follow_segment(self, node, seg) -> list[Node]:
        regions = []
        region = node
        # appends delta_0 -> delta_k-1 - these regions are intersected by s_i
        while region and (not seg.end.x < region.data.leftp.x): # and (seg.end.x > region.rightp.x or (seg.end > region.leftp and seg.end < region.rightp)):
            regions.append(region)
            region = self._next_neighbour(region, seg)
        return regions

    def _fix_neighbours(self, left, right, is_above):
        if is_above:
            left.data.rightN = [right]
            right.data.leftN[1] = left
        else:
            left.data.rightN = [right]
            right.data.leftN[0] = left

    # Tries to merge delta_i with delta_i+1 and returns the trapezoid to continue to try and merge delta_i+2 and so on         
    def _merge_above_aux(self, node, left_region_node, right_region_node):
        # merging/making trapezoids above/below the segment
        left_region, right_region = left_region_node.data, right_region_node.data
        if left_region.upper == right_region.upper:
            left_region.rightp = right_region.rightp
            node.left = left_region_node
            return left_region_node
        else: # if not merging with B save current as trapezoid as below as well as the next trapezoid to try and merge with
            node.left = right_region_node
            self._fix_neighbours(left_region_node, right_region_node, is_above=True)
            return right_region_node
    
    # same as _merge_above_aux but checks lower defining line segment 
    def _merge_below_aux(self, node, left_region_node, right_region_node):
        left_region, right_region = left_region_node.data, right_region_node.data
        if left_region.lower == right_region.lower:
            left_region.rightp = right_region.rightp
            node.right = left_region_node 
            return left_region_node
        else:
            node.right = right_region_node
            self._fix_neighbours(left_region_node, right_region_node, is_above=False)
            return right_region_node

    def _merge_trapezoids(self, node, left_region_node, right_region_node, is_above):
        if is_above:
            return self._merge_above_aux(node, left_region_node, right_region_node)
        else:
            return self._merge_below_aux(node, left_region_node, right_region_node)

    def _create_trapezoids_first(self, node, trap, seg_node, seg):
        # Make three new trapezoids (for delta_0 aka first trapezoid)
        A = Node(Trapezoid(trap.upper, trap.lower, trap.leftp, seg.start, leftN=trap.leftN))
        B = Node(Trapezoid(trap.upper, seg, seg.start, trap.rightp, leftN=[A]))
        C = Node(Trapezoid(seg, trap.lower, seg.start, trap.rightp, leftN=[A]))
        A.rightN = [B, C]

        # NOTE - MIGHT BE NEEDED, MIGHT BE REDUNDANTD, TBD 
        # ASSIGN RIGHT NEIGHBOURS TO B AND C BASED ON SEGMENT POSITION AND NEIGHBOURS OF delta_i ("trap")
        if trap.rightN and len(trap.rightN) == 2:
            if self._is_below(trap.rightp, seg): # right point of delta_i is below the inserted segment, so "C" gets both right neighbours
                C.data.rightN = trap.rightN
                B.data.rightN = [trap.rightN[0]]
            else: # right point of delta_i is above the inserted segment, so "B" gets both right neighbours
                B.data.rightN = trap.rightN
                C.data.rightN = [trap.rightN[1]]
        else:
            C.data.rightN = B.data.rightN = trap.rightN

        # Rearrange accoringly in SS for p
        node.overwrite(seg.start, A, seg_node) # change delta_0 node to P
        return B, C

    def _create_trapezoids_last(self, node, trap, seg_node, seg):
        # Make three new trapezoids (for delta_k aka last trapezoid)
        A = Node(Trapezoid(trap.upper, trap.lower, seg.end, trap.rightp, rightN=trap.rightN))
        B = Node(Trapezoid(trap.upper, seg, trap.leftp, seg.end, rightN=[A]))
        C = Node(Trapezoid(seg, trap.lower, trap.leftp, seg.end, rightN=[A]))
        A.leftN = [B, C]

        # ASSIGN LEFT NEIGHBOURS TO B AND C BASED ON SEGMENT POSITION AND NEIGHBOURS OF delta_k ("trap")
        if trap.leftN and len(trap.leftN) == 2:
            if self._is_below(trap.leftp, seg): # left point of delta_k is below the inserted segment, so "C" gets both left neighbours
                C.data.leftN = trap.leftN
                B.data.leftN = [trap.leftN[0]]
            else: # left point of delta_k is above the inserted segment "B" gets both left neighbours
                B.data.leftN = trap.leftN
                C.data.leftN = [trap.leftN[1]]
        else:
            C.data.leftN = B.data.leftN = trap.leftN

        # Rearrange accoringly in SS for q
        node.overwrite(seg.end, seg_node, A) # change delta_k node to Q
        return B, C
    
    def _create_trapezoids(self, node, seg_node, trap, is_first):
        B, C = None, None
        if is_first:
            B, C = self._create_trapezoids_first(node, trap, seg_node, seg_node.data)
        else: 
            B, C = self._create_trapezoids_last(node, trap, seg_node, seg_node.data)
        seg_node.left = B # above
        seg_node.right = C # below
        return B, C

    def insert(self, seg, debug=False):
        node = self._find_region(seg.start) # get region for point (delta_0) - Trapezoid is node.data
        seg_node = Node(seg) # create node for the segment s_i
        traps = self._follow_segment(node, seg) # traps is a list of nodes of the trapezoids which follow s_i

        if len(traps) > 1:
            print("case s_i intersects multiple trapezoids")
            B, C = B_first, C_first = self._create_trapezoids(node, seg_node, traps[0].data, is_first=True) # delta_0
            B_last, C_last = self._create_trapezoids(node, seg_node, traps[-1].data, is_first=False) # delta_k

            # Iteratively handle the middle traps
            for trap in traps[1:-1]: # if it helps; "trap" is the same as "delta_i"
                current = trap.data # trapezoid 
                trap.data = seg # node now representing segment s_i

                # split current trapezoid 
                above = Node(Trapezoid(current.upper, seg, current.leftp, current.rightp))
                below = Node(Trapezoid(seg, current.lower, current.leftp, current.rightp))

                # Trying to merge the delta_i and delta_i+1 above and below the segment
                B = self._merge_trapezoids(trap, B, above, is_above=True)
                C = self._merge_trapezoids(trap, C, below, is_above=False)
            B_first, C_first = B, C # Not actually "first", just variables used to save "previous", i.e., "current"
                
            # Trying to merge the second to last and last trapezoid above and below the segment


            # NOTE eller FIXME - THIS IS BROKEN !!! FIRST PRIORITY !!! FIX THIS PLEASE !!! XXX !!!
            B = self._merge_trapezoids(B_last, B_first, B_last, is_above=True) # B_first == B_"current"
            C = self._merge_trapezoids(C_last, C_first, C_last, is_above=False) # C_first == C_"current"



        else: # traps <= 1, so entire segment is contained within a single trapezoid / region
            print("case s_i intersects single trapezoid")
            # Trapezoid border data
            upper = node.data.upper
            lower = node.data.lower
            leftp = node.data.leftp
            rightp = node.data.rightp

            # Make the trapezoids that should replace the previous one and assign neighbours
            A = Node(Trapezoid(upper, lower, leftp, seg.start, leftN=node.data.leftN))
            B = Node(Trapezoid(upper, lower, seg.end, rightp, rightN=node.data.rightN))
            C = Node(Trapezoid(upper, seg, seg.start, seg.end, rightN=[B], leftN=[A]))
            D = Node(Trapezoid(seg, lower, seg.start, seg.end, rightN=[B], leftN=[A]))
            A.data.rightN = [C, D]
            B.data.leftN = [C, D]
            
            # rearrange SS structure to reflect that trapezoids A, B, C, D has replaced delta_0
            node.data = seg.start # change delta_0 -> p_i

            # set p_i's left and right child 
            node.left = A 
            node.right = q_node = Node(seg.end)

            # set q_i's left and right child
            q_node.left = seg_node
            q_node.right = B

            # set s_i left and right child
            seg_node.left = C
            seg_node.right = D
           
        print(f"#traps: {len(traps)}")
            
    # Find the region in which the given point is contained by querying the search structure
    def _find_region(self, point):
        current = self.root # node
        while not isinstance(current.data, Trapezoid):
            print(current.data.__class__.__name__)
            data = current.data
            if isinstance(data, Point):
                if point.x > data.x:
                    current = current.right
                else:
                    current = current.left
            elif isinstance(data, LineSegment):
                if self._is_below(point, data):
                    current = current.right
                else:
                    current = current.left

        return current # node with the trapezoide containing query point
    
    # O(1) since it's just some calculations no loops and such
    def _is_below(self, p, seg):
         # Calculate the cross product of vectors (seg.start -> seg.end) and (seg.start -> p)
        cross_product = ((seg.end.x - seg.start.x) * (p.y - seg.start.y) - 
                     (seg.end.y - seg.start.y) * (p.x - seg.start.x))
        if cross_product == 0:
            return False
        return cross_product < 0 # Negative cross product -> p is to the right of seg -> p is below

    def _get_TM_aux(self, current):
        if not (current.left and current.right): # has no left or right children => is leaf => trapezoid
            return [current.data] # extracts trapezoid from node
        else:
            return self._get_TM_aux(current.left) + self._get_TM_aux(current.right)

    def get_TM(self):
        print(f"#traps in trapmap: {len(self._get_TM_aux(self.root))}")
        return self._get_TM_aux(self.root)
    

# FIXME: ENSURE THE CORRECTNESS OF GET_TM
# FIXME: ENSURE SIDE EFFECTS ARE ACUALLY TAKING PLACE 
# FIXME: GO THROUGH INSERT TO MAKE SURE IT ACTUALLY DOES WHAT IT IS SUPPOSED TO DO
# FIXME: CHECK NEIGHBOURS FOR TRAPEZOIDS
# FIXME: ENSURE THAT TRAPEZOIDS ARE MADE WITH REGARDS TO EXISTING TRAPEZOIDS