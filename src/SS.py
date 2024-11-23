from objects import Trapezoid, LineSegment, Point
DEBUG = False

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

    def childless_copy(self):
        return Node(self.data)

    def print(self):
        print(f"Node(\n\tdata: {self.data}\n\t left: {self.left}\n\t right: {self.right})")

class SearchStructure:
    def __init__(self, BB):
        self.root = Node(BB)

    # O(1) since it's just some calculations no loops and such
    def _is_below(self, p, seg):
         # Calculate the cross product of vectors (seg.start -> seg.end) and (seg.start -> p)
        cross_product = ((seg.end.x - seg.start.x) * (p.y - seg.start.y) - 
                     (seg.end.y - seg.start.y) * (p.x - seg.start.x))
        if cross_product == 0:
            return False
        return cross_product < 0 # Negative cross product -> p is to the right of seg -> p is below

    # Find the region in which the given point is contained by querying the search structure
    def _find_region(self, point):
        current = self.root # node
        while not isinstance(current.data, Trapezoid):
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
        while region and (not seg.end.x < region.data.leftp.x):
            regions.append(region)
            region = self._next_neighbour(region, seg)
        return regions

    # Tries to merge delta_i with delta_i+1 and returns the trapezoid to continue to try and merge delta_i+2 and so on         
    def _merge_above_aux(self, left_region_node, right_region_node):
        # merging/making trapezoids above/below the segment
        left_region, right_region = left_region_node.data, right_region_node.data
        if left_region.upper == right_region.upper:
            left_region.rightp = right_region.rightp

            # THE NODE THAT CONTAINS RIGHT REGION IS SET TO CONTAIN LEFT REGION AS DATA, SO 
            # THINGS POINTING TO THAT NODE NOW EFFECTIVELY POINTS TO LEFT REGION INSTEAD OF RIGHT REGION AFTER MERGING
            right_region_node.data = left_region_node.data
            
            left_region.rightN = right_region.rightN # B GETS NEIGHBOURS OF ABOVE

            return left_region_node # RETURN B IF MERGING INTO ABOVE

        else:
            # SINCE IF NOT MERGING, EITHER LEFT_REGION OR RIGHT_REGION ALREADY HAS A NEIGHBOUR, WHICH IS 
            # THE REGION ABOVE RIGHT_REGION OR LEFT_REGION RESPECTIVELY. HENCE THAT REGION HAS EXACTLY ONE RIGHT OR LEFT NEIGHBOUR,
            # WHICH IS THEN OUTERMOST REGION STILL RELEVANTLY CLOSE TO THE INSERTED LINE SEGMENT.

            # if B has a right neighbour, it keeps it and gets ABOVE as well, otherwise it just gets ABOVE
            left_region.rightN = [left_region.rightN[0], right_region_node] if left_region.rightN else [right_region_node]
            # if ABOVE has a left neighbour, it keeps it and gets B as well, otherwise it just gets B
            right_region.leftN = [right_region.leftN[0], left_region_node] if right_region.leftN else [left_region_node]

            return right_region_node # RETURN ABOVE IF NO MERGE
    
    # same as _merge_above_aux but checks lower defining line segment
    def _merge_below_aux(self, left_region_node, right_region_node):
        left_region, right_region = left_region_node.data, right_region_node.data
        if left_region.lower == right_region.lower:
            left_region.rightp = right_region.rightp

            # THE NODE THAT CONTAINS RIGHT REGION IS SET TO CONTAIN LEFT REGION AS DATA, SO 
            # THINGS POINTING TO THAT NODE NOW EFFECTIVELY POINTS TO LEFT REGION INSTEAD OF RIGHT REGION AFTER MERGING
            right_region_node.data = left_region_node.data

            left_region.rightN = right_region.rightN # C GETS NEIGHBOURS OF BELOW

            return left_region_node # RETURN C IF MERGING INTO BELOW
        
        else:
            # SINCE IF NOT MERGING, EITHER LEFT_REGION OR RIGHT_REGION ALREADY HAS A NEIGHBOUR, WHICH IS 
            # THE REGION BELOW RIGHT_REGION OR LEFT_REGION RESPECTIVELY. HENCE THAT REGION HAS EXACTLY ONE RIGHT OR LEFT NEIGHBOUR,
            # WHICH IS THEN OUTERMOST REGION STILL RELEVANTLY CLOSE TO THE INSERTED LINE SEGMENT.

            # if C has a right neighbour, it keeps it and gets BELOW as well, otherwise it just gets BELOW
            left_region.rightN = [right_region_node, left_region.rightN[0]] if left_region.rightN else [right_region_node]
            # if BELOW has a left neighbour, it keeps it and gets C as well, otherwise it just gets C
            right_region.leftN = [left_region_node, right_region.leftN[0]] if right_region.leftN else [left_region_node]

            return right_region_node # RETURN BELOW IF NO MERGE

    def _merge_trapezoids(self, left_region_node, right_region_node, is_above):
        if is_above:
            return self._merge_above_aux(left_region_node, right_region_node)
        else:
            return self._merge_below_aux(left_region_node, right_region_node)

    def _create_trapezoids_first(self, trap, seg):
        # Make three new trapezoids (for delta_0 aka first trapezoid)
        A = Node(Trapezoid(trap.upper, trap.lower, trap.leftp, seg.start, leftN=trap.leftN))
        B = Node(Trapezoid(trap.upper, seg, seg.start, trap.rightp, leftN=[A]))
        C = Node(Trapezoid(seg, trap.lower, seg.start, trap.rightp, leftN=[A]))
        A.data.rightN = [B, C]

        if trap.rightN and len(trap.rightN) == 2:
            if not self._is_below(trap.rightp, seg): # trap.rightp is above segment
                trap.rightN[0].data.leftN = [B]
                B.data.rightN = [trap.rightN[0]]
            else: # trap.rightp is below segment
                trap.rightN[1].data.leftN = [C]
                C.data.rightN = [trap.rightN[1]]

        # rearrange delta_0's previous left neighbours to point to A
        if trap.leftN: # if trap being split by s_i has left neighbors
            for n in trap.leftN:
                if n.data.rightN and len(n.data.rightN) >= 2:
                    idx = 0 if n.data.rightN[0].data == trap else 1
                    n.data.rightN[idx] = A
                else: # only has one neighbour
                    n.data.rightN = [A]

        return A, B, C

    def _create_trapezoids_last(self, trap, seg):
        # Make three new trapezoids (for delta_k aka last trapezoid)
        A = Node(Trapezoid(trap.upper, trap.lower, seg.end, trap.rightp, rightN=trap.rightN))
        B = Node(Trapezoid(trap.upper, seg, trap.leftp, seg.end, rightN=[A]))
        C = Node(Trapezoid(seg, trap.lower, trap.leftp, seg.end, rightN=[A]))
        A.data.leftN = [B, C]

        # rearrange delta_k's previous neighbours to point to A
        if trap.rightN: # if trap being split by s_i has right neighbors
            for n in trap.rightN:
                if len(n.data.leftN) == 2:
                    idx = 0 if n.data.leftN[0].data == trap else 1
                    n.data.leftN[idx] = A
                else: # only has one neighbour
                    n.data.leftN = [A]

        if trap.leftN and len(trap.leftN) == 2:
            if not self._is_below(trap.leftp, seg): # leftp of trap is above seg
                trap.leftN[0].data.rightN = [B] # give the upper left neighbour of delta_k to B (the farthest relevant region from inserted segment)
                B.data.leftN = [trap.leftN[0]] # also the other way

            else: # leftp of trap is below seg
                trap.leftN[1].data.rightN = [C] # give the lower left neighbour delta_k to C (the farthest relevant region from inserted segment)
                C.data.leftN = [trap.leftN[1]] # also the other way

        return A, B, C
    
    def _create_trapezoids(self, seg, trap, is_first):
        if is_first:
            return self._create_trapezoids_first(trap, seg)
        else: 
            return self._create_trapezoids_last(trap, seg)
    
    # def _fix_neighbours(self, B_left, C_left, B_right, C_right):
    #     # assigns neigbhours to B_right and C_right - one has been given the outermost region prior 
    #     # (which depends on whether the segment is inserted above or below the leftp of delta_i)
    #     B_right.data.leftN = [B_right.data.leftN[0], B_left] if B_right.data.leftN else [B_left]
    #     C_right.data.leftN = [C_left, C_right.data.leftN[1]] if C_right.data.leftN else [C_left]

    #     # assigns the other way
    #     B_left.data.rightN = [B_left.data.rightN[0], B_right] if B_left.data.rightN else [B_right]
    #     C_left.data.rightN = [C_right, C_left.data.rightN[0]] if C_left.data.rightN else [C_right]

    def insert(self, seg, debug=False):
        global DEBUG
        DEBUG = debug
        print("INSERTING: ", seg)
        node = self._find_region(seg.start) # get region for point (delta_0) - Trapezoid is node.data
        #seg_node = Node(seg) # create node for the segment s_i
        traps = self._follow_segment(node, seg) # traps is a list of nodes of the trapezoids which follow s_i

        if len(traps) > 1:
            
            # Make three new trapezoids for delta_0
            A, B, C = self._create_trapezoids(seg, traps[0].data, is_first=True) # delta_0

            # Make three new trapezoids for delta_k
            A_last, B_last, C_last = self._create_trapezoids(seg, traps[-1].data, is_first=False) # delta_k

            # Update SS at delta_0
            traps[0].overwrite(seg.start, A, Node(seg, B, C)) # overwrite delta_0 with p and give children

            # Iteratively handle the middle traps FIXME 
            for trap in traps[1:-1]: # if it helps; "trap.data" is the same as "delta_i"
                current = trap.data # trapezoid 
                #trap.data = seg # node now representing segment s_i

                # split current trapezoid
                above = Node(Trapezoid(current.upper, seg, current.leftp, current.rightp))
                below = Node(Trapezoid(seg, current.lower, current.leftp, current.rightp))

                # if delta_i has two left neighbours
                if len(current.leftN) == 2:
                    if not self._is_below(current.leftp, seg): # if segment is inserted below the left-defining point of current
                        above.data.leftN = [current.leftN[0]]
                        current.leftN[0].data.rightN = [above]
                    else: # if segment is inserted above the left-defining point of current
                        below.data.leftN = [current.leftN[1]]
                        current.leftN[1].data.rightN = [below]
                # if delta_i has two right neighbours - FIXME - W.I.P
                if len(current.rightN) == 2:
                    if not self._is_below(current.rightp, seg): # if segment is inserted below the right-defining point of current
                        # Give above the outermost region (relative to the inserted segment) to above as right-neighbour
                        above.data.rightN = [current.rightN[0]] # this should result in above getting two right neighbours by _merge_trapezoids()
                        current.rightN[0].data.leftN = [above]
                    else: # if segment is inserted above the right-defining point of current
                        # Give above the outermost region (relative to the inserted segment) to below as right-neighbour
                        below.data.rightN = [current.rightN[1]] # this should result in below getting two right neighbours by _merge_trapezoids()
                        current.rightN[1].data.leftN = [below]


                # FIXME: THIS MIGHT BE REDUNDANT BUT IF NOT FIGURE OUT WHERE TO PLACE IT 
                #else: # In this case, current has one left nieghbour, and above/below hasn't been assigned any neighbours so is given B/C
                      # as leftN (respectively) by _fix_final_neighbours. Additionally, B or C will have been given the outmost neighbour
                      # of the prior region.
                    #self._fix_neighbours(B, C, above, below)
                    
                # Trying to merge the delta_i and delta_i+1 above and below the segment
                B = self._merge_trapezoids(B, above, is_above=True)
                if DEBUG:
                    self.show()
                C = self._merge_trapezoids(C, below, is_above=False)
                if DEBUG:
                    self.show()
                # B/C = IS EITHER MERGED INTO ABOVE/BELOW AND RETURNED OR NOT MERGED BUT REASSIGNED TO ABOVE/BELOW RESPECTIVELY
                trap.overwrite(seg, B, C) # TRAP_I GETS OVERWRITTEN AND IS GIVEN TWO CHILDREN BEING ABOVE+C OR B+BELOW DEPENDING ON HOW/WHERE MERGING IS DONE
            
            B = self._merge_trapezoids(B, B_last, is_above=True)
            C = self._merge_trapezoids(C, C_last, is_above=False)

            # Update SS at delta_k
            traps[-1].overwrite(seg.end, Node(seg, B, C), A_last) # overwrite delta_k with p

            #self.show()

        else: # traps <= 1, so entire segment is contained within a single trapezoid / region
            if DEBUG:
                print(f"case {seg} intersects single trapezoid")
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

            # FIXES NEIGHBOURS ON OUTSIDE POINTING IN TO HAVE A AND B INSTEAD OF DELTA_I, THE NODE OF WHICH IS NOW A POINT OBJECT
            # FIXME - VERIFY CORRECTNESS
            # NOTE: if node has two neighbours then it's left / right neighbours cannot have two neighbours in the same direction as node is
            # so if node is a left neighbour to its right neighbour then that cannot have two left neighbours.
            if node.data.leftN:
                if len(node.data.leftN) >= 2:
                    node.data.leftN[0].data.rightN = [A]
                    node.data.leftN[1].data.rightN = [A]
                else:
                    if node.data.leftN[0].data.rightN and len(node.data.leftN[0].data.rightN) >= 2:
                        idx = 0 if node.data.leftN[0].data.rightN[0] == node else 1
                        node.data.leftN[0].data.rightN[idx] = A # NOTE - i removed the brackets around A here btw idk
                    else:
                        node.data.leftN[0].data.rightN = [A]

            if node.data.rightN:
                if len(node.data.rightN) >= 2:
                    node.data.rightN[0].data.leftN = [B]
                    node.data.rightN[1].data.leftN = [B]
                else:
                    if node.data.rightN[0].data.leftN and len(node.data.rightN[0].data.leftN) >= 2:
                        idx = 0 if node.data.rightN[0].data.leftN[0] == node else 1
                        node.data.rightN[0].data.leftN[idx] = B # NOTE - i removed the brackets around B here btw idk
                    else:
                        node.data.rightN[0].data.leftN = [B]
            
            # rearrange SS structure to reflect that trapezoids A, B, C, D has replaced delta_0
            node.overwrite(seg.start, A, Node(seg.end, Node(seg, C, D), B))
            # node -->  p<(A, q)
            #           q<(s, B)
            #           s<(C, D)
            
           
        if DEBUG:
            print(f"#traps: {len(traps)}")
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
#########################################################################################################
