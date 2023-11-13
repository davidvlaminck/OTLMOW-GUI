import logging
import sys
import typing

from datetime import datetime
from pathlib import Path

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

from Domain.Project import Project
from Domain.ProjectFileManager import ProjectFileManager
from Domain.database import Database
from Domain.navigation import Navigation
from GUI.Screens.asset_data_change_screen import AssetDataChangeScreen
from GUI.Screens.conversion_screen import ConversionScreen
from GUI.Screens.export_data_screen import ExportDataScreen
from GUI.Screens.home_screen import HomeScreen
from GUI.Screens.insert_data_screen import InsertDataScreen
from GUI.Screens.template_screen import TemplateScreen
from GUI.Screens.relation_change_screen import RelationChangeScreen
from GUI.tab_widget import TableWidget

ROOT_DIR = Path(__file__).parent.parent

project_dir = ROOT_DIR / 'demo_projects/'


def initialize_database():
    db = Database()
    db.create_connection(":memory:")
    return db


def mockData(database):
    database.add_project('testen', 'test', 'test', datetime(2021, 9, 11, 12, 30, 0))
    database.add_project('test2', 'test2', 'test2', datetime(2022, 4, 3, 23, 59, 59))
    database.add_project('test3', 'test3', 'test3', datetime(2020, 1, 1, 0, 0, 0))


# Used to add demo data to the application for showcase purpose only
def demo_data():
    project_1 = Project(
        project_path=Path(Path.home() / 'OTLWizardProjects' / 'project_1'),
        subset_path=Path(project_dir / 'project_1' / 'FlitspaalTest.db'),
        assets_path=Path(project_dir / 'project_1' / 'assets.json'),
        eigen_referentie="test1",
        bestek="test_bestek1",
        laatst_bewerkt=datetime(2021, 9, 11))
    ProjectFileManager().save_project_to_dir(project_1)
    ProjectFileManager().delete_project(project_1)


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
        demo_data()
        app = MyApplication(sys.argv, db)
        app_icon = QIcon('../img/wizard.ico')
        app.setWindowIcon(app_icon)
        mockData(db)
        with open('custom.qss', 'r') as file:
            app.setStyleSheet(file.read())
        home_screen = HomeScreen(db)
        step1 = TemplateScreen()
        step1_tabwidget = TableWidget(db, 1, step1, 'template', 'step_1')
        step2 = InsertDataScreen()
        step2_tabwidget = TableWidget(db, 2, step2, 'insert_data', 'step_2')
        step3_data = AssetDataChangeScreen()
        step3_relations = RelationChangeScreen()
        step_3_tabwidget = TableWidget(db, 3, step3_data, 'data_change', 'step_3', step3_relations, 'relation_change')
        step4_export = ExportDataScreen()
        step4_conversion = ConversionScreen()
        step4_tabwidget = TableWidget(db, 4, step4_export, 'export_data', 'step_4', step4_conversion, 'conversion')
        stacked_widget = Navigation()
        stacked_widget.add_widget(home_screen)
        stacked_widget.add_widget(step1_tabwidget, True)
        stacked_widget.add_widget(step2_tabwidget, True)
        stacked_widget.add_widget(step_3_tabwidget, True)
        stacked_widget.add_widget(step4_tabwidget, True)
        home_screen.table.stacked_widget = stacked_widget
        step1.stacked_widget = stacked_widget
        stacked_widget.show()
        stacked_widget.resize(1360, 768)
        stacked_widget.setWindowTitle('OTLWizard')
        stacked_widget.setMinimumSize(1280, 720)
        print(Path(Path.home()) / 'OTLWizardProjects')
        app.exec()
        app.quit()
    except Exception as e:
        logging.error(e)
