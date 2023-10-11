import sys

from PyQt6.QtWidgets import QApplication, QWidget
from GUI.home_screen import HomeScreen
from qt_material import apply_stylesheet

if __name__ == '__main__':
    app = QApplication(sys.argv)
    with open('custom.css', 'r') as file:
        app.setStyleSheet(file.read())
    window = HomeScreen()
    window.resize(1920, 1080)
    window.setWindowTitle("OTLWizard")
    apply_stylesheet(app, theme='custom_theme.xml', css_file='custom.css')
    sys.exit(app.exec())
