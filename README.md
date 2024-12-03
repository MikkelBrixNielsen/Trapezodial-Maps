# README

This README will contain a description of how to setup a virtual environment, how to get the program running in the virtual environment on both Windows, MacOS/Linux, as well as IMADA LAB caveats and all.

## Creating a Virtual Environment

 To create a virtual environment for this project, follow these steps:

1. Open your terminal of choice and check that you have Python 3.8.10 or higher, as follows:

    ``` bash
    python --version
    # should output 3.8.10 or higher
    ```

   - Or maybe something similar (IMADA LAB):

    ```bash
    python3 --version
    ```

2. Navigate to the project folder where this README is located.

3. Run the following command to create a virtual environment (replace `myvenv` with your preferred name):

    ```bash
    python -m venv myvenv
    ```

   - Or on IMADA LAB use:

    ``` bash
    python3 -m pip install virtualenv
    python3 -m virtualenv myenv
    ```

4. Activate the virtual environment:

   - **Windows**:

    ```bash
    .\myvenv\Scripts\activate
    ```

   - **MacOS/Linux/IMADA LAB**:

    ```bash
    source myvenv/bin/activate
    ```

## Installing Requirements

Once the virtual environment is activated, install the required packages by running:

- **Windows/MacOS/LINUX**

    ```bash
    pip install -r requirements.txt
    ```

- **IMADA LAB**

    ``` bash
    python -m pip install -r requirements.txt
    ```

## Usage

To use the program, ensure you are inside the project folder and have Python 3.8.10 and Pip 20.0.2 or higher installed. To check this you can run the following commands:

- **Python**

    ```bash
    python --version      # should output 3.8.10 or higher
    ```

- **Pip**

    ```bash
    pip --version         # should output 20.0.2 or higher
    ```

Then to run the program use the following command:

```bash
python ./src/main.py [ optional -d -p -o -qo ] <path_to_file>
```

### Parameters

- **Optional Flags**:
  - `-d`: Enable debug mode.
  - `-p`: Plot the output (region containing query point is colored red, query point is colored blue).
  - `-o`: Output a textual result in `output.txt` and a visual result in `TrapezoidalMapPlot.png`.
  - `-qo`: Output only the result of the query in `output.txt` (No search structure or image).
  
<div style="page-break-after: always;"></div>

- **File Argument**:
  - You can specify either:
    - `./Test/<file_name>` to use the provided test files, or
    - `<path_to_file>` to use your own test files.

### Input Fromat

For input data, represent a line segment going from `(x1, y1)` to `(x2, y2)` by `x1 y1 x2 y2` terminated by one newline.

Similarly, a point is represented by using two coordinates instead of four and there should be exactly one.

A test file should have the point specified on the first line followed by a sequence of disjoint line segments on the subsequent lines, where no two coordinate's `(x or y)` are identical.

Positive and negative integer and float coordinates are allowed, the sign is however required to be immediately in front of the integer/float.

Additionally, before `x1`, in between two coordinates, and after `y2` (but before the newline), any number of spaces or tabs are allowed, so an input file could look like this (or worse):

<pre>
            2.5         0.5
2               2 17              2
            1 3      4                   3.1
5               1 7         1.1
8            3 9                    3.1
                 10         1       12       1.1
14              3.2 16               2.9
                     3 6 11 4
15 6 18 5
6               -1 13 -0.5
    2.25 -1.25 19               -1.5
            0.5                 7 16.5 4
8.5 0.5         0 0.1
                        18.5 -0.1 11.5 0.5

</pre>

#### Input Errors

In regards to input not following the specified format various errors can arise and will be printed to standard output. These errors include:

- Multiple points defined in input.
- No point defined in input.
- No line segments defined in the input file.
- Point not defined first in input file.
- Input file empty.
- Points or line segments being wrongly formatted.
- A line segment is vertical i.e. `x1 == x2`

### Textual / Pysical Output

The files `output.txt` and `TrapezoidalMapPlot.png` will be created in the current directory from which you run the program. For example:

- If you run the program, using [this](#usage) command, in the project folder, the files will be placed alongside the `README.md` and `requirements.txt` files in the project folder.

- If you navigate to the `src` folder and run the program from here, the files will be placed in the `src` folder and so on.

The format of `output.txt` will have a sentence describing which trapezoid the query point is contained within, along with the data describing the trapezoid followed by a textual representation of the search structure, which could look like the following:

``` example
----------------------------------------------------------------------------------
The query point: Point(x: 3.0, y: 3.0) lies within: R4

Trapezoid(
    upper: LineSegment(from: Point(x: 1.0, y: 5.0), to: Point(x: 5.0, y: 5.0))
    lower: LineSegment(from: Point(x: 0.0, y: 2.0), to: Point(x: 6.0, y: 2.0))
    leftp: Point(x: 1.0, y: 5.0)
    rightp: Point(x: 5.0, y: 5.0)
    label: R4
    leftN: ['R1']
    rightN: ['R2']
    )
----------------------------------------------------------------------------------

--------------------------The resulting search structure--------------------------
Root: Point(x: 1.0, y: 5.0)
    L: |--->Trapezoid(
        upper: LineSegment(from: Point(x: 0.0, y: 6.0), to: Point(x: 6.0, y: 6.0))
        lower: LineSegment(from: Point(x: 0.0, y: 2.0), to: Point(x: 6.0, y: 2.0))
        leftp: Point(x: 0.0, y: 2.0)
        rightp: Point(x: 1.0, y: 5.0)
        label: R1
        leftN: []
        rightN: ['R3', 'R4']
        )
    R: |--->Point(x: 5.0, y: 5.0)
        L: |--->LineSegment(from: Point(x: 1.0, y: 5.0), to: Point(x: 5.0, y: 5.0))
            L: |--->Trapezoid(
                upper: LineSegment(from: Point(x: 0.0, y: 6.0), to: Point(x: 6.0, y: 6.0))
                lower: LineSegment(from: Point(x: 1.0, y: 5.0), to: Point(x: 5.0, y: 5.0))
                leftp: Point(x: 1.0, y: 5.0)
                rightp: Point(x: 5.0, y: 5.0)
                label: R3
                leftN: ['R1']
                rightN: ['R2']
                )
            R: |--->Trapezoid(
                upper: LineSegment(from: Point(x: 1.0, y: 5.0), to: Point(x: 5.0, y: 5.0))
                lower: LineSegment(from: Point(x: 0.0, y: 2.0), to: Point(x: 6.0, y: 2.0))
                leftp: Point(x: 1.0, y: 5.0)
                rightp: Point(x: 5.0, y: 5.0)
                label: R4
                leftN: ['R1']
                rightN: ['R2']
                )
        R: |--->Trapezoid(
            upper: LineSegment(from: Point(x: 0.0, y: 6.0), to: Point(x: 6.0, y: 6.0))
            lower: LineSegment(from: Point(x: 0.0, y: 2.0), to: Point(x: 6.0, y: 2.0))
            leftp: Point(x: 5.0, y: 5.0)
            rightp: Point(x: 6.0, y: 6.0)
            label: R2
            leftN: ['R3', 'R4']
            rightN: []
            )
----------------------------------------------------------------------------------
```

<div style="page-break-after: always;"></div>

### Graphical Output

For graphical output, the `-p` option enables the program to generate a visual representation of the results. When this flag is used, Matplotlib is employed to display the trapezoidal map by plotting the trapezoids constructed during its creation along with the line segments specified in the input file as well as the query point. The trapezoid containing the query point will be colored red and the query point colored blue, which could look like the following figure:
![Example_Graphical_Output](Images\Example_Graphical_Output.png)

<div style="page-break-after: always;"></div>

### Notes on The Provided Tests

There are provided 21 tests of which the test files `test14.txt` through `test21.txt`, will fail and output something resembling the following errors to stdout:

- `test14.txt`: `Error: File '.\Test\test14.txt' is empty.`
  
- `test15.txt`:  `Error: No line segments provided in test file.`
  
- `test16.txt`:  `Error: No point provided in test file.`
  
- `test17.txt`:  `Error: The point is not defined first in input file.`
  
- `test18.txt`:  `Error: Multiple points defined in input file, line 4.`
  
- `test19.txt`:  `Error: Line 1 in input file was not formatted correctly, was expecting 2 coordinates but recieved 1 ('0.0').`
  
- `test20.txt`:  `Error: Line 4 in input file was not formatted correctly, was expecting 4 coordinates but recieved 3 ('2.0', '4.0', '6.0').`

- `test21.txt`:  `Error: Vertical line defined on line 2 in input file.`

For all other test files, when the `-qo` flag is used, all test files should output what region contains the query point is output.txt. Additionally, if the `-o` flag is used a representation of the search structure will also be written to output.txt along with what region  contains the query point as well as a picture of the map in TrapezoidalMapPlot.png. If the `-p` flag is used, the output should be displayed graphically. In any case, the program should run without errors.