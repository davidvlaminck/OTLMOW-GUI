import sys

from PyQt6.QtWidgets import QApplication
from GUI.home_screen import HomeScreen
from database import Database

if __name__ == '__main__':
    app = QApplication(sys.argv)
    #Initialiseren van Database
    db = Database()
    #Momenteel met test database
    db.create_test_connection()
    with open('custom.qss', 'r') as file:
        app.setStyleSheet(file.read())
    window = HomeScreen()
    window.resize(1920, 1080)
    window.setWindowTitle("OTLWizard")
    window.setMinimumSize(1280, 720)
    sys.exit(app.exec())