from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QDialogButtonBox

from otlmow_gui.Domain.project.Project import Project


class RemoveProjectFilesWindow:

    def __init__(self, project: Project, language_settings):
        self.project = project
        self._ = language_settings
        self.init_ui()

    def init_ui(self):
        dialog = QDialog()
        dialog.setModal(True)
        dialog.setWindowTitle(self._("remove_project_files_title"))
        layout = QVBoxLayout()
        question_label = QLabel()
        question_label.setText(self._("remove_project_files_question"))
        layout.addWidget(question_label)
        button_box = self.create_button_box()
        button_box.accepted.connect(lambda: self.remove_project_files(dialog))
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        dialog.setLayout(layout)
        dialog.show()
        dialog.exec()

    def create_button_box(self):
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.setProperty("class", "button-box")
        button_box.button(QDialogButtonBox.StandardButton.Ok).setProperty("class", "primary-button")
        button_box.button(QDialogButtonBox.StandardButton.Ok).setText(self._("submit"))
        button_box.button(QDialogButtonBox.StandardButton.Cancel).setProperty("class", "secondary-button")
        button_box.button(QDialogButtonBox.StandardButton.Cancel).setText(self._("cancel"))
        return button_box

    def remove_project_files(self, dialog):
        self.project.remove_all_project_files()
        dialog.close()

