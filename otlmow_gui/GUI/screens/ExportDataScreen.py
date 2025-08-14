from copy import deepcopy
from enum import IntEnum
from pathlib import Path

from PyQt6.QtWidgets import QVBoxLayout, QPushButton, QFrame, QLabel, QHBoxLayout, QComboBox, \
    QCheckBox, QRadioButton, QButtonGroup

from otlmow_gui.Domain import global_vars
from otlmow_gui.Domain.util.Helpers import Helpers
from otlmow_gui.GUI.screens.ExportData_elements.ExportAllDataSubScreen import ExportAllDataSubScreen
from otlmow_gui.GUI.screens.ExportData_elements.ExportFilteredDataSubScreen import ExportFilteredDataSubScreen
from otlmow_gui.GUI.screens.Screen import Screen


class ExportDataScreen(Screen):
    class ExportOptionId(IntEnum):
        ALL_DATA = 0
        ONLY_UNEDITED_DATA = 1

    def __init__(self, language_settings=None):
        super().__init__()
        self._ = language_settings
        self.container_insert_data_screen = QVBoxLayout()

        self.button_group = QButtonGroup()
        self.radio_button_export_all_data = QRadioButton()
        self.radio_button_export_only_unedited_data = QRadioButton()

        self.sub_screen_option_0_nothing = None
        self.sub_screen_option_1_all_data = None
        self.sub_screen_option_2_only_unedited_data = None

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
        # self.container_insert_data_screen.addStretch()
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


        self.extra_option_csv.setText(self._('export assets in different files'))
        self.extra_option_csv.setHidden(True)

        window_layout.addWidget(self.title)
        window_layout.addWidget(self.create_radio_button_box())
        window_layout.addWidget(self.create_horizontal_line())

        # screen when the user hasn't selected any radiobutton
        self.sub_screen_option_0_nothing = Screen()
        sub_window_layout_nothing = QVBoxLayout()
        sub_window_layout_nothing.addStretch()
        self.sub_screen_option_0_nothing.setLayout(sub_window_layout_nothing)


        # screen when the user selects the first option to export all data
        self.sub_screen_option_1_all_data = ExportAllDataSubScreen(language_settings=self._)


        # screen when the user selects the second option to export only unedited data
        self.sub_screen_option_2_only_unedited_data = ExportFilteredDataSubScreen(language_settings=self._)
        sub_window_layout_nothing = QVBoxLayout()
        sub_window_layout_nothing.addStretch()
        self.sub_screen_option_2_only_unedited_data.setLayout(sub_window_layout_nothing)

        window_layout.addWidget(self.sub_screen_option_0_nothing)
        window_layout.addWidget(self.sub_screen_option_1_all_data)
        window_layout.addWidget(self.sub_screen_option_2_only_unedited_data)

        self.sub_screen_option_1_all_data.setHidden(True)
        self.sub_screen_option_2_only_unedited_data.setHidden(True)

        window.setLayout(window_layout)
        return window

    def create_horizontal_line(self):
        horizontal_line = QFrame()
        horizontal_line.setFrameShape(QFrame.Shape.HLine)
        horizontal_line.setLineWidth(1)
        horizontal_line.setMidLineWidth(2)
        horizontal_line.setFrameShadow(QFrame.Shadow.Sunken)
        return horizontal_line

    def create_radio_button_box(self) -> QFrame:


        button_box_frame = QFrame()
        button_box_layout = QHBoxLayout()

        self.radio_button_export_all_data.setText(self._('All data'))
        self.radio_button_export_only_unedited_data.setText(self._('Without unedited data'))

        self.button_group.addButton(self.radio_button_export_all_data,self.ExportOptionId.ALL_DATA)
        # self.button_group.setId(self.radio_button_export_all_data,
        #                         self.ExportOptionId.ALL_DATA)

        self.button_group.addButton(self.radio_button_export_only_unedited_data,self.ExportOptionId.ONLY_UNEDITED_DATA)
        # self.button_group.setId(self.radio_button_export_only_unedited_data,
        #                         self.ExportOptionId.ONLY_UNEDITED_DATA)

        self.button_group.idClicked.connect(self.on_radio_button_click)

        button_box_layout.addWidget(self.radio_button_export_all_data)
        button_box_layout.addStretch(1)
        button_box_layout.addWidget(self.radio_button_export_only_unedited_data)
        button_box_layout.addStretch(5)

        button_box_frame.setLayout(button_box_layout)


        return button_box_frame

    def reset_ui(self, _):
        """
        Creates a button box containing the export button for the export data screen. This method
        sets up the layout for the button, assigns its properties, and connects the button's click
        event to a method for opening the file picker.

        :return: A QFrame containing the button box with the export button.
        :rtype: QFrame
        """
        super().reset_ui(_)
        self._ = _
        self.title.setText(self._('export_to_davie'))

    def on_radio_button_click(self,id:int):
        if (id == self.ExportOptionId.ALL_DATA and self.sub_screen_option_1_all_data.isHidden()):
            if not self.sub_screen_option_0_nothing.isHidden():
                self.sub_screen_option_0_nothing.setHidden(True)
            if not self.sub_screen_option_2_only_unedited_data.isHidden():
                self.sub_screen_option_2_only_unedited_data.setHidden(True)
            self.sub_screen_option_1_all_data.setHidden(False)
        elif (id == self.ExportOptionId.ONLY_UNEDITED_DATA and self.sub_screen_option_2_only_unedited_data.isHidden()):
            if not self.sub_screen_option_0_nothing.isHidden():
                self.sub_screen_option_0_nothing.setHidden(True)
            if not self.sub_screen_option_1_all_data.isHidden():
                self.sub_screen_option_1_all_data.setHidden(True)
            self.sub_screen_option_2_only_unedited_data.setHidden(False)


    def open_folder_of_created_export_files(self, document_path:Path):
        Helpers.open_folder_and_select_document(document_path)