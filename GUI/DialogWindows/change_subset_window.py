from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialogButtonBox, QDialog, QVBoxLayout, QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton, \
    QFileDialog
import qtawesome as qta

from Domain.home_domain import HomeDomain


class ChangeSubsetWindow:

    def __init__(self, language_settings):
        self.home_domain = HomeDomain(language_settings)
        self._ = language_settings

    def change_subset_window(self, project, stacked_widget):
        dialog = QDialog()
        dialog.setModal(True)
        dialog.setMinimumWidth(700)
        dialog.setWindowTitle(self._("change_subset"))
        layout = QVBoxLayout()

        frame = QFrame()
        horizontal_layout = QHBoxLayout()
        label = QLabel(self._("subset") + ":")
        input_subset = QLineEdit()
        input_subset.setReadOnly(True)
        input_subset.setText(str(project.subset_path))
        file_picker_btn = QPushButton()
        file_picker_btn.setIcon(qta.icon('mdi.folder-open-outline'))
        file_picker_btn.clicked.connect(lambda: self.open_file_picker(input_subset))
        horizontal_layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignLeft)
        horizontal_layout.addWidget(input_subset)
        horizontal_layout.addWidget(file_picker_btn)
        frame.setLayout(horizontal_layout)
        button_box = self.create_button_box()
        button_box.accepted.connect(
            lambda: self.home_domain.change_subset(project, input_subset.text(), dialog, stacked_widget))
        button_box.rejected.connect(dialog.reject)

        layout.addWidget(frame)
        layout.addWidget(button_box)
        dialog.setLayout(layout)
        dialog.show()
        dialog.exec()
        stacked_widget.reset_ui(self._)

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
