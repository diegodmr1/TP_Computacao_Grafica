from models.point import Point


class Polygon:
    def __init__(self, points=None):
        self.points = points if points is not None else []
        self.selected = False

    def add_point(self, point: Point):
        self.points.append(point)

    def copy(self):
        return Polygon([point.copy() for point in self.points])

    def get_points(self):
        return self.points

    def __repr__(self):
        return f"Polygon({self.points})"