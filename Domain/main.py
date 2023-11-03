import logging
import sys
import typing

from datetime import datetime

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QStackedWidget

from Domain.database import Database
from Domain.navigation import Navigation
from GUI.home_screen import HomeScreen
from GUI.make_template_screen import TemplateScreen


def initialize_database():
    db = Database()
    db.create_connection(":memory:")
    return db


def mockData(database):
    database.add_project('testen', 'test', 'test', datetime(2021, 9, 11, 12, 30, 0))
    database.add_project('test2', 'test2', 'test2', datetime(2022, 4, 3, 23, 59, 59))
    database.add_project('test3', 'test3', 'test3', datetime(2020, 1, 1, 0, 0, 0))


class MyApplication(QApplication):
    def __init__(self, argv: typing.List[str], db):
        super().__init__(argv)
        self.db = db

    def quit(self):
        self.db.close_connection()
        super().quit()


if __name__ == '__main__':
    try:
        logging.basicConfig(
            format='%(asctime)s %(levelname)-8s %(message)s',
            level=logging.DEBUG,
            datefmt='%Y-%m-%d %H:%M:%S')
        db = initialize_database()
        app = MyApplication(sys.argv, db)
        app_icon = QIcon('../img/wizard.ico')
        app.setWindowIcon(app_icon)
        mockData(db)
        with open('custom.qss', 'r') as file:
            app.setStyleSheet(file.read())
        home_screen = HomeScreen(db)
        step1 = TemplateScreen(db)
        stacked_widget = Navigation()
        stacked_widget.add_widget(step1)
        stacked_widget.add_widget(home_screen)
        home_screen.table.stacked_widget = stacked_widget
        step1.stacked_widget = stacked_widget
        stacked_widget.show()
        stacked_widget.resize(1920, 1080)
        stacked_widget.setWindowTitle('OTLWizard')
        stacked_widget.setMinimumSize(1280, 720)
        app.exec()
        app.quit()
    except Exception as e:
        logging.error(e)
