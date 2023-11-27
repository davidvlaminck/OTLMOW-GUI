import logging
from enum import Enum
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QDialogButtonBox, QLabel, QHBoxLayout, QPushButton, \
    QFileDialog, QFrame

from Domain.Project import Project
from Domain.ProjectFileManager import ProjectFileManager
from Domain.home_domain import HomeDomain
from Domain.language_settings import return_language
from Domain.enums import Language
import qtawesome as qta

from Exceptions.EmptyFieldError import EmptyFieldError

ROOT_DIR = Path(__file__).parent

LANG_DIR = ROOT_DIR.parent / 'locale/'


class DialogWindow:

    # TODO: Opsplitsen in verschillende aparte files in map 'Dialog Windows'
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
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.setProperty("class", "button-box")
        # sends the values off to validate once submitted
        button_box.accepted.connect(
            lambda: self.pass_values_through_validate(input_eigen_ref.text(), input_bestek.text(),
                                                      input_subset.text(), dialog_window, overview_table, project))
        button_box.rejected.connect(dialog_window.reject)
        # Adds the two buttons to the layout
        layout.addWidget(button_box)
        button_box.button(QDialogButtonBox.StandardButton.Ok).setProperty("class", "primary-button")
        button_box.button(QDialogButtonBox.StandardButton.Ok).setText(self._("submit"))
        button_box.button(QDialogButtonBox.StandardButton.Cancel).setProperty("class", "secondary-button")
        button_box.button(QDialogButtonBox.StandardButton.Cancel).setText(self._("cancel"))
        layout.addWidget(self.error_label)
        # Fills the dialog with the created layout
        dialog_window.setLayout(layout)
        # Shows the dialog
        dialog_window.show()
        dialog_window.exec()

    def pass_values_through_validate(self, input_eigen_ref: str, input_bestek: str, input_subset: str, dialog_window,
                                     overview_table,
                                     project: Project = None) -> None:
        try:
            self.home_domain.validate(input_eigen_ref, input_subset)
        except EmptyFieldError as e:
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

    def language_window(self, stacked_widget) -> None:
        dialog = QDialog()
        dialog.setModal(True)
        dialog.setWindowTitle(self._("change_language_title"))
        layout = QHBoxLayout()
        button_ned = QPushButton(self._("language_option_dutch"))
        button_eng = QPushButton(self._("language_option_english"))
        button_ned.clicked.connect(lambda: self.change_language(Language.DUTCH, dialog, stacked_widget))
        button_eng.clicked.connect(lambda: self.change_language(Language.ENGLISH, dialog, stacked_widget))
        layout.addWidget(button_ned)
        layout.addWidget(button_eng)
        dialog.setLayout(layout)
        dialog.show()
        dialog.exec()

    def change_language(self, lang: Enum, dialog: QDialog, stacked_widget) -> None:
        self._ = return_language(LANG_DIR, lang)
        stacked_widget.reset_ui(self._)
        dialog.close()

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

    @staticmethod
    def open_project_file_picker() -> Project:
        file_path = str(Path.home())
        file_picker = QFileDialog()
        file_picker.setWindowTitle("Selecteer een OTL wizard project")
        file_picker.setDirectory(file_path)
        file_picker.setNameFilter("OTLWizard project files (*.otlw)")
        file_picker.setOption(QFileDialog.Option.ShowDirsOnly, True)
        if file_picker.exec():
            project_file_path = Path(file_picker.selectedFiles()[0])
            return ProjectFileManager.load_project_file(file_path=project_file_path)

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

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.button(QDialogButtonBox.StandardButton.Ok).setProperty("class", "primary-button")
        button_box.button(QDialogButtonBox.StandardButton.Ok).setText(self._("submit"))
        button_box.button(QDialogButtonBox.StandardButton.Cancel).setProperty("class", "secondary-button")
        button_box.button(QDialogButtonBox.StandardButton.Cancel).setText(self._("cancel"))
        button_box.accepted.connect(lambda: self.home_domain.change_subset(project, input_subset.text(), dialog, stacked_widget))
        button_box.rejected.connect(dialog.reject)

        layout.addWidget(frame)
        layout.addWidget(button_box)
        dialog.setLayout(layout)
        dialog.show()
        dialog.exec()
        stacked_widget.reset_ui(self._)

    @staticmethod
    def export_window():
        file_picker = QFileDialog()
        file_picker.setModal(True)
        file_picker.setDirectory(str(Path.home()))
        document_loc = file_picker.getSaveFileName(filter="Excel files (*.xlsx);;CSV files (*.csv)")
        if document_loc:
            logging.debug(document_loc)
            return document_loc[0]

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



