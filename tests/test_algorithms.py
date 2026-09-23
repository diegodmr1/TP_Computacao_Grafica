from algorithms.rasterization.dda import dda_line
from algorithms.rasterization.bresenham_line import bresenham_line
from algorithms.rasterization.bresenham_circle import bresenham_circle

from algorithms.clipping.cohen_sutherland import cohen_sutherland
from algorithms.clipping.liang_barsky import liang_barsky

from algorithms.transformations.transformations import (
    translate_point,
    scale_point,
    rotate_point,
    reflect_x,
    reflect_y,
    reflect_xy,
)

from models.point import Point


def test_dda():
    result = dda_line(0, 0, 5, 5)

    assert result[0] == (0, 0)
    assert result[-1] == (5, 5)
    assert len(result) == 6


def test_bresenham_line():
    result = bresenham_line(0, 0, 5, 5)

    assert result[0] == (0, 0)
    assert result[-1] == (5, 5)


def test_bresenham_circle():
    result = bresenham_circle(0, 0, 5)

    assert (0, 5) in result
    assert (0, -5) in result
    assert (5, 0) in result
    assert (-5, 0) in result


def test_translation():
    point = Point(10, 20)

    result = translate_point(
        point,
        5,
        -10,
    )

    assert result.x == 15
    assert result.y == 10


def test_scale():
    point = Point(10, 20)

    result = scale_point(
        point,
        2,
        3,
    )

    assert result.x == 20
    assert result.y == 60


def test_rotation():
    point = Point(10, 0)

    result = rotate_point(
        point,
        90,
    )

    assert round(result.x, 5) == 0
    assert round(result.y, 5) == 10


def test_reflections():
    point = Point(10, 20)

    result_x = reflect_x(point)
    result_y = reflect_y(point)
    result_xy = reflect_xy(point)

    assert result_x.as_tuple() == (10, -20)
    assert result_y.as_tuple() == (-10, 20)
    assert result_xy.as_tuple() == (-10, -20)


def test_cohen_sutherland():
    result = cohen_sutherland(
        0,
        50,
        100,
        50,
        25,
        25,
        75,
        75,
    )

    assert result is not None

    x1, y1, x2, y2 = result

    assert round(x1) == 25
    assert round(y1) == 50
    assert round(x2) == 75
    assert round(y2) == 50


def test_liang_barsky():
    result = liang_barsky(
        0,
        50,
        100,
        50,
        25,
        25,
        75,
        75,
    )

    assert result is not None

    x1, y1, x2, y2 = result

    assert round(x1) == 25
    assert round(y1) == 50
    assert round(x2) == 75
    assert round(y2) == 50