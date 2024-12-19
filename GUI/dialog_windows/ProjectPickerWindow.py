from pathlib import Path

from PyQt6.QtWidgets import QFileDialog

from Domain.project.Project import Project
from Domain.project.ProgramFileManager import ProgramFileManager


class ProjectPickerWindow:

    def __init__(self, language_settings):
        self._ = language_settings

    def open_project_file_picker(self) -> Project:
        file_path = str(Path.home())
        file_picker = QFileDialog()
        file_picker.setWindowTitle(self._("select_OTL_project"))
        file_picker.setDirectory(file_path)
        file_picker.setNameFilter("OTLWizard project files (*.otlw)")
        file_picker.setOption(QFileDialog.Option.ShowDirsOnly, True)
        if file_picker.exec():
            project_file_path = Path(file_picker.selectedFiles()[0])
            return Project.import_project(file_path=project_file_path)