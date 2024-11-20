from utils import get_content, format_content, create_line_segments_and_point, check_usage, run_algorithm
DEBUG = None

def main():
    # Check if program is called with correct parameters returns debug_flag, plot_flag, write_flag, file_name
    DEBUG, show_plot, write_result_to_file, file_name  = check_usage() # O(1)
    # Gets content from file specified by call parameter 
    content = get_content(file_name) # O(n)
    # Formats the parsed content  
    fcontent = format_content(content) # O(n)
    # Uses formatted content to create points and line segments
    point, line_segments = create_line_segments_and_point(fcontent) # O(n)
    # runs the algorithm with specified parameters 
    run_algorithm(point, line_segments, show_plot, write_result_to_file) # O(n log(n))

if __name__ == "__main__":
    main()