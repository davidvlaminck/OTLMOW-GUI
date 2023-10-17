import sys

from PyQt6.QtWidgets import QApplication

from Domain.database import Database
from GUI.home_screen import HomeScreen


def initialize_database():
    db = Database()
    db.create_connection(":memory:")
    return db

def mockData(database):
    database.add_project('testen', 'test', 'test', None)
    database.add_project('test2', 'test2', 'test2', None)
    database.add_project('test3', 'test3', 'test3', None)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    db = initialize_database()
    mockData(db)
    with open('custom.qss', 'r') as file:
        app.setStyleSheet(file.read())
    window = HomeScreen(db)
    window.resize(1920, 1080)
    window.setWindowTitle("OTLWizard")
    window.setMinimumSize(1280, 720)
    sys.exit(app.exec())
