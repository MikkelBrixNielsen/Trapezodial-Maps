import matplotlib.pyplot as plt

class Point:
    def __init__(self, x, y, parent=None):
        self.x = x
        self.y = y
        self.parent = parent # references to its corresponding line segment 
    
    def plot(self, label):
        plt.plot(self.x, self.y, 'o', color="black", markersize=5)
        plt.annotate(label, (self.x, self.y), textcoords="offset points", xytext=(0, 10), ha='center')

    def __str__(self):
        return f"Point(x: {self.x}, y: {self.y})"

class LineSegment:
    def __init__(self, x1, y1, x2, y2):
        self.start = Point(x1, y1, self)
        self.end = Point(x2, y2, self)
    
    def plot(self):
        x_coords = [self.start.x, self.end.x]
        y_coords = [self.start.y, self.end.y]
        plt.plot(x_coords, y_coords, marker='o', linestyle='-', color="black")

    def __str__(self):
        return f'LineSegment(from: {self.start}, to: {self.end})'
    
    def intersect_vertical_line(self, x):
        if min(self.start.x, self.end.x) <= x <= max(self.start.x, self.end.x):
            slope = (self.end.y - self.start.y) / (self.end.x - self.start.x)
            y_intersect = self.start.y + slope * (x - self.start.x)
            return x, y_intersect
        return None
    
class Trapezoid:
    REGION_COUNT = 0
    def __init__(self, upper, lower, leftp, rightp, rightN=None, leftN=None):
        self.upper = upper # Upper line segment
        self.lower = lower # Lower line segment
        self.leftp = leftp # left point
        self.rightp = rightp # right point 
        self.rightN = rightN # right neighbours 
        self.leftN = leftN # left neighbours
        self.label = self._generate_region_label()
    
    def _generate_region_label(self):
        label = "R" + str(Trapezoid.REGION_COUNT)
        Trapezoid.REGION_COUNT += 1 
        return label
    
    def plot(self):
        LineSegment(*self.vertical_line_intersections(self.leftp.x)).plot()
        LineSegment(*self.vertical_line_intersections(self.rightp.x)).plot()
        self.upper.plot()
        self.lower.plot()

    def vertical_line_intersections(self, p):
        return *self.upper.intersect_vertical_line(p), *self.lower.intersect_vertical_line(p)
    
    def _print_neighbours(self, neigh):
        s = []
        if neigh:
            for n in neigh:
                s.append(str(n.data.__class__.__name__))
        return s
    
    def __str__(self, indent=""):
        return f'Trapezoid(\n\t{indent}upper: {self.upper}\n\t{indent}lower: {self.lower}\n\t{indent}leftp: {self.leftp}\n\t{indent}rightp: {self.rightp}\n\t{indent}rightN: {self._print_neighbours(self.rightN)}\n\t{indent}leftN: {self._print_neighbours(self.leftN)}\n{indent})'
    
    def to_string_with_indent(self, indent):
        return self.__str__(indent)