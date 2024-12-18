import sys
import os
import re
import matplotlib.pyplot as plt
from objects import LineSegment, Point
from SS import SearchStructure, Node, Trapezoid
from algorithm import build_TM_and_SS, print_borders, print_border

############################################################################# DEBUG METHODS #############################################################################
def print_results(point: Point, region: Node[Trapezoid]):
        print("\n")
        print_border()
        print(72*" " + "RESULTS" + 72*" ")
        print_borders(print, f"The query point: {point} lies within {region.data.label}:\n\n{str(region.data).strip()}") # prints the trapezoid the point is located in 
#########################################################################################################################################################################

# Checks if program is called with correct parameters
# Returns '-d' in sys.argv, '-p' in sys.argv, '-o' in sys.argv, '-qo' in sys.argv, file_name
def check_usage():
    usage_str = "Usage: python ./src/main.py [optional -d -p -o -qo] <file_name/path>"
    # Ensure there's at least one argument (the file name)
    if len(sys.argv) < 2:
        print(usage_str)
        sys.exit(1)

    for option in sys.argv[1:-1]:
        if option not in ['-d', '-p', '-o', '-qo']:
            print(f"Option '{option}' is not a valid option")
            print(usage_str)
            sys.exit(1)

    # Extract the options
    d_flag = '-d' in sys.argv # debug flag
    p_flag = '-p' in sys.argv # plot result flag
    o_flag = '-o' in sys.argv # output result, search structure to output.txt and create image of trapezodal map in TrapezoidalMapPlot.png
    qo_flag = '-qo' in sys.argv # output only the query result to output.txt no search structure or image

    # Extract file name ensuring it is provided
    # file_name should be the last argument after any options
    file_name = sys.argv[-1]
    
    if not os.path.exists(file_name):
        print("Error: File name is missing or invalid.")
        print(usage_str)
        sys.exit(1)

    return d_flag, p_flag, o_flag, qo_flag, file_name

def get_content(file_name: str): # O(n)
    content = ""
    try:
        with open(file_name, 'r') as file:
            content = file.read()
    except FileNotFoundError:
        print(f"Error: File '{file_name}' not found.")
        sys.exit(1)
    if not content:
        print(f"Error: File '{file_name}' is empty.")
        sys.exit(1)
    return content

def try_float_cast(d: int | float):
    try:
        return float(d)
    except ValueError:
        print(f"Error: Could not convert '{d}' to float, maybe a formatting issue in input file.")
        sys.exit(1)

def format_content(content: str): # O(n)
    fcontent = re.sub(r'[\t ]+', ' ', content.strip())
    fcontent = fcontent.split("\n")
    fcontent = [l.strip() for l in fcontent]
    return [[try_float_cast(d) if not d == '' and not d == '-' else d for d in l.split(" ")] for l in fcontent]
    
def check_output(point: Point, line_segments: LineSegment): # O(1)
    if not point:
        print("Error: No point provided in input file.")
        sys.exit(1)
    if not line_segments:
        print("Error: No line segments provided in input file.")
        sys.exit(1)

# O(1) since just comparisons
def determine_endpoint(p, q, linenum):
    if p[0] < q[0]: 
        return p, q     # start point is smallest x
    elif p[0] > q[0]:
        return q, p     # start point is smallest x
    else:
        print(f"Error: Vertical line defined on line {linenum} in input file.")
        sys.exit(1)
    
    if p[1] > q[1]:
        return p, q     # start point is largest y
    else:
        return q, p     # start point is largest y

def create_line_segments_and_point(content: str): # O(n)
    linenum = 1
    point = None
    line_segments = []
    for elem in content: # O(n) elements
        num_coords = len(elem)
        if not point and num_coords == 2:
            if linenum != 1:
                print("Error: The point is not defined first in input file.")
                sys.exit(1)
            # Creates a point Point(x, y)
            point = Point(elem[0], elem[1])
        elif num_coords == 2: # tries to create a point buy one already exists
            print(f"Error: Multiple points defined in input file, line {linenum}.")
            sys.exit(1)
        elif num_coords == 4:
            # finds start and endpoint for a line segment
            start, end = determine_endpoint((elem[0], elem[1]), (elem[2], elem[3]), linenum)
            # Creates line segment LineSegment(x1, y1, x2, y2)
            line_segments.append(LineSegment(*start, *end))
        else: # something neither a point nor a line segment was defined in input
            expected = 4 if linenum > 1 else 2
            elems = ''.join("\'" + str(e) + "\'" + ", " for e in elem).strip()[:-1]
            num_coords = 0 if num_coords == 1 and elem[0] == '' else num_coords
            print(f"Error: Line {linenum} in input file was not formatted correctly, " +
                  f"was expecting {expected} coordinates but recieved {num_coords} ({elems}).")
            sys.exit(1)
        linenum += 1
    check_output(point, line_segments) # O(1)
    return point, line_segments  

def write_to_file(point: Point, region: Node[Trapezoid], line_segments: LineSegment, T: list[Node[Trapezoid]], D: SearchStructure, query_only:bool=False): # O(n) if not query_only else O(1)
    with open("output.txt", "w") as file:
        output_string = ""
        if not query_only: # O(n)
            display_plot(point, region, line_segments, T, save=True) # saves plot as a png  --- O(n)
            output_string = 151*"-" + f"\nThe query point: {point} lies within: {region.data.label}\n\n{region.data}\n" + 151*"-" + "\n\n" + 60*"-" + "The resulting search structure:" + 60*"-" + f"\n{D.to_string(D.root)}\n" + 151*"-"
        else: # O(1)
            output_string = 151*"-" + f"\nThe query point: {point} lies within: {region.data.label}\n\n{region.data}\n" + 151*"-"
        file.write(output_string)

# displays a plot given a point and some line segments
def display_plot(point: Point, region: Node[Trapezoid], line_segments: LineSegment, T: list[Node], save=False): # O(n)
    # plots almost all trapezoids
    for trap in T: # O(n) by theorem 6.3 assuming the implementation is correct and follows the book 
        if not (trap == region.data):
            trap.plot()
    
    # plots all line segments
    for line in line_segments: # O(n)
        line.plot(lw=2)

    # plots region point is located in
    # plots the point
    point.plot("q", "blue", label_x=5,label_y=5) # O(1)
    region.data.plot() # O(1)
    
    # lables for x and y axis
    plt.xlabel("X-axis")
    plt.ylabel("Y-axis")

    # save plot if wanted
    if save:
        plt.savefig("TrapezoidalMapPlot.png")
    else: # displays plot
        plt.show()

def run_algorithm(point: Point, line_segments: LineSegment, show_plot:bool=False, write_result_to_file:bool=False, query_only:bool=False, debug:bool=False): # O_E(n log n)
    # runs the algorithm resulting in a trapezodial map, T, and a search structure, D.
    T, D = build_TM_and_SS(point, line_segments, debug) # O_E(n log n)

    # Query search structure
    region = D.query(point) # O_E(log n)

    if debug:
        print_results(point, region)

    # if wanted writes output to file 
    if write_result_to_file or query_only:
        write_to_file(point, region, line_segments, T, D, query_only) # O(n) if not query_only else O(1)

    # if wanted displays plot of trapazoid map
    if show_plot:
        display_plot(point, region, line_segments, T) # O(n)