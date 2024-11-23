import random
from objects import LineSegment, Trapezoid, Point
from SS import SearchStructure
import matplotlib.pyplot as plt

BB = None
DEBUG = False

################################################### DEBUG METHODS ##################################################
def print_border():
    print(151 * "-")
    
def print_borders(method, arg):
    print_border()
    method(arg)
    print_border()

def print_queue_aux(queue):
    for q in queue:
        print(q)

def print_queue(queue):
    print_borders(print_queue_aux, queue)

def print_SS_aux(SS):
    traps = SS.get_TM()
    BB.plot()
    for t in traps:
        print(t)
        t.plot()
    plt.show()

def print_each_trap(SS):
    traps = SS.get_TM()
    for t in traps:
        print(t)
        t.plot()
        BB.plot()
        plt.show()

def print_SS(SS):
    print_borders(print_SS_aux, SS)

def display_SS(SS):
    SS.show()

def print_queue_and_SS(queue, SS):
    print_border()
    print("Queue after initialization:")
    print_queue_aux(queue)
    print_border()
    print("TM after initialization:")
    print_SS_aux(SS)
    print_border()

def plot_line_segments(segments):
    for seg in segments:
        seg.plot()
    BB.plot()
    plt.show()

def print_order_aux(line_segments):
    print("The order the line segments were inserted:")
    for i in range(len(line_segments)):
        print(f"{i}: {line_segments[i]}")

def print_order(line_segments):
    print()
    print_borders(print_order_aux, line_segments)
##################################################################################################################

def extract_points(linesegments):
    return [p for ls in linesegments for p in (ls.start, ls.end)]

def find_min_max(points):
    x_min, x_max, y_min, y_max = points[0].x, points[0].x, points[0].y, points[0].y
    for p in points:
        if p.x >= x_max:
            x_max = p.x
        elif p.x <= x_min:
            x_min = p.x

        if p.y >= y_max:
            y_max = p.y
        elif p.y <= y_min:
            y_min = p.y

    return x_min, x_max, y_min, y_max

def create_bounding_box(point, linesegments):
    x_min, x_max, y_min, y_max = find_min_max(extract_points(linesegments))
    x_min, x_max = min(x_min, point.x), max(x_max, point.x)
    y_min, y_max = min(y_min, point.y), max(y_max, point.y)
    # make bounding box slightly larger than found coordinates 
    x_min, x_max, y_min, y_max = x_min - 1, x_max + 1, y_min - 1, y_max + 1
    # create bounding box trapezoid
    upper = LineSegment(x_min, y_max, x_max, y_max) # Top line 
    lower = LineSegment(x_min, y_min, x_max, y_min) # Bottom line
    return Trapezoid(upper, lower, Point(x_min, y_min), Point(x_max, y_max)) # upper, lower, left, right boundary for trapezoid

def generate_random_perm(linesegments):
    return random.sample(linesegments, len(linesegments))

def initialization(point, linesegments):
    global BB
    BB, perm = create_bounding_box(point, linesegments), generate_random_perm(linesegments)
    SS = SearchStructure(BB)
    return SS, perm

def BTM(point, linesegments, debug=False):
    global DEBUG
    DEBUG = debug
    order = [] # for debugging    
    SS, queue = initialization(point, linesegments)
    if DEBUG:
        print_border()
        #plot_line_segments(linesegments)
        # print_queue_and_SS(queue, SS)
        print("Before any insertion (bounding box):")
        display_SS(SS)
        print_border()


    for s in queue:
        if DEBUG:
            print(f"Inserting line segment {s}...")
            order.append(s)
        SS.insert(s, debug)
        if DEBUG:
            #print_SS(SS)
            # print_each_trap(SS)
            print("-"*151)


    if DEBUG:
        # print_SS(SS)
        print_order(order)

    return SS.get_TM(), SS
