import math

from models.point import Point


def translate_point(point: Point, tx, ty):
    return Point(
        point.x + tx,
        point.y + ty
    )


def scale_point(point: Point, sx, sy, pivot=None):
    if pivot is None:
        pivot = Point(0, 0)

    x = pivot.x + (point.x - pivot.x) * sx
    y = pivot.y + (point.y - pivot.y) * sy

    return Point(x, y)


def rotate_point(point: Point, angle_degrees, pivot=None):
    if pivot is None:
        pivot = Point(0, 0)

    angle = math.radians(angle_degrees)

    x = point.x - pivot.x
    y = point.y - pivot.y

    rotated_x = x * math.cos(angle) - y * math.sin(angle)
    rotated_y = x * math.sin(angle) + y * math.cos(angle)

    return Point(
        rotated_x + pivot.x,
        rotated_y + pivot.y
    )


def reflect_x(point: Point):
    return Point(
        point.x,
        -point.y
    )


def reflect_y(point: Point):
    return Point(
        -point.x,
        point.y
    )


def reflect_xy(point: Point):
    return Point(
        -point.x,
        -point.y
    )


def translate_points(points, tx, ty):
    return [
        translate_point(point, tx, ty)
        for point in points
    ]


def scale_points(points, sx, sy, pivot=None):
    return [
        scale_point(point, sx, sy, pivot)
        for point in points
    ]


def rotate_points(points, angle_degrees, pivot=None):
    return [
        rotate_point(point, angle_degrees, pivot)
        for point in points
    ]


def reflect_points_x(points):
    return [
        reflect_x(point)
        for point in points
    ]


def reflect_points_y(points):
    return [
        reflect_y(point)
        for point in points
    ]


def reflect_points_xy(points):
    return [
        reflect_xy(point)
        for point in points
    ]