from objects import Trapezoid, LineSegment, Point

class Node:
    def __init__(self, data=None, left=None, right=None):
        self.data = data # Can be region, line segment or point
        self.left = left # Left / above
        self.right = right # Right / below

class SearchStructure:
    def __init__(self, BB):
        self.root = Node(BB)

    # find next neighbor in regards to s_i
    def _next_neighbour(self, region, seg):
        if len(region.rightN) == 2: # current region has 2 neighbours
            region = region.rightN[0] if self._is_below(region.rightp, seg) else region.rightN[1]
        else: # else it has 1 neighbor
            region = region.rightN[0]
        return region.data

    def _follow_segment(self, node, seg):
        regions = [node.data] # appends delta_0 - this region contains p
        region = self._next_neighbour(node.data, seg)

        while seg.end.x > region.rightp.x: # appends delta_1 -> delta_k-1 - these regions are intersected by s_i
            regions.append(region)
            region = self._next_neighbour(region, seg)
        
        regions.append(region) # last region - this region contains q (appends delta_k)

        return regions

    def insert(self, seg):
        # New nodes
        node = self._find_region(seg.start) # get region for point (Delta_0) - Trapezoid is node.data
        q_node = Node(seg.end)
        seg_node = Node(seg)
        
        # Trapezoid border data
        upper = node.data.upper
        lower = node.data.lower
        leftp = node.data.leftp
        rightp = node.data.rightp  

        xs = self._is_below(seg.end, upper) and not self._is_below(seg.end, lower) and leftp < seg.end < rightp # FIXME: remove this 
        # CASE WHERE ENTIRE LINE SEGMENT IS not CONTAINED WITHIN A SINGLE REGION/TRAPEZOID
        if not xs: # if not the case below???
            traps = self._follow_segment(node, seg)
            
            first, last = traps[0], traps[:-1]
            # handle first and last traps
            B = seg_node.left = Node(Trapezoid(upper, seg, seg.start, first.rightp)) # Creates B 
            first.rightp = seg.start # Change delta_0's rightp to seg start => A
            C = seg_node.right = Node(Trapezoid(seg, lower, seg.start, self._next_neighbour(first, seg).rightp))




            # Iteratively handle the middle traps
            for trap in traps[1:-1]:
                pass # do the merge thing and the new traps

        
        # CASE WHERE ENTIRE LINE SEGMENT IS CONTAINED WITHIN A SINGLE REGION/TRAPEZOID
        elif self._is_below(seg.end, upper) and not self._is_below(seg.end, lower) and leftp < seg.end < rightp:
            # Make Trapezoid and assign to p_i.left (A)
            A = node.left = Node(Trapezoid(upper, lower, leftp, seg.start))
            node.right = q_node
            
            # Make Trapezoid and assign to q_i.right (B)
            B = q_node.right = Node(Trapezoid(upper, lower, seg.end, rightp))
            q_node.left = seg_node

            # Make and assign upper (C) and lower (D) Trapezoid to s_i children
            C = seg_node.left = Node(Trapezoid(upper, seg, seg.start, seg.end))
            D = seg_node.right = Node(Trapezoid(seg, lower, seg.start, seg.end))

            #FIXME - ASSIGN TRAPEZOID NEIGHBORS - THIS FOLLOWS THE EXAMPLE ON FIGURE 6.7 - NEIGHBORS ARE NODES NOT REGIONSA
            A.data.leftN = node.data.leftN
            A.data.rightN = [C, D]  # THIS POINT TO NODES CONTAINING TRAPEZOID C AND D
            B.data.leftN = [C, D] 
            B.data.rightN = node.data.rightN
            C.data.leftN = [A]
            C.data.rightN = [B]
            D.data.leftN = [A]
            D.data.rightN = [B]
            
    # Find the region in which the given point is contained by querying the search structure
    def _find_region(self, point):
        current = self.root
        while not isinstance(current.data, Trapezoid):
            print(current.data.__class__.__name__)
            if isinstance(current.data, Point):
                if point.x > current.data.x:
                    current = current.right
                else:
                    current = current.left
            elif isinstance(current.data, LineSegment):
                if self._is_below(point, current.data):
                    current = current.right
                else:
                    current = current.left
        return current
    
    # O(1) since it's just some calculations no loops and such
    def _is_below(self, p, seg):
         # Calculate the cross product of vectors (seg.start -> seg.end) and (seg.start -> p)
        cross_product = ((seg.end.x - seg.start.x) * (p.y - seg.start.y) - 
                     (seg.end.y - seg.start.y) * (p.x - seg.start.x))
        if cross_product == 0: 
            # If point is collinear to the line or its extension, it is either illegal 
            # OR guaranteed to be outside of the region anyway
            return False
        return cross_product < 0 # Negative cross product -> p is to the right of seg -> p is below