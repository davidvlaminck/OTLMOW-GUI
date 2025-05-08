from typing import Callable

from PyQt6.QtWidgets import QMessageBox, QPushButton

from otlmow_gui.Domain.project.Project import Project
from otlmow_gui.Domain.step_domain.HomeDomain import HomeDomain


class RemoveProjectWindow(QMessageBox):

    def __init__(self, language_settings: Callable, project: Project):
        super().__init__()
        self._ = language_settings


        self.setWindowTitle(self._("delete"))
        self.setText(self._("project_deletion_question"))
        self.setIcon(QMessageBox.Icon.Warning)
        self.addButton(QPushButton(self._("yes")), QMessageBox.ButtonRole.YesRole)
        self.addButton(QPushButton(self._("no")), QMessageBox.ButtonRole.NoRole)
        self.exec()
        reply = self.buttonRole(self.clickedButton())
        if reply == QMessageBox.ButtonRole.YesRole:
            HomeDomain.remove_project(project)