import asyncio
import importlib
import typing

from datetime import datetime
from pathlib import Path

import sys
import os

from otlmow_gui.Domain.ProgramFileStructure import ProgramFileStructure

if sys.platform.startswith("linux"):
    os.environ["QT_QUICK_BACKEND"] = "software" # fixes a flickering issue on some linux systems

from PyQt6 import QtCore

from otlmow_gui.Domain import global_vars
from otlmow_gui.Domain.Settings import Settings
from otlmow_gui.Domain.logger.OTLLogger import OTLLogger
from otlmow_gui.Domain.step_domain import InsertDataDomain
from otlmow_gui.Domain.network.Updater import Updater
from otlmow_gui.GUI.Styling import Styling
from otlmow_gui.GUI.translation.GlobalTranslate import GlobalTranslate
from otlmow_gui.exception_handler.ExceptionHandlers import create_task_reraise_exception, excepthook

ROOT_DIR =  Path(Path(__file__).absolute()).parent
sys.path.insert(0,str(ROOT_DIR.absolute()))# needed for python to import project files



from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication
from qasync import QEventLoop, asyncClose




from otlmow_gui.Domain.project import Project
from otlmow_gui.GUI.MainWindow import MainWindow

project_dir = ROOT_DIR / 'demo_projects/'

# Decide where the locale folder lives
if getattr(sys, 'frozen', False):
    # Running from PyInstaller bundle
    base_path = Path(sys._MEIPASS)  # temp dir PyInstaller unpacks to
else:
    # Running from source
    base_path = ROOT_DIR

LANG_DIR = base_path / 'locale'


    # OTLLogger.logger.info('Splash screen closed.')

# Used to add demo data to the application for showcase purpose only
def demo_data():
    project_1 = Project(eigen_referentie="test1", project_path=Path(
        Path.home() / 'OTLWizardProjects' / 'Projects' / 'project_1'),
                        subset_path=Path(project_dir / 'project_1' / 'Flitspaal_noAgent3.0.db'),
                        saved_documents_overview_path=Path(project_dir / 'project_1'),
                        bestek="test_bestek1", laatst_bewerkt=datetime(2021, 9, 11))
    project_1.save_project_to_dir()
    return project_1


class OTLWizard(QApplication):

    def __init__(self,settings: dict, argv: typing.List[str]):
        super().__init__(argv)
        # Windows will set the colorScheme to Dark if that is the setting of the system
        # We will set it to light no matter what the colorscheme of the system is.
        # if self.styleHints().colorScheme() == Qt.ColorScheme.Dark:
        # self.styleHints().setColorScheme(Qt.ColorScheme.Light)

        sys.excepthook = excepthook


        Updater.update_oltmow_model()

        if '_PYI_SPLASH_IPC' in os.environ and importlib.util.find_spec("pyi_splash"):
            import pyi_splash
            pyi_splash.update_text('UI Loaded ...')
            pyi_splash.close()

        Updater.check_for_OTL_wizard_updates()

        IMG_DIR = ProgramFileStructure.get_dynamic_library_path('img')

        app_icon = QIcon(str(IMG_DIR / 'wizard.ico'))
        self.setWindowIcon(app_icon)

        language = GlobalTranslate(settings, LANG_DIR).get_all()
        global_vars.otl_wizard = self
        self.main_window = MainWindow(language)
        self.main_window.resize(1250, 650)
        self.main_window.setWindowTitle('OTLWizard')
        self.main_window.setMinimumSize(800, 600)
        self.main_window.setWindowFlags(
            self.main_window.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)  # set always on top flag, makes window disappear
        self.main_window.show()



        self.meipass = sys._MEIPASS if hasattr(sys, '_MEIPASS') else None
        Styling.applyStyling(self,self.meipass)
        self.paletteChanged.connect(lambda state: Styling.applyStyling(self,self.meipass))


        # self.demo_project = demo_data()
        self.demo_project = None

        if "--test" in argv:
            self.test_setup()

    def test_setup(self):
        self.main_window.home_screen.table.open_project(2)
        create_task_reraise_exception(InsertDataDomain.load_and_validate_documents())
        self.main_window.setCurrentIndex(3)
        self.main_window.reset_ui(self.main_window._)
        self.main_window.step_3_tabwidget.tabs.setCurrentWidget(self.main_window.step3_relations)

    @asyncClose
    async def quit(self):
        OTLLogger.logger.debug("closing application")
        if self.demo_project:
            self.demo_project.delete_project_dir_by_path()
        super().quit()


def otl_wizard_2_main():
    program_settings = Settings.get_or_create_settings_file()
    OTLLogger.init()
    OTLLogger.logger.debug("Application started")

    app = OTLWizard(program_settings, sys.argv)

    if '_PYI_SPLASH_IPC' in os.environ and importlib.util.find_spec("pyi_splash"):
        import pyi_splash

        pyi_splash.update_text('UI Loaded ...')
        pyi_splash.close()
        OTLLogger.logger.info('Splash screen closed.')

    app.main_window.raise_()
    app.main_window.setWindowFlags(
        app.main_window.windowFlags() & ~QtCore.Qt.WindowStaysOnTopHint)  # clear always on top flag, makes window disappear
    app.main_window.show()
    event_loop = QEventLoop(app)
    asyncio.set_event_loop(event_loop)

    event_loop.run_forever()