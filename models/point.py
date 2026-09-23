class Point:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)

    def copy(self):
        return Point(self.x, self.y)

    def as_tuple(self):
        return self.x, self.y

    def __repr__(self):
        return f"Point({self.x:.2f}, {self.y:.2f})"