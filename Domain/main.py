import sys
import gettext

from datetime import datetime

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QStyle

from Domain.database import Database
from GUI.home_screen import HomeScreen


def initialize_database():
    db = Database()
    db.create_connection(":memory:")
    return db


def mockData(database):
    database.add_project('testen', 'test', 'test', datetime(2021, 9, 11, 12, 30, 0))
    database.add_project('test2', 'test2', 'test2', datetime(2022, 4, 3, 23, 59, 59))
    database.add_project('test3', 'test3', 'test3', datetime(2020, 1, 1, 0, 0, 0))


if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        app_icon = QIcon('../img/wizard.ico')
        app.setWindowIcon(app_icon)
        db = initialize_database()
        mockData(db)
        with open('custom.qss', 'r') as file:
            app.setStyleSheet(file.read())
        window = HomeScreen(db)
        window.resize(1920, 1080)
        window.setWindowTitle("OTLWizard")
        window.setMinimumSize(1280, 720)
        sys.exit(app.exec())
    except Exception as e:
        print(e)
