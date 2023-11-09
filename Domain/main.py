import logging
import sys
import typing

from datetime import datetime

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

from Domain.database import Database
from Domain.navigation import Navigation
from GUI.Screens.asset_data_change_screen import AssetDataChangeScreen
from GUI.Screens.conversion_screen import ConversionScreen
from GUI.Screens.export_data_screen import ExportDataScreen
from GUI.Screens.home_screen import HomeScreen
from GUI.Screens.insert_data_screen import InsertDataScreen
from GUI.Screens.template_screen import TemplateScreen
from GUI.Screens.relation_change_screen import RelationChangeScreen
from GUI.TabWidget import TableWidget


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
        step2 = InsertDataScreen(db)
        step3_data = AssetDataChangeScreen(db)
        step3_relations = RelationChangeScreen(db)
        tabWidgetTryOut = TableWidget(db)
        step4_export = ExportDataScreen(db)
        step4_conversion = ConversionScreen(db)
        stacked_widget = Navigation()
        stacked_widget.add_widget(home_screen)
        stacked_widget.add_widget(step1, True)
        stacked_widget.add_widget(step2, True)
        stacked_widget.add_widget(step3_data, True)
        stacked_widget.add_widget(step3_relations, True)
        stacked_widget.add_widget(tabWidgetTryOut, True)
        # stacked_widget.add_widget(step4_export, True)
        # stacked_widget.add_widget(step4_conversion, True)
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
