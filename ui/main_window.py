from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QComboBox,
    QDoubleSpinBox,
    QGroupBox,
    QMessageBox,
    QColorDialog,
    QScrollArea,
)

from ui.canvas import Canvas


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("TP_CG - Diego Moreira")
        self.resize(1280, 800)
        self.setMinimumSize(1000, 650)

        self.canvas = Canvas()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)

        controls = self.create_controls()

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(controls)
        scroll_area.setMinimumWidth(350)
        scroll_area.setMaximumWidth(380)

        main_layout.addWidget(scroll_area)
        main_layout.addWidget(self.canvas, 1)

        self.statusBar().showMessage(
            "Selecione uma ferramenta."
        )

        self.setStyleSheet("""
            QPushButton {
                padding: 5px;
                border: 1px solid #aaaaaa;
                border-radius: 4px;
            }

            QPushButton:hover {
                border: 2px solid #4285f4;
            }

            QPushButton:pressed {
                border: 2px solid #1a73e8;
            }

            QGroupBox {
                font-weight: bold;
                margin-top: 6px;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 4px;
            }
""")

    def create_controls(self):
        panel = QWidget()
        panel.setMinimumWidth(320)

        layout = QVBoxLayout(panel)

        title = QLabel("TP_CG - Diego Moreira")
        title.setStyleSheet(
            "font-size: 18px;"
            "font-weight: bold;"
            "margin: 8px;"
        )

        layout.addWidget(title)

        self.active_tool_label = QLabel(
            "Ferramenta ativa: Reta"
        )

        self.active_tool_label.setStyleSheet(
            "background-color: #e8f0fe;"
            "border: 1px solid #4285f4;"
            "border-radius: 5px;"
            "padding: 8px;"
            "font-weight: bold;"
        )

        layout.addWidget(
            self.active_tool_label
        )           

        layout.addWidget(
            self.create_color_group()
        )

        layout.addWidget(
            self.create_drawing_group()
        )

        layout.addWidget(
            self.create_rasterization_group()
        )

        layout.addWidget(
            self.create_fill_group()
        )

        layout.addWidget(
            self.create_selection_group()
        )

        layout.addWidget(
            self.create_transform_group()
        )

        layout.addWidget(
            self.create_clipping_group()
        )

        clear_button = QPushButton(
            "Limpar área de desenho"
        )

        clear_button.clicked.connect(
            self.canvas.clear_canvas
        )

        layout.addWidget(clear_button)
        layout.addStretch()

        return panel

    def create_color_group(self):
        group = QGroupBox("Cores")
        layout = QVBoxLayout(group)

        self.line_color_button = QPushButton(
            "Cor do desenho"
        )

        self.line_color_button.setStyleSheet(
            "background-color: #000000;"
            "color: white;"
        )

        self.line_color_button.clicked.connect(
            self.choose_line_color
        )

        self.fill_color_button = QPushButton(
            "Cor do preenchimento"
        )

        self.fill_color_button.setStyleSheet(
            "background-color: #3498db;"
            "color: white;"
        )

        self.fill_color_button.clicked.connect(
            self.choose_fill_color
        )

        layout.addWidget(
            self.line_color_button
        )

        layout.addWidget(
            self.fill_color_button
        )

        return group

    def create_drawing_group(self):
        group = QGroupBox("Objetos")
        layout = QVBoxLayout(group)

        line_button = QPushButton("Reta")
        circle_button = QPushButton(
            "Circunferência"
        )
        polygon_button = QPushButton(
            "Polígono"
        )

        line_button.clicked.connect(
            lambda: self.set_mode(
                "line",
                "Reta",
            )
        )

        circle_button.clicked.connect(
            lambda: self.set_mode(
                "circle",
                "Circunferência",
            )
        )

        polygon_button.clicked.connect(
            lambda: self.set_mode(
                "polygon",
                "Polígono",
            )
        )

        layout.addWidget(line_button)
        layout.addWidget(circle_button)
        layout.addWidget(polygon_button)

        help_label = QLabel(
            "Polígono: clique nos vértices "
            "e use o botão direito para finalizar."
        )

        help_label.setWordWrap(True)

        layout.addWidget(help_label)

        return group

    def create_rasterization_group(self):
        group = QGroupBox(
            "Rasterização de Retas"
        )

        layout = QVBoxLayout(group)

        self.line_algorithm = QComboBox()

        self.line_algorithm.addItem(
            "Bresenham",
            "bresenham",
        )

        self.line_algorithm.addItem(
            "DDA",
            "dda",
        )

        self.line_algorithm.currentIndexChanged.connect(
            self.change_line_algorithm
        )

        layout.addWidget(
            self.line_algorithm
        )

        return group

    def create_fill_group(self):
        group = QGroupBox(
            "Preenchimento"
        )

        layout = QVBoxLayout(group)

        self.fill_algorithm = QComboBox()

        self.fill_algorithm.addItem(
            "Boundary-Fill",
            "boundary",
        )

        self.fill_algorithm.addItem(
            "Flood Fill",
            "flood",
        )

        self.fill_algorithm.currentIndexChanged.connect(
            self.change_fill_algorithm
        )

        fill_button = QPushButton(
            "Aplicar preenchimento"
        )

        fill_button.clicked.connect(
            lambda: self.set_mode(
                "fill",
                "Preenchimento",
            )
        )

        help_label = QLabel(
            "Selecione o algoritmo e clique "
            "dentro da região fechada."
        )

        help_label.setWordWrap(True)

        layout.addWidget(
            self.fill_algorithm
        )

        layout.addWidget(
            fill_button
        )

        layout.addWidget(
            help_label
        )

        return group

    def create_selection_group(self):
        group = QGroupBox("Seleção")
        layout = QVBoxLayout(group)

        select_button = QPushButton(
            "Selecionar por região"
        )

        select_button.clicked.connect(
            lambda: self.set_mode(
                "select",
                "Seleção retangular",
            )
        )

        layout.addWidget(select_button)

        return group

    def create_transform_group(self):
        group = QGroupBox(
            "Transformações 2D"
        )

        layout = QVBoxLayout(group)

        translation_layout = QHBoxLayout()

        self.tx = self.create_spinbox(
            -1000,
            1000,
            20,
        )

        self.ty = self.create_spinbox(
            -1000,
            1000,
            20,
        )

        translation_layout.addWidget(
            QLabel("X")
        )

        translation_layout.addWidget(
            self.tx
        )

        translation_layout.addWidget(
            QLabel("Y")
        )

        translation_layout.addWidget(
            self.ty
        )

        translate_button = QPushButton(
            "Aplicar translação"
        )

        translate_button.clicked.connect(
            self.apply_translation
        )

        layout.addWidget(
            QLabel("Translação")
        )

        layout.addLayout(
            translation_layout
        )

        layout.addWidget(
            translate_button
        )

        rotation_layout = QHBoxLayout()

        self.angle = self.create_spinbox(
            -360,
            360,
            45,
        )

        rotation_layout.addWidget(
            QLabel("Graus")
        )

        rotation_layout.addWidget(
            self.angle
        )

        rotate_button = QPushButton(
            "Aplicar rotação"
        )

        rotate_button.clicked.connect(
            self.apply_rotation
        )

        layout.addWidget(
            QLabel("Rotação")
        )

        layout.addLayout(
            rotation_layout
        )

        layout.addWidget(
            rotate_button
        )

        scale_layout = QHBoxLayout()

        self.sx = self.create_spinbox(
            -10,
            10,
            1.5,
        )

        self.sy = self.create_spinbox(
            -10,
            10,
            1.5,
        )

        scale_layout.addWidget(
            QLabel("X")
        )

        scale_layout.addWidget(
            self.sx
        )

        scale_layout.addWidget(
            QLabel("Y")
        )

        scale_layout.addWidget(
            self.sy
        )

        scale_button = QPushButton(
            "Aplicar escala"
        )

        scale_button.clicked.connect(
            self.apply_scale
        )

        layout.addWidget(
            QLabel("Escala")
        )

        layout.addLayout(
            scale_layout
        )

        layout.addWidget(
            scale_button
        )

        reflection_layout = QHBoxLayout()

        reflect_x = QPushButton("Refletir X")
        reflect_y = QPushButton("Refletir Y")
        reflect_xy = QPushButton("Refletir XY")

        reflect_x.clicked.connect(
            lambda: self.apply_reflection(
                "reflect_x"
            )
        )

        reflect_y.clicked.connect(
            lambda: self.apply_reflection(
                "reflect_y"
            )
        )

        reflect_xy.clicked.connect(
            lambda: self.apply_reflection(
                "reflect_xy"
            )
        )

        reflection_layout.addWidget(
            reflect_x
        )

        reflection_layout.addWidget(
            reflect_y
        )

        reflection_layout.addWidget(
            reflect_xy
        )

        layout.addWidget(
            QLabel("Reflexões")
        )

        layout.addLayout(
            reflection_layout
        )

        return group

    def create_clipping_group(self):
        group = QGroupBox("Recorte")
        layout = QVBoxLayout(group)

        self.clipping_algorithm = QComboBox()

        self.clipping_algorithm.addItem(
            "Cohen-Sutherland",
            "cohen",
        )

        self.clipping_algorithm.addItem(
            "Liang-Barsky",
            "liang",
        )

        self.clipping_algorithm.currentIndexChanged.connect(
            self.change_clipping_algorithm
        )

        clip_button = QPushButton(
            "Definir janela de recorte"
        )

        clip_button.clicked.connect(
            lambda: self.set_mode(
                "clip",
                "Janela de recorte",
            )
        )

        remove_button = QPushButton(
            "Remover recorte"
        )

        remove_button.clicked.connect(
            self.remove_clipping
        )

        layout.addWidget(
            self.clipping_algorithm
        )

        layout.addWidget(
            clip_button
        )

        layout.addWidget(
            remove_button
        )

        return group

    def create_spinbox(
        self,
        minimum,
        maximum,
        value,
    ):
        spinbox = QDoubleSpinBox()

        spinbox.setRange(
            minimum,
            maximum,
        )

        spinbox.setValue(value)
        spinbox.setDecimals(2)

        return spinbox

    def choose_line_color(self):
        color = QColorDialog.getColor(
            QColor(
                self.canvas.current_color
            ),
            self,
            "Escolha a cor do desenho",
        )

        if not color.isValid():
            return

        color_name = color.name()

        self.canvas.set_current_color(
            color_name
        )

        text_color = self.get_text_color(
            color
        )

        self.line_color_button.setStyleSheet(
            f"background-color: {color_name};"
            f"color: {text_color};"
        )

    def choose_fill_color(self):
        color = QColorDialog.getColor(
            QColor(
                self.canvas.current_fill_color
            ),
            self,
            "Escolha a cor do preenchimento",
        )

        if not color.isValid():
            return

        color_name = color.name()

        self.canvas.set_fill_color(
            color_name
        )

        text_color = self.get_text_color(
            color
        )

        self.fill_color_button.setStyleSheet(
            f"background-color: {color_name};"
            f"color: {text_color};"
        )

    def get_text_color(self, color):
        brightness = (
            color.red() * 299
            + color.green() * 587
            + color.blue() * 114
        ) / 1000

        if brightness > 128:
            return "black"

        return "white"

    def set_mode(
    self,
    mode,
    description,
):
        self.canvas.set_mode(mode)

        self.active_tool_label.setText(
            f"Ferramenta ativa: {description}"
        )

        self.statusBar().showMessage(
            f"Ferramenta atual: {description}"
        )

    def change_line_algorithm(self):
        self.canvas.set_line_algorithm(
            self.line_algorithm.currentData()
        )

    def change_fill_algorithm(self):
        self.canvas.set_fill_algorithm(
            self.fill_algorithm.currentData()
        )

    def change_clipping_algorithm(self):
        self.canvas.set_clipping_algorithm(
            self.clipping_algorithm.currentData()
        )

    def check_selection(self):
        if not self.canvas.selected_objects:
            QMessageBox.warning(
                self,
                "Seleção",
                "Selecione um objeto primeiro.",
            )

            return False

        return True

    def apply_translation(self):
        if not self.check_selection():
            return

        self.canvas.transform_selected(
            "translate",
            self.tx.value(),
            self.ty.value(),
        )

    def apply_rotation(self):
        if not self.check_selection():
            return

        self.canvas.transform_selected(
            "rotate",
            self.angle.value(),
        )

    def apply_scale(self):
        if not self.check_selection():
            return

        self.canvas.transform_selected(
            "scale",
            self.sx.value(),
            self.sy.value(),
        )

    def apply_reflection(
        self,
        operation,
    ):
        if not self.check_selection():
            return

        self.canvas.transform_selected(
            operation
        )

    def remove_clipping(self):
        self.canvas.clip_rect = None
        self.canvas.update()

        self.statusBar().showMessage(
            "Janela de recorte removida."
        )