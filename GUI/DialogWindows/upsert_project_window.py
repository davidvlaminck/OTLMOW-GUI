from enum import Enum
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QDialogButtonBox, \
    QFileDialog

from Domain.Project import Project
from Domain.home_domain import HomeDomain

import qtawesome as qta

from Exceptions.EmptyFieldError import EmptyFieldError
from Exceptions.WrongDatabaseError import WrongDatabaseError


class UpsertProjectWindow:

    def __init__(self, language_settings):
        self.home_domain = HomeDomain(language_settings)
        self.error_label = QLabel()
        self._ = language_settings

    def draw_upsert_project(self, overview_table, project: Project = None):
        is_project = project is not None
        # Resets the error label to empty when reopening the dialog
        self.error_label.setText("")
        dialog_window = QDialog()
        dialog_window.setMinimumWidth(400)
        # Makes the dialog the primary screen, disabling the screen behind it
        dialog_window.setModal(True)
        if is_project:
            dialog_window.setWindowTitle(self._("alter_project_title"))
        else:
            dialog_window.setWindowTitle(self._("new_project_title"))
        # Creates the vertical stack layout
        layout = QVBoxLayout()
        # Creates 3 horizontal layouts for each input field with its label
        container_eigen_ref = QHBoxLayout()
        container_bestek = QHBoxLayout()
        container_subset = QHBoxLayout()
        # Creates labels for the input fields and adds them to the horizontal layouts
        label_eigen_ref = QLabel(self._("own_reference") + ":")
        container_eigen_ref.addWidget(label_eigen_ref, alignment=Qt.AlignmentFlag.AlignLeft)
        label_bestek = QLabel(self._("service_order") + ":")
        container_bestek.addWidget(label_bestek, alignment=Qt.AlignmentFlag.AlignLeft)
        label_subset = QLabel(self._("subset") + ":")
        container_subset.addWidget(label_subset, alignment=Qt.AlignmentFlag.AlignLeft)
        # Creates the input fields
        input_eigen_ref = QLineEdit()
        container_eigen_ref.addWidget(input_eigen_ref)
        input_bestek = QLineEdit()
        container_bestek.addWidget(input_bestek)
        input_subset = QLineEdit()
        input_subset.setReadOnly(True)
        file_picker_btn = QPushButton()
        file_picker_btn.setIcon(qta.icon('mdi.folder-open-outline'))
        file_picker_btn.clicked.connect(lambda: self.open_file_picker(input_subset))
        container_subset.addWidget(input_subset)
        container_subset.addWidget(file_picker_btn)
        input_eigen_ref.setPlaceholderText(self._("own_reference"))
        input_bestek.setPlaceholderText(self._("service_order"))
        input_subset.setPlaceholderText(self._("subset"))
        if is_project:
            input_eigen_ref.setText(project.eigen_referentie)
            input_bestek.setText(project.bestek)
            input_subset.setText(str(project.subset_path))
        # Adds the input fields to the layout
        layout.addLayout(container_eigen_ref)
        layout.addLayout(container_bestek)
        layout.addLayout(container_subset)

        # Changes the color of the error label to red
        self.error_label.setStyleSheet("color: red")

        # Creates the button box
        button_box = self.create_button_box()
        # sends the values off to validate once submitted
        button_box.accepted.connect(
            lambda: self.pass_values_through_validate(input_eigen_ref.text(), input_bestek.text(),
                                                      input_subset.text(), dialog_window, overview_table, project))
        button_box.rejected.connect(dialog_window.reject)
        # Adds the two buttons to the layout
        layout.addWidget(button_box)
        layout.addWidget(self.error_label)
        # Fills the dialog with the created layout
        dialog_window.setLayout(layout)
        # Shows the dialog
        dialog_window.show()
        dialog_window.exec()

    def create_button_box(self):
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.setProperty("class", "button-box")
        button_box.button(QDialogButtonBox.StandardButton.Ok).setProperty("class", "primary-button")
        button_box.button(QDialogButtonBox.StandardButton.Ok).setText(self._("submit"))
        button_box.button(QDialogButtonBox.StandardButton.Cancel).setProperty("class", "secondary-button")
        button_box.button(QDialogButtonBox.StandardButton.Cancel).setText(self._("cancel"))
        return button_box

    def pass_values_through_validate(self, input_eigen_ref: str, input_bestek: str, input_subset: str, dialog_window,
                                     overview_table,
                                     project: Project = None) -> None:
        try:
            self.home_domain.validate(input_eigen_ref, input_bestek, input_subset)
        except EmptyFieldError as e:
            self.error_label.setText(str(e))
            return
        except WrongDatabaseError as e:
            self.error_label.setText(str(e))
            return
        self.error_label.setText("")
        if project is None:
            project = Project()
        project.eigen_referentie = input_eigen_ref
        project.bestek = input_bestek
        project.subset_path = Path(input_subset)
        self.home_domain.alter_table(dlg=dialog_window,
                                     overview_table=overview_table, project=project)

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
