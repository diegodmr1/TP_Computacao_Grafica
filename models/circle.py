from models.point import Point


class Circle:
    def __init__(
        self,
        center: Point,
        radius,
        color="#000000",
        fill_color=None,
    ):
        self.center = center
        self.radius = float(radius)
        self.color = color
        self.fill_color = fill_color
        self.selected = False

    def copy(self):
        return Circle(
            self.center.copy(),
            self.radius,
            self.color,
            self.fill_color,
        )

    def get_points(self):
        return [self.center]

    def __repr__(self):
        return (
            f"Circle(center={self.center}, "
            f"radius={self.radius:.2f}, "
            f"color={self.color}, "
            f"fill_color={self.fill_color})"
        )