from models.point import Point


class Circle:
    def __init__(self, center: Point, radius):
        self.center = center
        self.radius = float(radius)
        self.selected = False

    def copy(self):
        return Circle(self.center.copy(), self.radius)

    def get_points(self):
        return [self.center]

    def __repr__(self):
        return f"Circle(center={self.center}, radius={self.radius:.2f})"