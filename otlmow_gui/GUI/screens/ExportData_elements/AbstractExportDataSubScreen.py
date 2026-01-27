from abc import abstractmethod
from copy import deepcopy
from pathlib import Path

from PyQt6.QtWidgets import QVBoxLayout, QPushButton, QFrame, QLabel, QHBoxLayout, QComboBox, \
    QCheckBox

from otlmow_gui.Domain import global_vars
from otlmow_gui.Domain.step_domain.ExportDataDomain import ExportDataDomain
from otlmow_gui.Domain.util.Helpers import Helpers
from otlmow_gui.GUI.dialog_windows.file_picker_dialog.SaveFilePickerDialog import SaveFilePickerDialog
from otlmow_gui.GUI.screens.Screen import Screen
from otlmow_gui.exception_handler.ExceptionHandlers import create_task_reraise_exception


class AbstractExportDataSubScreen(Screen):

    def __init__(self, language_settings=None):
        super().__init__()
        self._ = language_settings

        self.export_btn = QPushButton()
        self.input_file_label = QLabel()
        self.extra_option_csv = QCheckBox()
        self.file_extension_selection = QComboBox()
        self.title = QLabel()
        self.file_type_label = QLabel()
        self.main_window = None
        self.relations_split_optionality = QCheckBox()
        self.supported_export_formats:dict = deepcopy(global_vars.supported_file_formats)
        if "SDF" in self.supported_export_formats:
            self.supported_export_formats.pop("SDF") # not yet supported for export in V0.5.0

        self.export_file_dialog_window = SaveFilePickerDialog(self._)

        self.init_ui()


    @abstractmethod
    def init_ui(self) -> None:
        pass

    def create_filetype_combobox(self) -> QFrame:
        """
        Creates a combo box for selecting the file type for export. This method sets up the layout,
        adds a label and a combo box populated with supported file formats, and connects the c
        ombo box's change event to a method for displaying additional options.

        :return: A QFrame containing the combo box for file type selection.
        :rtype: QFrame
        """

        frame = QFrame()
        frame_layout = QHBoxLayout()

        self.file_type_label.setText(self._('select file type for export') + ":")

        self.file_extension_selection.addItems(list(self.supported_export_formats.keys()))
        self.file_extension_selection.currentTextChanged.connect(self.show_additional_options)

        frame_layout.addWidget(self.file_type_label)
        frame_layout.addWidget(self.file_extension_selection)
        frame_layout.addStretch()
        frame_layout.setContentsMargins(0,0,0,0)
        frame.setLayout(frame_layout)
        return frame

    def create_relations_split_optionality(self):
        checkbox_frame = QFrame()
        checkbox_layout = QVBoxLayout()

        self.relations_split_optionality.setText(
            self._('export relations and assets in different files'))

        checkbox_layout.addWidget(self.relations_split_optionality)
        checkbox_layout.addWidget(self.create_extra_option_csv())
        checkbox_layout.setContentsMargins(11,0,0,0)
        checkbox_frame.setLayout(checkbox_layout)

        return checkbox_frame

    def create_button_box(self):
        """
        Creates a button box containing the export button for the export data screen.
        This method sets up the layout for the button, assigns its properties,
        and connects the button's click event to a method for opening the file picker.

        :return: A QFrame containing the button box with the export button.
        :rtype: QFrame
        """

        button_box = QFrame()
        button_box_layout = QHBoxLayout()

        self.export_btn.setText(self._('export'))
        self.export_btn.setProperty('class', 'primary-button')
        self.export_btn.clicked.connect(lambda: self.open_file_picker())

        button_box_layout.addWidget(self.export_btn)
        button_box_layout.addStretch()
        button_box_layout.setContentsMargins(0, 0, 0, 0)
        button_box.setLayout(button_box_layout)

        return button_box

    def reset_ui(self, _):
        super().reset_ui(_)
        """
        Creates a button box containing the export button for the export data screen. This method
        sets up the layout for the button, assigns its properties, and connects the button's click
        event to a method for opening the file picker.

        :return: A QFrame containing the button box with the export button.
        :rtype: QFrame
        """

        self._ = _
        self.export_btn.setText(self._('export'))
        self.file_type_label.setText(self._('select file type for export') + ":")
        self.relations_split_optionality.setText(self._('export relations and assets in different files'))
        self.extra_option_csv.setText(self._('export assets in different files'))
        self.input_file_label.setText(self._('file_to_upload'))


    def create_extra_option_csv(self):
        self.extra_option_csv.setText(self._('export assets in different files'))
        self.extra_option_csv.setHidden(True)
        return self.extra_option_csv

    def open_file_picker(self):
        """
        Opens a file picker dialog for the user to select a location to save exported files.
        This method configures the dialog based on the currently selected file format and options,
        and triggers the file generation process if a valid file location is chosen.

        :return: None
        """



        chosen_file_format = self.file_extension_selection.currentText()
        if chosen_file_format in self.supported_export_formats:
            document_path_list = self.export_file_dialog_window.summon(
                chosen_file_format=chosen_file_format,
                supported_export_formats=self.supported_export_formats,
                project_name=global_vars.current_project.eigen_referentie)

            if document_path_list and document_path_list[0]:
                csv_option = self.extra_option_csv.isChecked()
                split_relations_and_objects = self.relations_split_optionality.isChecked()
                try:
                    self.process_export(document_path_list, csv_option, split_relations_and_objects)
                except Exception as e:
                    # TODO: proper error message when file fails to be exported
                    raise e

    def process_export(self, document_path_list, csv_option, split_relations_and_objects):
        create_task_reraise_exception(
            ExportDataDomain.generate_files(end_file=document_path_list[0],
                                            separate_per_class_csv_option=csv_option,
                                            separate_relations_option=split_relations_and_objects))

    def show_additional_options(self, text):
        """
        Displays additional options based on the selected file type in the export data screen.
        This method shows or hides the CSV option based on whether the user selects 'CSV' as the
        file type, ensuring that only relevant options are visible.

        :param text: The selected file type that determines which options to display.
        :type text: str

        :return: None
        """

        if text == 'CSV':
            self.extra_option_csv.setHidden(False)
            self.extra_option_csv.setChecked(True)
        else:
            self.extra_option_csv.setChecked(False)
            self.extra_option_csv.setHidden(True)


    def open_folder_of_created_export_files(self, document_path:Path):
        Helpers.open_folder_and_select_document(document_path)