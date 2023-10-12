import sys

from PyQt6.QtWidgets import QApplication, QWidget
from GUI.home_screen import HomeScreen
from qt_material import apply_stylesheet

if __name__ == '__main__':
    app = QApplication(sys.argv)
    with open('custom.qss', 'r') as file:
        app.setStyleSheet(file.read())
    window = HomeScreen()
    window.resize(1920, 1080)
    window.setWindowTitle("OTLWizard")
    sys.exit(app.exec())
