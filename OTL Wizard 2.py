import argparse
import asyncio
import importlib
import logging
import os
import sys
import traceback
import typing

from datetime import datetime
from pathlib import Path

from Domain import global_vars
from Domain.InsertDataDomain import InsertDataDomain
from Domain.Updater import Updater
from GUI.translation.GlobalTranslate import GlobalTranslate

ROOT_DIR =  Path(Path(__file__).absolute()).parent
sys.path.insert(0,str(ROOT_DIR.absolute()))# needed for python to import project files

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication
from qasync import QEventLoop, asyncClose

from Domain.Project import Project
from Domain.ProjectFileManager import ProjectFileManager
from GUI.MainWindow import MainWindow
from GUI.Screens.ErrorScreen import ErrorScreen


project_dir = ROOT_DIR / 'demo_projects/'

LANG_DIR = ROOT_DIR / 'locale/'



# Used to add demo data to the application for showcase purpose only
def demo_data():
    project_1 = Project(
        project_path=Path(Path.home() / 'OTLWizardProjects' / 'Projects' / 'project_1'),
        subset_path=Path(project_dir / 'project_1' / 'Flitspaal_noAgent3.0.db'),
        assets_path=Path(project_dir / 'project_1'),
        eigen_referentie="test1",
        bestek="test_bestek1",
        laatst_bewerkt=datetime(2021, 9, 11))
    ProjectFileManager.save_project_to_dir(project_1)
    return project_1


class OTLWizard(QApplication):

    def __init__(self,settings: dict, argv: typing.List[str]):
        super().__init__(argv)

        sys.excepthook = excepthook

        Updater.check_for_updates()

        app_icon = QIcon('img/wizard.ico')
        self.setWindowIcon(app_icon)

        style_path = Path('style/custom.qss')

        if hasattr(sys, '_MEIPASS'): # when in .exe file
            style_path = Path(os.path.join(sys._MEIPASS,'style/custom.qss'))
        elif not style_path.exists():
            style_path = Path('data/style/custom.qss')


        with open(style_path, 'r') as file:
            self.setStyleSheet(file.read())

        logging.debug(f"style sheet found in: {str(style_path.absolute())}")

        # self.demo_project = demo_data()
        self.demo_project = None

        language = GlobalTranslate(settings,LANG_DIR).get_all()

        self.main_window = MainWindow(language)

        self.main_window.resize(1250, 650)
        self.main_window.setWindowTitle('OTLWizard')
        self.main_window.setMinimumSize(800, 600)
        self.main_window.show()
        global_vars.otl_wizard = self

        if "--test" in argv:
            self.test_setup()

    def test_setup(self):
        self.main_window.home_screen.table.open_project_async_task(2)
        InsertDataDomain.load_and_validate_documents()
        self.main_window.setCurrentIndex(3)
        self.main_window.reset_ui(self.main_window._)
        self.main_window.step_3_tabwidget.tabs.setCurrentWidget(self.main_window.step3_relations)

    @asyncClose
    async def quit(self):
        logging.debug("closing application")
        if self.demo_project:
            ProjectFileManager.delete_project_files_by_path(self.demo_project.project_path)
        super().quit()

def excepthook(exc_type, exc_value, exc_tb):
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    logging.error("error caught!")
    logging.error("error message: \n: " + tb)
    error_screen = ErrorScreen(tb)
    error_screen.show()
    # QApplication.quit()


if __name__ == '__main__':
    settings = ProjectFileManager.init()

    logging.debug("Application started")

    app = OTLWizard(settings,sys.argv)

    if '_PYI_SPLASH_IPC' in os.environ and importlib.util.find_spec("pyi_splash"):
        import pyi_splash

        pyi_splash.update_text('UI Loaded ...')
        pyi_splash.close()
        logging.info('Splash screen closed.')

    event_loop = QEventLoop(app)
    asyncio.set_event_loop(event_loop)

    event_loop.run_forever()



