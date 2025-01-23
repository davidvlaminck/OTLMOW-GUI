from copy import deepcopy
from pathlib import Path
import qtawesome as qta

from PyQt6.QtWidgets import QVBoxLayout, QPushButton, QFrame, QLabel, QHBoxLayout, QLineEdit, QFileDialog, QComboBox, \
    QCheckBox

from Domain import global_vars
from Domain.step_domain.ExportDataDomain import ExportDataDomain
from GUI.screens.Screen import Screen


class ExportDataScreen(Screen):
    def __init__(self, language_settings=None):
        super().__init__()
        self._ = language_settings
        self.container_insert_data_screen = QVBoxLayout()
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
        self.init_ui()

    def init_ui(self) -> None:
        """
        Initializes the user interface for the export data screen. This method sets up the layout
        by adding spacing, a menu, and configuring the container's margins and stretch properties
        to ensure proper alignment and appearance.

        :return: None
        """

        self.container_insert_data_screen.addSpacing(10)
        self.container_insert_data_screen.addWidget(self.create_menu())
        self.container_insert_data_screen.setContentsMargins(0, 0, 0, 0)
        self.container_insert_data_screen.addStretch()
        self.setLayout(self.container_insert_data_screen)

    def create_menu(self) -> QFrame:
        """
         Creates and configures a menu for the export data screen.
         This method sets up the layout, adds various widgets including titles, options, and
         buttons, and returns the constructed menu as a QFrame.

        :return: A QFrame containing the configured menu for the export data screen.
        :rtype: QFrame
        """

        window = QFrame()
        window.setProperty('class', 'background-box')

        window_layout = QVBoxLayout()

        self.title.setText(self._('export_to_davie'))
        self.title.setProperty('class', 'sub-title')

        self.relations_split_optionality.setText(self._('export relations and assets in different files'))

        self.extra_option_csv.setText(self._('export assets in different files'))
        self.extra_option_csv.setHidden(True)

        window_layout.addWidget(self.title)
        window_layout.addSpacing(20)
        window_layout.addWidget(self.create_combobox())
        window_layout.addWidget(self.relations_split_optionality)
        window_layout.addWidget(self.extra_option_csv)
        window_layout.addSpacing(10)
        window_layout.addWidget(self.button_box())
        window_layout.addSpacing(10)

        window.setLayout(window_layout)
        return window

    def create_combobox(self) -> QFrame:
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
        frame.setLayout(frame_layout)
        return frame

    def button_box(self):
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

        button_box.setLayout(button_box_layout)

        return button_box

    def reset_ui(self, _):
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
        self.title.setText(self._('export_to_davie'))

    def open_file_picker(self):
        """
        Opens a file picker dialog for the user to select a location to save exported files.
        This method configures the dialog based on the currently selected file format and options,
        and triggers the file generation process if a valid file location is chosen.

        :return: None
        """

        file_path = str(Path.home())

        file_picker = QFileDialog()
        file_picker.setModal(True)
        file_picker.setDirectory(file_path)

        chosen_file_format = self.file_extension_selection.currentText()
        if chosen_file_format in self.supported_export_formats:
            file_suffix = self.supported_export_formats[chosen_file_format]
            filter_filepicker = f"{chosen_file_format} files (*.{file_suffix})"
            document_loc = file_picker.getSaveFileName(filter=filter_filepicker)
        else:
            document_loc = file_picker.getSaveFileName()

        if document_loc != ('', ''):
            csv_option = self.extra_option_csv.isChecked()
            split_relations_and_objects = self.relations_split_optionality.isChecked()
            ExportDataDomain.generate_files(end_file=document_loc[0],
                                            separate_per_class_csv_option=csv_option,
                                            separate_relations_option=split_relations_and_objects)

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
