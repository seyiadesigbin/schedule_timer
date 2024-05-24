import sys
from main_window import MainWindow
from PySide6.QtWidgets import QApplication
from globals import load_stylesheet

APP_STYLESHEET_FILE_NAME = "app_stylesheet.qss"

stylesheet = load_stylesheet(APP_STYLESHEET_FILE_NAME)

# print(f"Without resolve: {__file__}")
# print(f"With resolve: {Path(__file__).resolve()}")
# print(f"Parent with resolve: {Path(__file__).parent.resolve()}")
# print(f"Parent without resolve: {Path(__file__).parent}")

if __name__ == '__main__':

    app = QApplication(sys.argv)

    # app.setStyle('Fusion')
    app.setStyleSheet(stylesheet)

    window = MainWindow(app)

    window.show()
    app.exec()
