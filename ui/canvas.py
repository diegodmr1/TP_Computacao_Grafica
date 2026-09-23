import math

from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QColor, QPainter, QPen, QImage
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

from algorithms.filling.boundary_fill import boundary_fill
from algorithms.filling.flood_fill import flood_fill

from algorithms.transformations.transformations import (
    translate_points,
    rotate_points,
    scale_points,
)


class Canvas(QWidget):
    def __init__(self):
        super().__init__()

        self.setMinimumSize(800, 600)
        self.setMouseTracking(True)
        self.setStyleSheet("background-color: white;")

        self.objects = []

        self.mode = "line"
        self.line_algorithm = "bresenham"
        self.clipping_algorithm = "cohen"

        self.current_color = "#000000"
        self.current_fill_color = "#3498db"
        self.fill_algorithm = "boundary"

        self.first_point = None
        self.temp_point = None
        self.polygon_points = []

        self.selection_start = None
        self.selection_end = None
        self.selected_objects = []

        self.clip_start = None
        self.clip_end = None
        self.clip_rect = None
        self.clip_dragging = False
        self.clip_moved = False

        self.fill_image = None

    def set_mode(self, mode):
        self.mode = mode
        self.first_point = None
        self.temp_point = None
        self.polygon_points = []

        # Sempre reinicia uma criação de janela de recorte.
        self.clip_start = None
        self.clip_end = None

        cursors = {
            "line": Qt.CrossCursor,
            "circle": Qt.CrossCursor,
            "polygon": Qt.CrossCursor,
            "select": Qt.PointingHandCursor,
            "clip": Qt.CrossCursor,
            "fill": Qt.PointingHandCursor,
        }

        self.setCursor(
            cursors.get(
                mode,
                Qt.ArrowCursor,
            )
        )

        self.update()

    def set_line_algorithm(self, algorithm):
        self.line_algorithm = algorithm
        self.update()

    def set_clipping_algorithm(self, algorithm):
        self.clipping_algorithm = algorithm
        self.update()

    def set_current_color(self, color):
        self.current_color = color

    def set_fill_color(self, color):
        self.current_fill_color = color

    def set_fill_algorithm(self, algorithm):
        self.fill_algorithm = algorithm

    def clear_canvas(self):
        self.objects.clear()
        self.selected_objects.clear()
        self.polygon_points.clear()

        self.first_point = None
        self.temp_point = None

        self.clip_rect = None
        self.fill_image = None

        self.update()

    def mousePressEvent(self, event):
        point = Point(
            event.position().x(),
            event.position().y(),
        )

        if event.button() == Qt.LeftButton:
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
                # Primeiro clique: marca o primeiro canto.
                if self.clip_start is None:
                    self.clip_start = point
                    self.clip_end = point
                    self.update()
                    return

                # Segundo clique: fixa a janela e aplica o recorte.
                self.clip_end = point

                if self.create_clip_rectangle():
                    self.clip_start = None
                    self.clip_end = None
                    self.mode = "none"
                    self.setCursor(Qt.ArrowCursor)

                self.update()

            elif self.mode == "fill":
                self.apply_fill(
                    round(point.x),
                    round(point.y),
                )

        elif event.button() == Qt.RightButton:
            if (
                self.mode == "polygon"
                and len(self.polygon_points) >= 3
            ):
                polygon = Polygon(
                    [
                        vertex.copy()
                        for vertex in self.polygon_points
                    ],
                    self.current_color,
                )

                self.objects.append(polygon)
                self.polygon_points.clear()
                self.update()

    def mouseMoveEvent(self, event):
        point = Point(
            event.position().x(),
            event.position().y(),
        )

        self.temp_point = point

        if (
            self.mode == "select"
            and self.selection_start is not None
        ):
            self.selection_end = point

        elif (
            self.mode == "clip"
            and self.clip_start is not None
        ):
            # Somente a prévia visual.
            # clip_rect ainda não existe/é alterado aqui.
            self.clip_end = point

        self.update()

    def mouseReleaseEvent(self, event):
        if event.button() != Qt.LeftButton:
            return

        # O recorte NÃO é finalizado ao soltar o mouse.
        # Ele é finalizado exclusivamente no segundo clique.
        if self.mode != "select":
            return

        if self.selection_start is None:
            return

        point = Point(
            event.position().x(),
            event.position().y(),
        )

        self.selection_end = point
        self.select_objects()

        self.selection_start = None
        self.selection_end = None

        self.update()

    def handle_line_click(self, point):
        if self.first_point is None:
            self.first_point = point
            self.temp_point = point
            self.update()
            return

        line = Line(
            self.first_point.copy(),
            point.copy(),
            self.current_color,
        )

        self.objects.append(line)

        self.first_point = None
        self.temp_point = None

        self.update()

    def handle_circle_click(self, point):
        if self.first_point is None:
            self.first_point = point

        else:
            dx = point.x - self.first_point.x
            dy = point.y - self.first_point.y

            radius = math.sqrt(
                dx * dx + dy * dy
            )

            self.objects.append(
                Circle(
                    self.first_point.copy(),
                    radius,
                    self.current_color,
                )
            )

            self.first_point = None
            self.update()

    def create_clip_rectangle(self):
        if (
            self.clip_start is None
            or self.clip_end is None
        ):
            return False

        xmin = min(
            self.clip_start.x,
            self.clip_end.x,
        )
        ymin = min(
            self.clip_start.y,
            self.clip_end.y,
        )
        xmax = max(
            self.clip_start.x,
            self.clip_end.x,
        )
        ymax = max(
            self.clip_start.y,
            self.clip_end.y,
        )

        # Impede janela de área zero ou quase zero.
        if (xmax - xmin) < 5 or (ymax - ymin) < 5:
            return False

        self.clip_rect = (
            xmin,
            ymin,
            xmax,
            ymax,
        )

        return True

    def select_objects(self):
        xmin = min(
            self.selection_start.x,
            self.selection_end.x,
        )
        xmax = max(
            self.selection_start.x,
            self.selection_end.x,
        )

        ymin = min(
            self.selection_start.y,
            self.selection_end.y,
        )
        ymax = max(
            self.selection_start.y,
            self.selection_end.y,
        )

        self.selected_objects.clear()

        for obj in self.objects:
            obj.selected = False

            inside = any(
                xmin <= point.x <= xmax
                and ymin <= point.y <= ymax
                for point in obj.get_points()
            )

            if inside:
                obj.selected = True
                self.selected_objects.append(obj)

    def transform_selected(self, operation, *values):
        for obj in self.selected_objects:

            if isinstance(obj, Line):
                points = [
                    obj.start,
                    obj.end,
                ]

            elif isinstance(obj, Polygon):
                points = obj.points

            elif isinstance(obj, Circle):
                points = [obj.center]

            else:
                continue

            center_x = (
                sum(point.x for point in points)
                / len(points)
            )

            center_y = (
                sum(point.y for point in points)
                / len(points)
            )

            pivot = Point(
                center_x,
                center_y,
            )

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

    def create_scene_image(self):
        image = QImage(
            self.size(),
            QImage.Format_ARGB32,
        )

        # Fundo transparente.
        image.fill(Qt.transparent)

        painter = QPainter(image)

        try:
            for obj in self.objects:
                if isinstance(obj, Line):
                    self.draw_line(
                        painter,
                        obj,
                        use_selection=False,
                    )

                elif isinstance(obj, Circle):
                    self.draw_circle(
                        painter,
                        obj,
                        use_selection=False,
                    )

                elif isinstance(obj, Polygon):
                    self.draw_polygon(
                        painter,
                        obj,
                        use_selection=False,
                    )

        finally:
            painter.end()

        return image

    def apply_fill(self, x, y):
        x = round(x)
        y = round(y)

        if not (
            0 <= x < self.width()
            and 0 <= y < self.height()
        ):
            return

        target_object = None

        # Procura primeiro circunferências.
        for obj in reversed(self.objects):
            if isinstance(obj, Circle):
                dx = x - obj.center.x
                dy = y - obj.center.y

                if (
                    dx * dx + dy * dy
                    < obj.radius * obj.radius
                ):
                    target_object = obj
                    break

        # Se não encontrou circunferência,
        # procura polígonos.
        if target_object is None:
            for obj in reversed(self.objects):
                if not isinstance(obj, Polygon):
                    continue

                points = obj.points

                if len(points) < 3:
                    continue

                inside = False
                j = len(points) - 1

                for i in range(len(points)):
                    xi = points[i].x
                    yi = points[i].y
                    xj = points[j].x
                    yj = points[j].y

                    if (yi > y) != (yj > y):
                        intersection_x = (
                            (xj - xi)
                            * (y - yi)
                            / (yj - yi)
                            + xi
                        )

                        if x < intersection_x:
                            inside = not inside

                    j = i

                if inside:
                    target_object = obj
                    break

        # Clique fora de região fechada:
        # não faz nada.
        if target_object is None:
            return

        # Cria uma imagem somente para a região
        # que será preenchida.
        image = QImage(
            self.size(),
            QImage.Format_RGB32,
        )

        image.fill(QColor("white"))

        painter = QPainter(image)

        try:
            boundary_color = QColor("black")

            if isinstance(target_object, Circle):
                pixels = bresenham_circle(
                    target_object.center.x,
                    target_object.center.y,
                    target_object.radius,
                )

                for px, py in pixels:
                    self.draw_pixel(
                        painter,
                        px,
                        py,
                        "#000000",
                    )

            elif isinstance(target_object, Polygon):
                points = target_object.points

                for index in range(len(points)):
                    start = points[index]
                    end = points[
                        (index + 1) % len(points)
                    ]

                    pixels = bresenham_line(
                        start.x,
                        start.y,
                        end.x,
                        end.y,
                    )

                    for px, py in pixels:
                        self.draw_pixel(
                            painter,
                            px,
                            py,
                            "#000000",
                        )

        finally:
            painter.end()

        fill_color = QColor(
            self.current_fill_color
        ).rgb()

        boundary_rgb = boundary_color.rgb()

        def get_color(px, py):
            return image.pixel(px, py)

        def set_color(px, py, color):
            image.setPixel(
                px,
                py,
                color,
            )

        if self.fill_algorithm == "boundary":
            boundary_fill(
                x,
                y,
                get_color,
                set_color,
                {boundary_rgb},
                fill_color,
                image.width(),
                image.height(),
            )

        elif self.fill_algorithm == "flood":
            flood_fill(
                x,
                y,
                get_color,
                set_color,
                fill_color,
                image.width(),
                image.height(),
            )

        # Guarda a cor diretamente no objeto.
        target_object.fill_color = (
            self.current_fill_color
        )

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)

        try:
            painter.fillRect(
                self.rect(),
                QColor("white"),
            )

            # Grid sempre fica no fundo.
            self.draw_grid(painter)

            # Preenchimentos.
            for obj in self.objects:
                if (
                    isinstance(obj, Circle)
                    and obj.fill_color
                ):
                    painter.setPen(Qt.NoPen)
                    painter.setBrush(
                        QColor(obj.fill_color)
                    )

                    painter.drawEllipse(
                        QPoint(
                            round(obj.center.x),
                            round(obj.center.y),
                        ),
                        round(obj.radius),
                        round(obj.radius),
                    )

                    painter.setBrush(Qt.NoBrush)

                elif (
                    isinstance(obj, Polygon)
                    and obj.fill_color
                    and len(obj.points) >= 3
                ):
                    from PySide6.QtGui import QPolygon

                    polygon_points = [
                        QPoint(
                            round(point.x),
                            round(point.y),
                        )
                        for point in obj.points
                    ]

                    painter.setPen(Qt.NoPen)
                    painter.setBrush(
                        QColor(obj.fill_color)
                    )

                    painter.drawPolygon(
                        QPolygon(polygon_points)
                    )

                    painter.setBrush(Qt.NoBrush)

            # Bordas rasterizadas por cima.
            for obj in self.objects:
                if isinstance(obj, Line):
                    self.draw_line(
                        painter,
                        obj,
                    )

                elif isinstance(obj, Circle):
                    self.draw_circle(
                        painter,
                        obj,
                    )

                elif isinstance(obj, Polygon):
                    self.draw_polygon(
                        painter,
                        obj,
                    )

            self.draw_temporary(painter)
            self.draw_selection_rectangle(painter)
            self.draw_clip_rectangle(painter)

        finally:
            painter.end()

    def draw_grid(self, painter):
        painter.setPen(
            QPen(
                QColor(235, 235, 235),
                1,
            )
        )

        painter.setBrush(Qt.NoBrush)

        spacing = 20

        for x in range(
            0,
            self.width(),
            spacing,
        ):
            painter.drawLine(
                x,
                0,
                x,
                self.height(),
            )

        for y in range(
            0,
            self.height(),
            spacing,
        ):
            painter.drawLine(
                0,
                y,
                self.width(),
                y,
            )

    def draw_pixel(
        self,
        painter,
        x,
        y,
        color="#000000",
    ):
        qcolor = QColor(color)

        painter.setPen(
            QPen(qcolor, 1)
        )
        painter.setBrush(qcolor)

        painter.drawRect(
            round(x),
            round(y),
            2,
            2,
        )

        painter.setBrush(Qt.NoBrush)

    def draw_line(
        self,
        painter,
        line,
        use_selection=True,
    ):
        x1 = line.start.x
        y1 = line.start.y
        x2 = line.end.x
        y2 = line.end.y

        # Só aplica recorte quando existe
        # uma janela FINALIZADA.
        if self.clip_rect is not None:
            xmin, ymin, xmax, ymax = (
                self.clip_rect
            )

            if self.clipping_algorithm == "cohen":
                result = cohen_sutherland(
                    x1,
                    y1,
                    x2,
                    y2,
                    xmin,
                    ymin,
                    xmax,
                    ymax,
                )

            else:
                result = liang_barsky(
                    x1,
                    y1,
                    x2,
                    y2,
                    xmin,
                    ymin,
                    xmax,
                    ymax,
                )

            if result is None:
                return

            x1, y1, x2, y2 = result

        if self.line_algorithm == "dda":
            pixels = dda_line(
                x1,
                y1,
                x2,
                y2,
            )

        else:
            pixels = bresenham_line(
                x1,
                y1,
                x2,
                y2,
            )

        color = line.color

        if use_selection and line.selected:
            color = "#ff0000"

        for x, y in pixels:
            self.draw_pixel(
                painter,
                x,
                y,
                color,
            )

    def draw_circle(
        self,
        painter,
        circle,
        use_selection=True,
    ):
        pixels = bresenham_circle(
            circle.center.x,
            circle.center.y,
            circle.radius,
        )

        color = circle.color

        if use_selection and circle.selected:
            color = "#ff0000"

        for x, y in pixels:
            self.draw_pixel(
                painter,
                x,
                y,
                color,
            )

    def draw_polygon(
        self,
        painter,
        polygon,
        use_selection=True,
    ):
        if len(polygon.points) < 2:
            return

        color = polygon.color

        if use_selection and polygon.selected:
            color = "#ff0000"

        for index in range(
            len(polygon.points)
        ):
            start = polygon.points[index]

            end = polygon.points[
                (index + 1)
                % len(polygon.points)
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
                    color,
                )

    def draw_temporary(self, painter):
        if (
            self.first_point is not None
            and self.temp_point is not None
        ):
            painter.setPen(
                QPen(
                    QColor(
                        self.current_color
                    ),
                    1,
                )
            )

            painter.setBrush(Qt.NoBrush)

            if self.mode == "line":
                painter.drawLine(
                    QPoint(
                        round(
                            self.first_point.x
                        ),
                        round(
                            self.first_point.y
                        ),
                    ),
                    QPoint(
                        round(
                            self.temp_point.x
                        ),
                        round(
                            self.temp_point.y
                        ),
                    ),
                )

            elif self.mode == "circle":
                dx = (
                    self.temp_point.x
                    - self.first_point.x
                )

                dy = (
                    self.temp_point.y
                    - self.first_point.y
                )

                radius = int(
                    math.sqrt(
                        dx * dx + dy * dy
                    )
                )

                painter.drawEllipse(
                    QPoint(
                        round(
                            self.first_point.x
                        ),
                        round(
                            self.first_point.y
                        ),
                    ),
                    radius,
                    radius,
                )

        if (
            self.mode == "polygon"
            and self.polygon_points
        ):
            painter.setPen(
                QPen(
                    QColor(
                        self.current_color
                    ),
                    1,
                )
            )

            painter.setBrush(Qt.NoBrush)

            for index in range(
                len(self.polygon_points) - 1
            ):
                start = (
                    self.polygon_points[index]
                )

                end = self.polygon_points[
                    index + 1
                ]

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
                    round(
                        self.temp_point.x
                    ),
                    round(
                        self.temp_point.y
                    ),
                )

    def draw_selection_rectangle(
        self,
        painter,
    ):
        if (
            self.selection_start is None
            or self.selection_end is None
        ):
            return

        painter.setBrush(Qt.NoBrush)

        painter.setPen(
            QPen(
                QColor("blue"),
                1,
                Qt.DashLine,
            )
        )

        x = min(
            self.selection_start.x,
            self.selection_end.x,
        )

        y = min(
            self.selection_start.y,
            self.selection_end.y,
        )

        width = abs(
            self.selection_end.x
            - self.selection_start.x
        )

        height = abs(
            self.selection_end.y
            - self.selection_start.y
        )

        painter.drawRect(
            round(x),
            round(y),
            round(width),
            round(height),
        )

    def draw_clip_rectangle(self, painter):
        rect = None

        # Janela finalizada.
        if self.clip_rect is not None:
            rect = self.clip_rect

        # Enquanto cria, mostra somente a prévia.
        if (
            self.mode == "clip"
            and self.clip_start is not None
            and self.clip_end is not None
        ):
            rect = (
                min(
                    self.clip_start.x,
                    self.clip_end.x,
                ),
                min(
                    self.clip_start.y,
                    self.clip_end.y,
                ),
                max(
                    self.clip_start.x,
                    self.clip_end.x,
                ),
                max(
                    self.clip_start.y,
                    self.clip_end.y,
                ),
            )

        if rect is None:
            return

        xmin, ymin, xmax, ymax = rect

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