import sys

from PyQt6.QtWidgets import QApplication
from GUI.home_screen import HomeScreen

if __name__ == '__main__':
    app = QApplication(sys.argv)
    with open('custom.qss', 'r') as file:
        app.setStyleSheet(file.read())
    window = HomeScreen()
    window.resize(1920, 1080)
    window.setWindowTitle("OTLWizard")
    window.setMinimumSize(1280, 720)
    sys.exit(app.exec())