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

class SearchStructure:
    def __init__(self, BB):
        self.root = Node(BB)

    # find next neighbor in regards to s_i
    def _next_neighbour(self, region, seg):
        if len(region.data.rightN) == 2: # current region has 2 neighbours
            region = region.data.rightN[0] if self._is_below(region.data.rightp, seg) else region.data.rightN[1]
        else: # else it has 1 neighbor
            region = region.data.rightN[0]
        return region # Returns the node of the region

    def _follow_segment(self, node, seg):
        regions = [node] # appends delta_0 - this region contains p
        region = self._next_neighbour(node, seg) 

        while seg.end.x > region.rightp.x: # appends delta_1 -> delta_k-1 - these regions are intersected by s_i
            regions.append(region)
            region = self._next_neighbour(region, seg)
        
        regions.append(region) # last region - this region contains q (appends delta_k)

        return regions

    def insert(self, seg):
        node = self._find_region(seg.start) # get region for point (delta_0) - Trapezoid is node.data
        q_node = Node(seg.end)
        seg_node = Node(seg)

        # FIXME: remove this
        xs = self._is_below(seg.end, node.data.upper) and not self._is_below(seg.end, lower) and leftp < seg.end < rightp 
        
        # CASE WHERE ENTIRE LINE SEGMENT IS not CONTAINED WITHIN A SINGLE REGION/TRAPEZOID
        if not xs: # if not the case below???
            traps = self._follow_segment(node, seg) # traps is a list of nodes of regions

            first, last = traps[0].data, traps[:-1].data # delta_0 and delta_k
            # Make three new trapezoids (for delta_0 aka first trapezoid) - FIXME: DONE MAYBE?
            Ap = Node(Trapezoid(first.upper, first.lower, first.leftp, seg.start))
            Bp = Node(Trapezoid(first.upper, seg, seg.start, first.rightp)) # upper and rightp from delta_0, lower is segment, leftp is start of segment
            Cp = Node(Trapezoid(seg, first.lower, seg.start, first.rightp)) # lower and rightp from delta_0, upper is segment, leftp is start of segment

            # Rearrange accoringly in SS for p
            node.overwrite(seg.start, Ap, seg_node) # change delta_0 node to P
            seg_node.left = Bp # above
            seg_node.right = Cp # below

            # Make three new trapezoids (for delta_k aka last trapezoid) - FIXME: DONE MAYBE?
            Aq = Node(Trapezoid(last.upper, last.lower, seg.end, last.rightp))
            Bq = Node(Trapezoid(last.upper, seg, last.leftp, seg.end)) # upper and leftp from delta_k, lower is segment, rightp is end of segment
            Cq = Node(Trapezoid(seg, last.lower, last.leftp, seg.end)) # lower and leftp from delta_k, upper is segment, rightp is end of segment 

            # Rearrange accoringly in SS for q
            node.overwrite(seg.end, seg_node, Aq) # change delta_k node to Q
            seg_node.left = Bq # above
            seg_node.right = Cq # below

            # Iteratively handle the middle traps
            for trap in traps[1:-1]: # if it helps; "trap" is the same as "delta_i"
                B, C = Bp, Cp # starting trapezoid to try and merge with the next trapezoids
                current = trap.data
                trap.data = seg
                # split current trapezoid 
                above = Trapezoid(current.upper, seg, current.leftp, current.rightp)
                below = Trapezoid(seg, current.lower, current.leftp, current.rightp)
                # merging/making trapezoids above/below the segment
                if B.upper == above.upper:
                    B.rightp = above.rightp # merge B with next region above the segment - "above" dies
                    current.upper = seg
                    trap.left = B
                else: # if not merging with B save current as trapezoid as below as well as the next trapezoid to try and merge with
                    B = trap.left = current
                    
                if C.lower == below.lower:
                    C.rightp = below.rightp # merge C with next region below the segment - "below" dies
                    current.lower = seg
                    trap.right = C
                else: # if not merging with C save current as trapezoid as below as well as the next trapezoid to try and merge with
                    C = trap.right = current

            
            

                # NOTE - REMEMBER TO MERGE WITH Bq AND Cq AFTER DOING THE MIDDLE STUFF
                # NOTE - REMEMBER TO ADD NEIGHBOUR-RELATIONS TO TRAPEZOIDS





        # FIXME - ABSTRACT THIS TO "SIGNLE_TRAP_INSERTION(...)"
        # CASE WHERE ENTIRE LINE SEGMENT IS CONTAINED WITHIN A SINGLE REGION/TRAPEZOID
        elif self._is_below(seg.end, node.data.upper) and not self._is_below(seg.end, lower) and leftp < seg.end < rightp:
            # Trapezoid border data
            upper = node.data.upper
            lower = node.data.lower
            leftp = node.data.leftp
            rightp = node.data.rightp  
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