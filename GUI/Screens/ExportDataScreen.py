from pathlib import Path
import qtawesome as qta

from PyQt6.QtWidgets import QVBoxLayout, QPushButton, QFrame, QLabel, QHBoxLayout, QLineEdit, QFileDialog, QComboBox, \
    QCheckBox

from Domain import global_vars
from Domain.ExportDataDomain import ExportDataDomain
from GUI.Screens.Screen import Screen


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
        self.init_ui()

    def init_ui(self):
        self.container_insert_data_screen.addSpacing(10)
        self.container_insert_data_screen.addWidget(self.create_menu())
        self.container_insert_data_screen.setContentsMargins(0, 0, 0, 0)
        self.container_insert_data_screen.addStretch()
        self.setLayout(self.container_insert_data_screen)

    def create_menu(self):
        window = QFrame()
        window_layout = QVBoxLayout()
        window.setProperty('class', 'background-box')
        self.title.setText(self._('export_to_davie'))
        self.title.setProperty('class', 'sub-title')

        window_layout.addWidget(self.title)
        window_layout.addSpacing(20)

        combobox = self.create_combobox()

        window_layout.addWidget(combobox)
        self.relations_split_optionality.setText(self._('export relations and assets in different files'))

        self.extra_option_csv.setText(self._('export assets in different files'))
        self.extra_option_csv.setHidden(True)

        window_layout.addWidget(self.relations_split_optionality)
        window_layout.addWidget(self.extra_option_csv)

        window_layout.addSpacing(10)
        window_layout.addWidget(self.button_box())
        window_layout.addSpacing(10)
        window.setLayout(window_layout)
        return window

    def create_combobox(self):
        frame = QFrame()
        frame_layout = QHBoxLayout()
        self.file_type_label.setText(self._('select file type for export') + ":")
        frame_layout.addWidget(self.file_type_label)
        self.file_extension_selection.addItems(list(global_vars.supported_file_formats.keys()))
        self.file_extension_selection.currentTextChanged.connect(self.show_additional_options)
        frame_layout.addWidget(self.file_extension_selection)
        frame_layout.addStretch()
        frame.setLayout(frame_layout)
        return frame

    def button_box(self):
        button_box = QFrame()
        button_box_layout = QHBoxLayout()
        self.export_btn.setText(self._('export'))
        self.export_btn.setProperty('class', 'primary-button')
        self.export_btn.clicked.connect(lambda: self.open_file_picker())
        button_box_layout.addWidget(self.export_btn)
        button_box_layout.addStretch()
        button_box.setLayout(button_box_layout)
        return button_box

    def input_file_field(self):
        input_file = QFrame()
        input_file_layout = QHBoxLayout()
        self.input_file_label.setText(self._('file_to_upload'))
        input_file_field = QLineEdit()
        input_file_field.setReadOnly(True)
        input_file_button = QPushButton()
        input_file_button.setIcon(qta.icon('mdi.folder-open-outline'))
        input_file_layout.addWidget(self.input_file_label)
        input_file_layout.addWidget(input_file_field)
        input_file_layout.addWidget(input_file_button)
        input_file.setLayout(input_file_layout)
        return input_file

    def reset_ui(self, _):
        self._ = _
        self.export_btn.setText(self._('export'))
        self.file_type_label.setText(self._('select file type for export') + ":")
        self.relations_split_optionality.setText(self._('export relations and assets in different files'))
        self.extra_option_csv.setText(self._('export assets in different files'))
        self.input_file_label.setText(self._('file_to_upload'))
        self.title.setText(self._('export_to_davie'))

    def open_file_picker(self):
        file_path = str(Path.home())
        file_picker = QFileDialog()
        file_picker.setModal(True)
        file_picker.setDirectory(file_path)
        chosen_file_format = self.file_extension_selection.currentText()
        if chosen_file_format in global_vars.supported_file_formats:
            file_suffix = global_vars.supported_file_formats[chosen_file_format]
            filter_filepicker = f"{chosen_file_format} files (*.{file_suffix})"
            document_loc = file_picker.getSaveFileName(filter=filter_filepicker)
        else:
            document_loc = file_picker.getSaveFileName()
        if document_loc != ('', ''):
            csv_option = self.extra_option_csv.isChecked()
            split_relations_and_objects = self.relations_split_optionality.isChecked()
            ExportDataDomain.generate_files(document_loc[0], global_vars.current_project, csv_option, split_relations_and_objects)

    def show_additional_options(self, text):
        if text == 'CSV':
            self.extra_option_csv.setHidden(False)
            self.extra_option_csv.setChecked(True)
        else:
            self.extra_option_csv.setChecked(False)
            self.extra_option_csv.setHidden(True)
