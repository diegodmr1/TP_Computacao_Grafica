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
)

from ui.canvas import Canvas


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("TP_CG - Diego Moreira")
        self.resize(1200, 750)

        self.canvas = Canvas()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)

        controls = self.create_controls()

        main_layout.addWidget(controls)
        main_layout.addWidget(self.canvas, 1)

        self.statusBar().showMessage(
            "Selecione uma ferramenta e utilize o mouse na área de desenho."
        )

    def create_controls(self):
        panel = QWidget()
        panel.setMaximumWidth(320)

        layout = QVBoxLayout(panel)

        title = QLabel("TP_CG - Diego Moreira")
        title.setStyleSheet(
            "font-size: 18px; font-weight: bold; margin: 8px;"
        )

        layout.addWidget(title)

        layout.addWidget(self.create_drawing_group())
        layout.addWidget(self.create_rasterization_group())
        layout.addWidget(self.create_selection_group())
        layout.addWidget(self.create_transform_group())
        layout.addWidget(self.create_clipping_group())

        clear_button = QPushButton("Limpar área de desenho")
        clear_button.clicked.connect(self.canvas.clear_canvas)

        layout.addWidget(clear_button)
        layout.addStretch()

        return panel

    def create_drawing_group(self):
        group = QGroupBox("Objetos")
        layout = QVBoxLayout(group)

        line_button = QPushButton("Reta")
        circle_button = QPushButton("Circunferência")
        polygon_button = QPushButton("Polígono")

        line_button.clicked.connect(
            lambda: self.set_mode("line", "Reta")
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

        polygon_help = QLabel(
            "Polígono: clique nos vértices e use o botão direito para finalizar."
        )
        polygon_help.setWordWrap(True)

        layout.addWidget(polygon_help)

        return group

    def create_rasterization_group(self):
        group = QGroupBox("Rasterização de Retas")
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

        layout.addWidget(self.line_algorithm)

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
        group = QGroupBox("Transformações 2D")
        layout = QVBoxLayout(group)

        translate_label = QLabel("Translação")

        translation_layout = QHBoxLayout()

        self.tx = self.create_spinbox(-1000, 1000, 20)
        self.ty = self.create_spinbox(-1000, 1000, 20)

        translation_layout.addWidget(QLabel("X"))
        translation_layout.addWidget(self.tx)

        translation_layout.addWidget(QLabel("Y"))
        translation_layout.addWidget(self.ty)

        translate_button = QPushButton("Aplicar translação")
        translate_button.clicked.connect(
            self.apply_translation
        )

        layout.addWidget(translate_label)
        layout.addLayout(translation_layout)
        layout.addWidget(translate_button)

        rotation_label = QLabel("Rotação")

        rotation_layout = QHBoxLayout()

        self.angle = self.create_spinbox(
            -360,
            360,
            45,
        )

        rotation_layout.addWidget(QLabel("Graus"))
        rotation_layout.addWidget(self.angle)

        rotate_button = QPushButton("Aplicar rotação")
        rotate_button.clicked.connect(
            self.apply_rotation
        )

        layout.addWidget(rotation_label)
        layout.addLayout(rotation_layout)
        layout.addWidget(rotate_button)

        scale_label = QLabel("Escala")

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

        scale_layout.addWidget(QLabel("X"))
        scale_layout.addWidget(self.sx)

        scale_layout.addWidget(QLabel("Y"))
        scale_layout.addWidget(self.sy)

        scale_button = QPushButton("Aplicar escala")
        scale_button.clicked.connect(
            self.apply_scale
        )

        layout.addWidget(scale_label)
        layout.addLayout(scale_layout)
        layout.addWidget(scale_button)

        reflection_layout = QHBoxLayout()

        reflect_x_button = QPushButton("Refletir X")
        reflect_y_button = QPushButton("Refletir Y")
        reflect_xy_button = QPushButton("Refletir XY")

        reflect_x_button.clicked.connect(
            lambda: self.apply_reflection(
                "reflect_x"
            )
        )

        reflect_y_button.clicked.connect(
            lambda: self.apply_reflection(
                "reflect_y"
            )
        )

        reflect_xy_button.clicked.connect(
            lambda: self.apply_reflection(
                "reflect_xy"
            )
        )

        reflection_layout.addWidget(
            reflect_x_button
        )

        reflection_layout.addWidget(
            reflect_y_button
        )

        reflection_layout.addWidget(
            reflect_xy_button
        )

        layout.addWidget(QLabel("Reflexões"))
        layout.addLayout(reflection_layout)

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

        remove_clip_button = QPushButton(
            "Remover recorte"
        )

        remove_clip_button.clicked.connect(
            self.remove_clipping
        )

        layout.addWidget(
            self.clipping_algorithm
        )

        layout.addWidget(clip_button)
        layout.addWidget(remove_clip_button)

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

    def set_mode(self, mode, description):
        self.canvas.set_mode(mode)

        self.statusBar().showMessage(
            f"Ferramenta atual: {description}"
        )

    def change_line_algorithm(self):
        algorithm = (
            self.line_algorithm.currentData()
        )

        self.canvas.set_line_algorithm(
            algorithm
        )

        self.canvas.update()

    def change_clipping_algorithm(self):
        algorithm = (
            self.clipping_algorithm.currentData()
        )

        self.canvas.set_clipping_algorithm(
            algorithm
        )

        self.canvas.update()

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

    def apply_reflection(self, operation):
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