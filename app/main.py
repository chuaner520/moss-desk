import sys
from PySide6.QtWidgets import QApplication
# import qdarkstyle
from app.router import MainWindow


def main():
    app = QApplication(sys.argv)
    # app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 