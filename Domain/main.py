import asyncio
import logging
import sys
import typing

from datetime import datetime
from pathlib import Path

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication
from qasync import QEventLoop, asyncClose

from Domain.Project import Project
from Domain.ProjectFileManager import ProjectFileManager
from Domain.navigation import Navigation

ROOT_DIR = Path(__file__).parent.parent

project_dir = ROOT_DIR / 'demo_projects/'


# Used to add demo data to the application for showcase purpose only
def demo_data():
    project_1 = Project(
        project_path=Path(Path.home() / 'OTLWizardProjects' / 'Projects' / 'project_1'),
        subset_path=Path(project_dir / 'project_1' / 'Flitspaal_noAgent3.0.db'),
        assets_path=Path(project_dir / 'project_1' / 'assets.json'),
        eigen_referentie="test1",
        bestek="test_bestek1",
        laatst_bewerkt=datetime(2021, 9, 11))
    ProjectFileManager().save_project_to_dir(project_1)
    return project_1


class MyApplication(QApplication):
    def __init__(self, argv: typing.List[str]):
        super().__init__(argv)
        self.demo_project = demo_data()

    @asyncClose
    async def quit(self):
        logging.debug("closing application")
        ProjectFileManager().delete_project_files_by_path(self.demo_project.project_path)
        super().quit()


if __name__ == '__main__':
    try:
        logging.basicConfig(
            format='%(asctime)s %(levelname)-8s %(message)s',
            level=logging.DEBUG,
            datefmt='%Y-%m-%d %H:%M:%S')
        app = MyApplication(sys.argv)
        event_loop = QEventLoop(app)
        asyncio.set_event_loop(event_loop)
        app_icon = QIcon('../img/wizard.ico')
        app.setWindowIcon(app_icon)
        with open('custom.qss', 'r') as file:
            app.setStyleSheet(file.read())
        stacked_widget = Navigation()
        stacked_widget.show()
        future = event_loop.create_future()
        stacked_widget.resize(1360, 768)
        stacked_widget.setWindowTitle('OTLWizard')
        stacked_widget.setMinimumSize(1280, 720)
        event_loop.run_until_complete(future)
        app.exec()
        app.quit()
        # event_loop.close()
    except Exception as e:
        logging.error(e)
