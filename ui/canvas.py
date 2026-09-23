import math

from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget

from models.point import Point
from models.line import Line
from models.circle import Circle
from models.polygon import Polygon

from algorithms.rasterization.dda import dda_line
from algorithms.rasterization.bresenham_line import bresenham_line
from algorithms.rasterization.bresenham_circle import bresenham_circle

from algorithms.clipping.cohen_sutherland import cohen_sutherland
from algorithms.clipping.liang_barsky import liang_barsky

from algorithms.transformations.transformations import (
    translate_points,
    rotate_points,
    scale_points,
    reflect_points_x,
    reflect_points_y,
    reflect_points_xy,
)


class Canvas(QWidget):
    def __init__(self):
        super().__init__()

        self.setMinimumSize(800, 600)
        self.setMouseTracking(True)

        self.objects = []

        self.mode = "line"
        self.line_algorithm = "bresenham"
        self.clipping_algorithm = "cohen"

        self.first_point = None
        self.temp_point = None

        self.polygon_points = []

        self.selection_start = None
        self.selection_end = None

        self.clip_start = None
        self.clip_end = None
        self.clip_rect = None

        self.selected_objects = []

        self.setStyleSheet("background-color: white;")

    def set_mode(self, mode):
        self.mode = mode
        self.first_point = None
        self.temp_point = None
        self.polygon_points = []
        self.update()

    def set_line_algorithm(self, algorithm):
        self.line_algorithm = algorithm
        self.update()

    def set_clipping_algorithm(self, algorithm):
        self.clipping_algorithm = algorithm

    def clear_canvas(self):
        self.objects.clear()
        self.selected_objects.clear()
        self.polygon_points.clear()
        self.first_point = None
        self.temp_point = None
        self.clip_rect = None
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            point = Point(event.position().x(), event.position().y())

            if self.mode == "line":
                self.handle_line_click(point)

            elif self.mode == "circle":
                self.handle_circle_click(point)

            elif self.mode == "polygon":
                self.polygon_points.append(point)
                self.update()

            elif self.mode == "select":
                self.selection_start = point
                self.selection_end = point

            elif self.mode == "clip":
                self.clip_start = point
                self.clip_end = point

        elif event.button() == Qt.RightButton:
            if self.mode == "polygon" and len(self.polygon_points) >= 3:
                polygon = Polygon(
                    [point.copy() for point in self.polygon_points]
                )
                self.objects.append(polygon)
                self.polygon_points.clear()
                self.update()

    def mouseMoveEvent(self, event):
        point = Point(event.position().x(), event.position().y())
        self.temp_point = point

        if self.mode == "select" and self.selection_start is not None:
            self.selection_end = point

        if self.mode == "clip" and self.clip_start is not None:
            self.clip_end = point

        self.update()

    def mouseReleaseEvent(self, event):
        if event.button() != Qt.LeftButton:
            return

        point = Point(event.position().x(), event.position().y())

        if self.mode == "select" and self.selection_start is not None:
            self.selection_end = point
            self.select_objects()
            self.selection_start = None
            self.selection_end = None
            self.update()

        elif self.mode == "clip" and self.clip_start is not None:
            self.clip_end = point
            self.create_clip_rectangle()
            self.clip_start = None
            self.clip_end = None
            self.update()

    def handle_line_click(self, point):
        if self.first_point is None:
            self.first_point = point
        else:
            self.objects.append(
                Line(self.first_point.copy(), point.copy())
            )
            self.first_point = None
            self.update()

    def handle_circle_click(self, point):
        if self.first_point is None:
            self.first_point = point
        else:
            dx = point.x - self.first_point.x
            dy = point.y - self.first_point.y

            radius = math.sqrt(dx * dx + dy * dy)

            self.objects.append(
                Circle(self.first_point.copy(), radius)
            )

            self.first_point = None
            self.update()

    def create_clip_rectangle(self):
        x1 = self.clip_start.x
        y1 = self.clip_start.y
        x2 = self.clip_end.x
        y2 = self.clip_end.y

        self.clip_rect = (
            min(x1, x2),
            min(y1, y2),
            max(x1, x2),
            max(y1, y2),
        )

    def select_objects(self):
        if self.selection_start is None or self.selection_end is None:
            return

        xmin = min(self.selection_start.x, self.selection_end.x)
        xmax = max(self.selection_start.x, self.selection_end.x)
        ymin = min(self.selection_start.y, self.selection_end.y)
        ymax = max(self.selection_start.y, self.selection_end.y)

        self.selected_objects.clear()

        for obj in self.objects:
            obj.selected = False

            points = obj.get_points()

            inside = any(
                xmin <= point.x <= xmax
                and ymin <= point.y <= ymax
                for point in points
            )

            if inside:
                obj.selected = True
                self.selected_objects.append(obj)

    def transform_selected(self, operation, *values):
        for obj in self.selected_objects:

            if isinstance(obj, Line):
                points = [obj.start, obj.end]

            elif isinstance(obj, Polygon):
                points = obj.points

            elif isinstance(obj, Circle):
                points = [obj.center]

            else:
                continue

            # Centro do próprio objeto
            center_x = sum(point.x for point in points) / len(points)
            center_y = sum(point.y for point in points) / len(points)
            pivot = Point(center_x, center_y)

            if operation == "translate":
                transformed = translate_points(
                    points,
                    values[0],
                    values[1],
                )

            elif operation == "rotate":
                transformed = rotate_points(
                    points,
                    values[0],
                    pivot,
                )

            elif operation == "scale":
                transformed = scale_points(
                    points,
                    values[0],
                    values[1],
                    pivot,
                )

            elif operation == "reflect_x":
                transformed = [
                    Point(
                        point.x,
                        2 * pivot.y - point.y,
                    )
                    for point in points
                ]

            elif operation == "reflect_y":
                transformed = [
                    Point(
                        2 * pivot.x - point.x,
                        point.y,
                    )
                    for point in points
                ]

            elif operation == "reflect_xy":
                transformed = [
                    Point(
                        2 * pivot.x - point.x,
                        2 * pivot.y - point.y,
                    )
                    for point in points
                ]

            else:
                continue

            if isinstance(obj, Line):
                obj.start = transformed[0]
                obj.end = transformed[1]

            elif isinstance(obj, Polygon):
                obj.points = transformed

            elif isinstance(obj, Circle):
                obj.center = transformed[0]

                if operation == "scale":
                    sx, sy = values
                    obj.radius *= (
                        abs(sx) + abs(sy)
                    ) / 2

        self.update()

    def transform_points(self, points, operation, *values):
        if operation == "translate":
            return translate_points(points, values[0], values[1])

        if operation == "rotate":
            return rotate_points(points, values[0])

        if operation == "scale":
            return scale_points(points, values[0], values[1])

        if operation == "reflect_x":
            return reflect_points_x(points)

        if operation == "reflect_y":
            return reflect_points_y(points)

        if operation == "reflect_xy":
            return reflect_points_xy(points)

        return points

    def paintEvent(self, event):
        painter = QPainter(self)

        painter.fillRect(self.rect(), QColor("white"))

        self.draw_grid(painter)

        for obj in self.objects:
            if isinstance(obj, Line):
                self.draw_line(painter, obj)

            elif isinstance(obj, Circle):
                self.draw_circle(painter, obj)

            elif isinstance(obj, Polygon):
                self.draw_polygon(painter, obj)

        self.draw_temporary(painter)
        self.draw_selection_rectangle(painter)
        self.draw_clip_rectangle(painter)

        painter.end()

    def draw_grid(self, painter):
        painter.setPen(QPen(QColor(235, 235, 235), 1))

        spacing = 20

        for x in range(0, self.width(), spacing):
            painter.drawLine(x, 0, x, self.height())

        for y in range(0, self.height(), spacing):
            painter.drawLine(0, y, self.width(), y)

    def draw_pixel(self, painter, x, y, selected=False):
        if selected:
            painter.setPen(QPen(QColor("red"), 1))
            painter.setBrush(QColor("red"))
        else:
            painter.setPen(QPen(QColor("black"), 1))
            painter.setBrush(QColor("black"))

        painter.drawRect(round(x), round(y), 2, 2)

    def draw_line(self, painter, line):
        if self.line_algorithm == "dda":
            pixels = dda_line(
                line.start.x,
                line.start.y,
                line.end.x,
                line.end.y,
            )
        else:
            pixels = bresenham_line(
                line.start.x,
                line.start.y,
                line.end.x,
                line.end.y,
            )

        if self.clip_rect is not None:
            xmin, ymin, xmax, ymax = self.clip_rect

            if self.clipping_algorithm == "cohen":
                result = cohen_sutherland(
                    line.start.x,
                    line.start.y,
                    line.end.x,
                    line.end.y,
                    xmin,
                    ymin,
                    xmax,
                    ymax,
                )
            else:
                result = liang_barsky(
                    line.start.x,
                    line.start.y,
                    line.end.x,
                    line.end.y,
                    xmin,
                    ymin,
                    xmax,
                    ymax,
                )

            if result is None:
                return

            x1, y1, x2, y2 = result

            if self.line_algorithm == "dda":
                pixels = dda_line(x1, y1, x2, y2)
            else:
                pixels = bresenham_line(x1, y1, x2, y2)

        for x, y in pixels:
            self.draw_pixel(
                painter,
                x,
                y,
                line.selected
            )

    def draw_circle(self, painter, circle):
        pixels = bresenham_circle(
            circle.center.x,
            circle.center.y,
            circle.radius,
        )

        for x, y in pixels:
            self.draw_pixel(
                painter,
                x,
                y,
                circle.selected
            )

    def draw_polygon(self, painter, polygon):
        if len(polygon.points) < 2:
            return

        for index in range(len(polygon.points)):
            start = polygon.points[index]
            end = polygon.points[
                (index + 1) % len(polygon.points)
            ]

            pixels = bresenham_line(
                start.x,
                start.y,
                end.x,
                end.y,
            )

            for x, y in pixels:
                self.draw_pixel(
                    painter,
                    x,
                    y,
                    polygon.selected
                )

    def draw_temporary(self, painter):
        if self.first_point is not None and self.temp_point is not None:
            painter.setPen(QPen(QColor("gray"), 1))

            if self.mode == "line":
                painter.drawLine(
                    QPoint(
                        round(self.first_point.x),
                        round(self.first_point.y),
                    ),
                    QPoint(
                        round(self.temp_point.x),
                        round(self.temp_point.y),
                    ),
                )

            elif self.mode == "circle":
                dx = self.temp_point.x - self.first_point.x
                dy = self.temp_point.y - self.first_point.y

                radius = int(math.sqrt(dx * dx + dy * dy))

                painter.drawEllipse(
                    QPoint(
                        round(self.first_point.x),
                        round(self.first_point.y),
                    ),
                    radius,
                    radius,
                )

        if self.mode == "polygon" and self.polygon_points:
            painter.setPen(QPen(QColor("gray"), 1))

            for index in range(len(self.polygon_points) - 1):
                start = self.polygon_points[index]
                end = self.polygon_points[index + 1]

                painter.drawLine(
                    round(start.x),
                    round(start.y),
                    round(end.x),
                    round(end.y),
                )

            if self.temp_point is not None:
                last = self.polygon_points[-1]

                painter.drawLine(
                    round(last.x),
                    round(last.y),
                    round(self.temp_point.x),
                    round(self.temp_point.y),
                )

    def draw_selection_rectangle(self, painter):
        if self.selection_start is None or self.selection_end is None:
            return

        painter.setPen(
            QPen(
                QColor("blue"),
                1,
                Qt.DashLine,
            )
        )

        x = min(self.selection_start.x, self.selection_end.x)
        y = min(self.selection_start.y, self.selection_end.y)

        width = abs(
            self.selection_end.x - self.selection_start.x
        )
        height = abs(
            self.selection_end.y - self.selection_start.y
        )

        painter.drawRect(
            round(x),
            round(y),
            round(width),
            round(height),
        )

    def draw_clip_rectangle(self, painter):
        rect = self.clip_rect

        if self.clip_start is not None and self.clip_end is not None:
            rect = (
                min(self.clip_start.x, self.clip_end.x),
                min(self.clip_start.y, self.clip_end.y),
                max(self.clip_start.x, self.clip_end.x),
                max(self.clip_start.y, self.clip_end.y),
            )

        if rect is None:
            return

        xmin, ymin, xmax, ymax = rect

        # Sem preenchimento: desenha apenas a borda
        painter.setBrush(Qt.NoBrush)

        painter.setPen(
            QPen(
                QColor("green"),
                2,
                Qt.DashLine,
            )
        )

        painter.drawRect(
            round(xmin),
            round(ymin),
            round(xmax - xmin),
            round(ymax - ymin),
        )