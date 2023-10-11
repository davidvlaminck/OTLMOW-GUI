import sys

from PyQt6.QtWidgets import QApplication, QWidget
from GUI.home_screen import HomeScreen


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = HomeScreen()
    window.resize(1920, 1080)
    window.setWindowTitle("OTLWizard")
    sys.exit(app.exec())