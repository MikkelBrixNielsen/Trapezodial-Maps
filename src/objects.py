import matplotlib.pyplot as plt

class Point:
    def __init__(self, x, y, parent=None):
        self.x = x
        self.y = y
        self.parent = parent # references to its corresponding line segment 
    
    def plot(self, label: str = "", color: str = "black"):
        plt.plot(self.x, self.y, 'o', color=color, markersize=5)
        plt.annotate(label, (self.x, self.y), textcoords="offset points", xytext=(0, 10), ha='center')

    def __str__(self):
        return f"Point(x: {self.x}, y: {self.y})"

class LineSegment:
    def __init__(self, x1: int | float, y1: int | float, x2: int | float, y2: int | float, color: str = "black"):
        self.start = Point(x1, y1, self)
        self.end = Point(x2, y2, self)
        self.color = color
    
    def plot(self, marker: bool = True):
        x_coords = [self.start.x, self.end.x]
        y_coords = [self.start.y, self.end.y]
        plt.plot(x_coords, y_coords, marker='o', linestyle='-', color=self.color) if marker else plt.plot(x_coords, y_coords, linestyle='-', color=self.color)

    def intersect_vertical_line(self, x: Point):
        slope = (self.end.y - self.start.y) / (self.end.x - self.start.x)
        intercept = self.start.y - slope * self.start.x
        return x, (slope * x + intercept)
    
    def __str__(self):
        return f'LineSegment(from: {self.start}, to: {self.end})'
    
class Trapezoid:
    REGION_COUNT = 0
    def __init__(self, upper, lower, leftp, rightp, rightN=None, leftN=None, color="black"):
        self.upper = upper # Upper line segment
        self.lower = lower # Lower line segment
        self.leftp = leftp # left point
        self.rightp = rightp # right point 
        self.rightN = rightN # right neighbours 
        self.leftN = leftN # left neighbours
        self.label = self._generate_region_label()
        self.collected = False
        self.color = color
    
    def _generate_region_label(self):
        label = "R" + str(Trapezoid.REGION_COUNT)
        Trapezoid.REGION_COUNT += 1 
        return label
    
    def plot(self):
        left = LineSegment(*self.vertical_line_intersections(self.leftp.x), self.color)
        right = LineSegment(*self.vertical_line_intersections(self.rightp.x), self.color)
        upper = LineSegment(left.start.x, left.start.y, right.start.x, right.start.y, self.color)
        lower = LineSegment(left.end.x, left.end.y, right.end.x, right.end.y, self.color)
        left.plot(marker=False), right.plot(marker=False), upper.plot(marker=False), lower.plot(marker=False)

        x_mid = (self.rightp.x + self.leftp.x) / 2
        _ , y_upper = self.upper.intersect_vertical_line(x_mid)
        _ , y_lower = self.lower.intersect_vertical_line(x_mid)
        Point(x_mid, (y_upper + y_lower) / 2).plot(self.label)

    def vertical_line_intersections(self, p: Point):
        return *self.upper.intersect_vertical_line(p), *self.lower.intersect_vertical_line(p)
    
    def _print_neighbours(self, neigh):
        s = []
        if neigh:
            for n in neigh:
                if not n:
                    s.append(n)
                elif isinstance(n.data, Trapezoid):
                    s.append(f"{n.data.label}")
                else:
                    s.append(str(n.data.__class__.__name__))
        return s
    
    def __str__(self, indent: str = ""):
        return (f"Trapezoid(\n\t{indent}upper: {self.upper}\n\t"
                   f"{indent}lower: {self.lower}\n\t"
                   f"{indent}leftp: {self.leftp}\n\t"
                   f"{indent}rightp: {self.rightp}\n\t"
                   f"{indent}label: {self.label}\n\t"
                   f"{indent}leftN: {self._print_neighbours(self.leftN)}\n\t"
                   f"{indent}rightN: {self._print_neighbours(self.rightN)}\n\t{indent})")
    
    def to_string_with_indent(self, indent: str):
        return self.__str__(indent)