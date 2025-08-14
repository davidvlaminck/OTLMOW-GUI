from PyQt6.QtWidgets import QVBoxLayout

from otlmow_gui.GUI.screens.ExportData_elements.AbstractExportDataSubScreen import AbstractExportDataSubScreen



class ExportAllDataSubScreen(AbstractExportDataSubScreen):
    def __init__(self, language_settings=None):
        super().__init__(language_settings=language_settings)

    def init_ui(self) -> None:
        """
        Initializes the user interface for the export data screen. This method sets up the layout
        by adding spacing, a menu, and configuring the container's margins and stretch properties
        to ensure proper alignment and appearance.

        :return: None
        """



        sub_window_layout = QVBoxLayout()
        sub_window_layout.addWidget(self.create_filetype_combobox())
        sub_window_layout.addWidget(self.create_relations_split_optionality())
        sub_window_layout.addSpacing(10)
        sub_window_layout.addWidget(self.create_button_box())
        sub_window_layout.addSpacing(10)
        sub_window_layout.addStretch()
        self.setLayout(sub_window_layout)
