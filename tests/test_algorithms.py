from algorithms.filling.boundary_fill import boundary_fill
from algorithms.filling.flood_fill import flood_fill


def test_boundary_fill():
    width = 10
    height = 10

    WHITE = 0
    BLACK = 1
    RED = 2

    pixels = [
        [WHITE for _ in range(width)]
        for _ in range(height)
    ]

    # Cria uma região quadrada fechada
    for x in range(2, 8):
        pixels[2][x] = BLACK
        pixels[7][x] = BLACK

    for y in range(2, 8):
        pixels[y][2] = BLACK
        pixels[y][7] = BLACK

    def get_color(x, y):
        return pixels[y][x]

    def set_color(x, y, color):
        pixels[y][x] = color

    boundary_fill(
        4,
        4,
        get_color,
        set_color,
        BLACK,
        RED,
        width,
        height,
    )

    assert pixels[4][4] == RED
    assert pixels[3][3] == RED

    assert pixels[2][4] == BLACK
    assert pixels[7][4] == BLACK

    assert pixels[0][0] == WHITE


def test_flood_fill():
    width = 10
    height = 10

    WHITE = 0
    BLACK = 1
    BLUE = 2

    pixels = [
        [WHITE for _ in range(width)]
        for _ in range(height)
    ]

    # Região interna
    for y in range(3, 7):
        for x in range(3, 7):
            pixels[y][x] = BLACK

    def get_color(x, y):
        return pixels[y][x]

    def set_color(x, y, color):
        pixels[y][x] = color

    flood_fill(
        4,
        4,
        get_color,
        set_color,
        BLUE,
        width,
        height,
    )

    assert pixels[4][4] == BLUE
    assert pixels[3][3] == BLUE
    assert pixels[6][6] == BLUE

    assert pixels[0][0] == WHITE


def test_object_colors():
    from models.point import Point
    from models.line import Line
    from models.circle import Circle
    from models.polygon import Polygon

    line = Line(
        Point(0, 0),
        Point(10, 10),
        "#ff0000",
    )

    circle = Circle(
        Point(50, 50),
        20,
        "#00ff00",
    )

    polygon = Polygon(
        [
            Point(0, 0),
            Point(10, 0),
            Point(5, 10),
        ],
        "#0000ff",
    )

    assert line.color == "#ff0000"
    assert circle.color == "#00ff00"
    assert polygon.color == "#0000ff"