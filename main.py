import sys

from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow


def main():
    print("Iniciando aplicação...")

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    print("Janela criada.")

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())