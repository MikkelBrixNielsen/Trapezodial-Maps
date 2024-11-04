import random
from objects import LineSegment, Trapezoid, Point
from SS import SearchStructure

def extract_points(linesegments):
    return [p for ls in linesegments for p in (ls.start, ls.end)]

def find_min_max(points):
    x_min, x_max, y_min, y_max = points[0].x, points[0].x, points[0].y, points[0].y
    for p in points: # could start at first index in points but thought this was more readable
        if p.x >= x_max:
            x_max = p.x
        elif p.x <= x_min:
            x_min = p.x

        if p.y >= y_max:
            y_max = p.y
        elif p.y <= y_min:
            y_min = p.y

    return x_min, x_max, y_min, y_max

def create_bounding_box(linesegments):
    x_min, x_max, y_min, y_max = find_min_max(extract_points(linesegments))
    # make bounding box slightly larger than found coordinates 
    x_min, x_max, y_min, y_max = x_min - 1, x_max + 1, y_min - 1, y_max + 1
    # create bounding box trapezoid
    upper = LineSegment(x_min, y_max, x_max, y_max) # Top line 
    lower = LineSegment(x_min, y_min, x_max, y_min) # Bottom line
    return Trapezoid(upper, lower, Point(x_min, y_min), Point(x_max, y_max)) # upper, lower, left, right boundary for trapezoid

def generate_random_perm(linesegments):
    return random.sample(linesegments, len(linesegments))

def initialization(linesegments):
    BB, perm = create_bounding_box(linesegments), generate_random_perm(linesegments)
    SS = SearchStructure(BB)
    return [BB], SS, perm

def BTM(linesegments, debug=False):
    TM, SS, queue = initialization(linesegments)



    for s in queue:
        SS.insert(s)

    return TM, SS
