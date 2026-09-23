from models.point import Point


class Polygon:
    def __init__(
        self,
        points=None,
        color="#000000",
        fill_color=None,
    ):
        self.points = points if points is not None else []
        self.color = color
        self.fill_color = fill_color
        self.selected = False

    def add_point(self, point: Point):
        self.points.append(point)

    def copy(self):
        return Polygon(
            [point.copy() for point in self.points],
            self.color,
            self.fill_color,
        )

    def get_points(self):
        return self.points

    def __repr__(self):
        return (
            f"Polygon({self.points}, "
            f"color={self.color}, "
            f"fill_color={self.fill_color})"
        )