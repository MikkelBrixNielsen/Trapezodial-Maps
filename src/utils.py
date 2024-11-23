import sys
import os
import re
import matplotlib.pyplot as plt
from objects import LineSegment, Point
from algorithm import BTM, print_borders, print_border

# Checks if program is called with correct parameters
# Returns '-d' in sys.argv, '-p' in sys.argv, '-o' in sys.argv, file_name
def check_usage():
    usage_str = "Usage: python ./src/main.py [optional -d -p -o] <file_name/path>"
    # Ensure there's at least one argument (the file name)
    if len(sys.argv) < 2:
        print(usage_str)
        sys.exit(1)

    for option in sys.argv[1:-1]:
        if option not in ['-d', '-p', '-o']:
            print(f"Option '{option}' is not a valid option")
            print(usage_str)
            sys.exit(1)

    # Extract the options
    d_flag = '-d' in sys.argv # debug flag
    p_flag = '-p' in sys.argv # plot result flag
    o_flag = '-o' in sys.argv # output result to text file flag

    # Extract file name ensuring it is provided
    # file_name should be the last argument after any options
    file_name = sys.argv[-1]
    
    if not os.path.exists(file_name):
        print("Error: File name is missing or invalid.")
        print(usage_str)
        sys.exit(1)

    return d_flag, p_flag, o_flag, file_name

def get_content(file_name): # O(n)
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

def try_float_cast(d):
    try:
        return float(d)
    except ValueError:
        print(f"Error: Could not convert '{d}' to float, maybe a formatting issue in input file.")
        sys.exit(1)

def format_content(content): # O(n)
    fcontent = re.sub(r'[\t ]+', ' ', content.strip())
    fcontent = fcontent.split("\n")
    fcontent = [l.strip() for l in fcontent]
    return [[try_float_cast(d) if not d == '' and not d == '-' else d for d in l.split(" ")] for l in fcontent]
    
def check_output(point, line_segments): # O(1)
    if not point:
        print("Error: No point provided in input file.")
        sys.exit(1)
    if not line_segments:
        print("Error: No line segments provided in input file.")
        sys.exit(1)

# O(1) since just comparisons
def determine_endpoint(p, q):
    if p[0] < q[0]: 
        return p, q     # start point is smallest x
    elif p[0] > q[0]:
        return q, p     # start point is smallest x
    else:   # both points have same x-value (vertical line segment)
        if p[1] > q[1]:
            return p, q     # start point is largest y
        elif p[1] < q[1]:
            return q, p     # start point is largest y
        else:
            print("Error: Multiple points with identical coordiantes defined in input file.")
            sys.exit(1)

def create_line_segments_and_point(content): # O(n)
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
            start, end = determine_endpoint((elem[0], elem[1]), (elem[2], elem[3]))
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

def write_to_file(point, region, line_segments, T, D):
    with open("output.txt", "w") as file:
        display_plot(point, line_segments, T, save=True) # saves plot as a png
        output_string = 151*"-" + f"\nThe query point: {point} lies within: {region.data.label}\n" + 151*"-" + "\n\n" + 60*"-" + "The resulting search structure:" + 60*"-" + f"\n{D.to_string(D.root)}\n" + 151*"-"
        file.write(output_string)

def run_algorithm(point, line_segments, show_plot=False, write_result_to_file=False, debug=False):
    # runs the algorithm resulting in a trapezodial map, T, and a search structure, D.
    T, D = BTM(point, line_segments, debug)

    # Query search structure
    region = D._find_region(point)
    if debug:
        print("\n")
        print_border()
        print(72*" " + "RESULTS" + 72*" ")
        print_borders(print, f"The query point: {point} lies within {region.data.label}:\n\n{str(region.data).strip()}") # prints the trapezoid the point is located in 

    # if wanted writes output to file 
    if write_result_to_file:
        write_to_file(point, region, line_segments, T, D)

    # if wanted displays plot of trapazoid map
    if show_plot:
        display_plot(point, line_segments, T) # O(n)

# displays a plot given a point and some line segments
def display_plot(point, line_segments, T, save=False): # O(n)
    # plots the point
    point.plot("q") # O(1)

    # plots all line segments
    for line in line_segments: # O(n)
        line.plot()

    # plots all trapezoids
    for trap in T: # O(n)
        trap.plot()
    
    # lables for x and y axis
    plt.xlabel("X-axis")
    plt.ylabel("Y-axis")

    # save plot if wanted
    if save:
        plt.savefig("TrapezoidalMapPlot.png")
    else: # displays plot
        plt.show()