from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialogButtonBox, QDialog, QVBoxLayout, QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton
import qtawesome as qta

from otlmow_gui.Domain import global_vars
from otlmow_gui.Domain.step_domain.HomeDomain import HomeDomain
from otlmow_gui.Exceptions.WrongDatabaseError import WrongDatabaseError
from otlmow_gui.GUI.dialog_windows.file_picker_dialog.SubsetLoadFilePickerDialog import \
    SubsetLoadFilePickerDialog


class ChangeSubsetWindow(QDialog):

    def __init__(self, language_settings):
        super().__init__()
        self._ = language_settings

        project = global_vars.current_project

        self.setModal(True)
        self.setMinimumWidth(700)
        self.setWindowTitle(self._("change_subset"))

        layout = QVBoxLayout()

        frame = QFrame()
        horizontal_layout = QHBoxLayout()

        self.subset_label = QLabel(self._("subset") + ":")

        self.input_subset = QLineEdit()
        self.input_subset.setReadOnly(True)
        self.input_subset.setText(str(project.subset_path))

        file_picker_btn = QPushButton()
        file_picker_btn.setIcon(qta.icon('mdi.folder-open-outline'))
        file_picker_btn.clicked.connect(lambda: self.open_file_picker(self.input_subset))

        horizontal_layout.addWidget(self.subset_label, alignment=Qt.AlignmentFlag.AlignLeft)
        horizontal_layout.addWidget(self.input_subset)
        horizontal_layout.addWidget(file_picker_btn)

        frame.setLayout(horizontal_layout)
        layout.addWidget(frame)

        self.error_label = QLabel()
        self.error_label.setText("")
        self.error_label.setStyleSheet("color: red")

        button_box = self.create_button_box()
        button_box.accepted.connect(
            lambda: self.validate_change_subset(input_subset=self.input_subset.text(), old_project_path=project.project_path))
        button_box.rejected.connect(self.reject)

        layout.addWidget(self.error_label)
        layout.addWidget(button_box)
        self.setLayout(layout)

        self.show()
        self.exec()

    def validate_change_subset(self, input_subset: str, old_project_path: Path) -> None:
        """
        Validates and applies a change to the current subset.

        This function attempts to change the subset to the specified input path. If the change is
        unsuccessful due to a WrongDatabaseError, it updates the error label with the error message
        and resets the input field to the old project path.

        Args:
            self: The instance of the class.
            input_subset (str): The new subset path to be validated and applied.
            old_project_path (Path): The path of the old project to revert to in case of an error.

        Returns:
            None
        """

        try:
            HomeDomain.change_subset(new_path=input_subset)
        except WrongDatabaseError as e:
            self.error_label.setText(str(e))
            self.input_subset.setText(str(old_project_path))
            return
        except FileNotFoundError as e:
            self.error_label.setText(f"Can't find subset: {str(Path(input_subset).name)}")
            self.input_subset.setText(str(old_project_path))
            return
        self.close()

    def create_button_box(self) -> QDialogButtonBox:
        """
        Creates a button box for the dialog window.

        This function initializes a QDialogButtonBox with "Ok" and "Cancel" buttons, setting their
        properties and text labels. It provides a user-friendly interface for submitting or
        canceling actions within the dialog.

        Args:
            self: The instance of the class.

        Returns:
            QDialogButtonBox: The configured button box containing the action buttons.
        """

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.setProperty("class", "button-box")
        button_box.button(QDialogButtonBox.StandardButton.Ok).setProperty("class", "primary-button")
        button_box.button(QDialogButtonBox.StandardButton.Ok).setText(self._("submit"))
        button_box.button(QDialogButtonBox.StandardButton.Cancel).setProperty("class", "secondary-button")
        button_box.button(QDialogButtonBox.StandardButton.Cancel).setText(self._("cancel"))

        return button_box

    @classmethod
    def open_file_picker(cls, input_subset:QLineEdit) -> None:
        """
        Opens a file picker dialog to select a subset file.

        This class method retrieves the starting directory for the file picker based on the
        current input and allows the user to select a database file. It updates the input field
        with the selected file path and stores the directory for future use.

        Args:
            cls: The class itself.
            input_subset: The input field where the selected file path will be set.

        Returns:
            None
        """

        file_path = global_vars.get_start_dir_subset_selection(
            input_subset_str= input_subset.text())

        selected_list = SubsetLoadFilePickerDialog.instance.summon(directory=file_path)
        cls.set_input_line_to_new_subset_path(input_subset, selected_list)

    @classmethod
    def set_input_line_to_new_subset_path(cls, input_subset:QLineEdit, selected:list[Path]):
        if not selected:
            return

        selected_file:Path= selected[0]
        input_subset.setText(str(selected_file))
        if selected_file:
            global_vars.last_subset_selected_dir = selected_file

