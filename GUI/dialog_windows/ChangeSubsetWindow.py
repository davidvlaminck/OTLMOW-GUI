from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialogButtonBox, QDialog, QVBoxLayout, QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton, \
    QFileDialog
import qtawesome as qta

from Domain.step_domain.HomeDomain import HomeDomain
from Exceptions.WrongDatabaseError import WrongDatabaseError


class ChangeSubsetWindow:

    def __init__(self, language_settings):
        self.home_domain = HomeDomain(language_settings)
        self._ = language_settings
        self.error_label = QLabel()
        self.input_subset = QLineEdit()

    def change_subset_window(self, project, main_window):
        dialog = QDialog()
        self.error_label.setText("")
        self.error_label.setStyleSheet("color: red")
        dialog.setModal(True)
        dialog.setMinimumWidth(700)
        dialog.setWindowTitle(self._("change_subset"))
        layout = QVBoxLayout()

        frame = QFrame()
        horizontal_layout = QHBoxLayout()
        label = QLabel(self._("subset") + ":")
        self.input_subset.setReadOnly(True)
        old_project_path = Path(project.project_path)
        self.input_subset.setText(str(project.subset_path))
        file_picker_btn = QPushButton()
        file_picker_btn.setIcon(qta.icon('mdi.folder-open-outline'))
        file_picker_btn.clicked.connect(lambda: self.open_file_picker(self.input_subset))
        horizontal_layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignLeft)
        horizontal_layout.addWidget(self.input_subset)
        horizontal_layout.addWidget(file_picker_btn)
        frame.setLayout(horizontal_layout)
        button_box = self.create_button_box()
        button_box.accepted.connect(
            lambda: self.validate_change_subset(project, dialog, main_window, self.input_subset.text(), old_project_path))
        button_box.rejected.connect(dialog.reject)

        layout.addWidget(frame)
        layout.addWidget(self.error_label)
        layout.addWidget(button_box)
        dialog.setLayout(layout)
        dialog.show()
        dialog.exec()
        main_window.reset_ui(self._)

    def validate_change_subset(self, project, dialog, main_window, input_subset: str, old_project_path: Path):
        try:
            self.home_domain.change_subset(project=project, new_path=input_subset, main_window=main_window)
        except WrongDatabaseError as e:
            self.error_label.setText(str(e))
            self.input_subset.setText(str(old_project_path))
            return
        dialog.close()

    def create_button_box(self):
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.setProperty("class", "button-box")
        button_box.button(QDialogButtonBox.StandardButton.Ok).setProperty("class", "primary-button")
        button_box.button(QDialogButtonBox.StandardButton.Ok).setText(self._("submit"))
        button_box.button(QDialogButtonBox.StandardButton.Cancel).setProperty("class", "secondary-button")
        button_box.button(QDialogButtonBox.StandardButton.Cancel).setText(self._("cancel"))
        return button_box

    @staticmethod
    def open_file_picker(input_subset):
        if input_subset.text() == "":
            file_path = str(Path.home())
        else:
            file_path = input_subset.text()
        file_picker = QFileDialog()
        file_picker.setWindowTitle("Selecteer subset")
        file_picker.setDirectory(file_path)
        file_picker.setNameFilter("Database files (*.db)")
        file_picker.setOption(QFileDialog.Option.ShowDirsOnly, True)
        if file_picker.exec():
            input_subset.setText(file_picker.selectedFiles()[0])
