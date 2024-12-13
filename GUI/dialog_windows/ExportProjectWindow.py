from pathlib import Path

from PyQt6.QtWidgets import QFileDialog

from Domain.project.Project import Project
from Domain.project.ProjectFileManager import ProjectFileManager


class ExportProjectWindow:

    @staticmethod
    def export_project_window(project: Project) -> None:
        file_picker = QFileDialog()
        file_picker.setModal(True)
        file_picker.setDirectory(str(Path.home()))
        project_path_str = file_picker.getSaveFileName(filter="OTLWizard project files (*.otlw)")[0]
        if not project_path_str:
            return

        if not project_path_str.endswith('.otlw'):
            project_path_str += '.otlw'

        project_path = Path(project_path_str)
        ProjectFileManager.export_project_to_file(file_path=project_path, project=project)