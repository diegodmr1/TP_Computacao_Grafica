from models.point import Point


class Line:
    def __init__(self, start: Point, end: Point):
        self.start = start
        self.end = end
        self.selected = False

    def copy(self):
        return Line(self.start.copy(), self.end.copy())

    def get_points(self):
        return [self.start, self.end]

    def __repr__(self):
        return f"Line({self.start}, {self.end})"