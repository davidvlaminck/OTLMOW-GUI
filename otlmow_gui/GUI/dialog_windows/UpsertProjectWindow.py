from pathlib import Path
from typing import Callable

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QDialogButtonBox

from otlmow_gui.Domain import global_vars
from otlmow_gui.Domain.project.Project import Project
from otlmow_gui.Domain.step_domain.HomeDomain import HomeDomain

import qtawesome as qta

from otlmow_gui.Exceptions.EmptyFieldError import EmptyFieldError
from otlmow_gui.Exceptions.WrongDatabaseError import WrongDatabaseError
from otlmow_gui.GUI.dialog_windows.NotificationWindow import NotificationWindow
from otlmow_gui.GUI.dialog_windows.ProjectExistsError import ProjectExistsError
from otlmow_gui.GUI.dialog_windows.file_picker_dialog.SubsetLoadFilePickerDialog import \
    SubsetLoadFilePickerDialog


class UpsertProjectWindow(QDialog):

    def __init__(self, language_settings: Callable, project: Project = None):
        super().__init__()

        self._ = language_settings

        self.error_label = QLabel()
        self.error_label.setText("")

        self.setMinimumWidth(400)
        # Makes the dialog the primary screen, disabling the screen behind it
        self.setModal(True)

        # Creates the vertical stack layout
        layout = QVBoxLayout()

        # Creates the input fields
        container_eigen_ref, input_eigen_ref = self.create_eigen_ref_container()
        container_bestek, input_bestek = self.create_bestek_container()
        container_subset, input_subset = self.create_subset_container()

        # Adds the input fields to the layout
        layout.addLayout(container_eigen_ref)
        layout.addLayout(container_bestek)
        layout.addLayout(container_subset)

        if project:
            self.setWindowTitle(self._("alter_project_title"))
            input_eigen_ref.setText(project.eigen_referentie)
            input_bestek.setText(project.bestek)
            input_subset.setText(str(project.subset_path))
        else:
            self.setWindowTitle(self._("new_project_title"))

        # Changes the color of the error label to red
        self.error_label.setStyleSheet("color: red")

        # Creates the button box
        button_box = self.create_button_box()
        # sends the values off to validate once submitted
        button_box.accepted.connect(
            lambda: self.pass_values_through_validate(input_eigen_ref= input_eigen_ref.text(),
                                                      input_bestek= input_bestek.text(),
                                                      input_subset= input_subset.text(),
                                                      project=project))
        button_box.rejected.connect(self.reject)
        # Adds the two buttons to the layout
        layout.addWidget(button_box)
        layout.addWidget(self.error_label)
        # Fills the dialog with the created layout
        self.setLayout(layout)

    def create_subset_container(self) -> tuple[QHBoxLayout,QLineEdit]:
        """
        Creates a container for the subset input field along with its label and file picker button.

        This method constructs a horizontal layout that includes a label indicating the subset, a read-only input field for displaying the subset value, and a button that allows the user to open a file picker dialog. The layout and input field are returned for further use in the user interface.

        :return: A tuple containing the layout for the subset container and the input field.
        :rtype: tuple[QHBoxLayout, QLineEdit]
        """

        label_subset = QLabel(self._("subset") + ":")
        input_subset = QLineEdit()
        input_subset.setObjectName("subset_edit")
        input_subset.setReadOnly(True)
        input_subset.setPlaceholderText(self._("subset"))
        file_picker_btn = QPushButton()
        file_picker_btn.setObjectName("file_picker_btn")
        file_picker_btn.setIcon(qta.icon('mdi.folder-open-outline'))
        file_picker_btn.clicked.connect(lambda: self.open_file_picker(input_subset))
        container_subset = QHBoxLayout()
        container_subset.addWidget(label_subset, alignment=Qt.AlignmentFlag.AlignLeft)
        container_subset.addWidget(input_subset)
        container_subset.addWidget(file_picker_btn)
        return container_subset, input_subset

    def create_bestek_container(self) -> tuple[QHBoxLayout,QLineEdit]:
        """
        Creates a container for the bestek input field along with its label.

        This method constructs a horizontal layout that includes a label indicating the service order and an input field for entering the bestek value. The layout and input field are returned for further use in the user interface.

        :return: A tuple containing the layout for the bestek container and the input field.
        :rtype: tuple[QHBoxLayout, QLineEdit]
        """

        label_bestek = QLabel(self._("service_order") + ":")
        input_bestek = QLineEdit()
        input_bestek.setObjectName("bestek_edit")
        input_bestek.setPlaceholderText(self._("service_order"))
        container_bestek = QHBoxLayout()
        container_bestek.addWidget(label_bestek, alignment=Qt.AlignmentFlag.AlignLeft)
        container_bestek.addWidget(input_bestek)
        return container_bestek, input_bestek

    def create_eigen_ref_container(self)  -> tuple[QHBoxLayout,QLineEdit]:
        """
        Creates a container for the eigen reference input field along with its label.

        This method constructs a horizontal layout that includes a label indicating the own reference and an input field for entering the eigen reference value. The layout and input field are returned for further use in the user interface.

        :return: A tuple containing the layout for the eigen reference container and the input field.
        :rtype: tuple[QHBoxLayout, QLineEdit]
        """

        label_eigen_ref = QLabel(self._("own_reference") + ":")
        input_eigen_ref = QLineEdit()
        input_eigen_ref.setObjectName("eigen_ref_edit")
        input_eigen_ref.setPlaceholderText(self._("own_reference"))
        container_eigen_ref = QHBoxLayout()
        container_eigen_ref.addWidget(label_eigen_ref, alignment=Qt.AlignmentFlag.AlignLeft)
        container_eigen_ref.addWidget(input_eigen_ref)
        return container_eigen_ref, input_eigen_ref

    def create_button_box(self) -> QDialogButtonBox:
        """
        Creates a button box for the dialog window with OK and Cancel buttons.

        This method initializes a QDialogButtonBox with standard OK and Cancel buttons, applying specific properties and text labels to each button. The button box is configured for use in the dialog interface and returned for further integration.

        :return: The configured QDialogButtonBox containing the OK and Cancel buttons.
        :rtype: QDialogButtonBox
        """

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.setProperty("class", "button-box")
        button_box.button(QDialogButtonBox.StandardButton.Ok).setProperty("class", "primary-button")
        button_box.button(QDialogButtonBox.StandardButton.Ok).setText(self._("submit"))
        button_box.button(QDialogButtonBox.StandardButton.Cancel).setProperty("class", "secondary-button")
        button_box.button(QDialogButtonBox.StandardButton.Cancel).setText(self._("cancel"))
        return button_box

    def pass_values_through_validate(self,
                                     input_eigen_ref: str,
                                     input_bestek: str,
                                     input_subset: str,
                                     project: Project = None) -> None:
        """
        Validates input values and processes them for project upsert operations.

        This method checks the provided eigen reference, bestek, and subset values for validity
        using the HomeDomain validation methods. If the inputs are valid, it processes the upsert
        dialog input and closes the dialog; otherwise, it displays an error message.

        :param input_eigen_ref: The eigen reference input to validate.
        :type input_eigen_ref: str
        :param input_bestek: The bestek input to validate.
        :type input_bestek: str
        :param input_subset: The subset input to validate.
        :type input_subset: str
        :param project: An optional Project instance to process. Defaults to None.
        :type project: Project, optional

        :return: None
        """

        try:
            HomeDomain.validate(input_eigen_ref, input_bestek, input_subset)
        except EmptyFieldError as e:
            self.error_label.setText(str(e))
            return
        except WrongDatabaseError as e:
            self.error_label.setText(str(e))
            return
        except FileNotFoundError as e:
            self.error_label.setText(f"Can't find subset: {str(Path(input_subset).name)}")
            return
        self.error_label.setText("")

        try:
            HomeDomain.process_upsert_dialog_input(input_bestek, input_eigen_ref.strip(), input_subset, project)
            self.close()
        except ProjectExistsError as e:
            notification = NotificationWindow(title=self._("Project bestaat al"),
                                              message=self._(
                                                  "Project naam: \"{project_naam}\" bestaat al.\nGeef 1 van de projecten een andere naam of verwijder het bestaande project".format(
                                                      project_naam=e.eigen_referentie)))
            notification.exec()




    @staticmethod
    def open_file_picker(input_subset: QLineEdit):
        """
        Opens a file picker dialog to select a subset file.

        This static method displays a file dialog that allows the user to select a database file. If the input subset field is empty, the dialog starts in the user's home directory; otherwise, it starts in the directory specified by the input subset field.

        :param input_subset: The QLineEdit widget where the selected file path will be set.
        :type input_subset: QLineEdit

        :return: None
        """

        file_path = global_vars.get_start_dir_subset_selection(input_subset.text())

        selected_path_list = SubsetLoadFilePickerDialog.instance.summon(directory=file_path)
        if selected_path_list:
            selected = selected_path_list[0]
            input_subset.setText(str(selected))
            if selected:
                global_vars.last_subset_selected_dir = selected
