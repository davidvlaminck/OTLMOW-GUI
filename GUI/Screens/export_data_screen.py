from pathlib import Path

from PyQt6.QtWidgets import QVBoxLayout, QWidget, QPushButton

from Domain.language_settings import return_language
from GUI.Screens.screen import Screen
from GUI.header_bar import HeaderBar
from GUI.stepper import StepperWidget

ROOT_DIR = Path(__file__).parent

LANG_DIR = ROOT_DIR.parent.parent / 'locale/'


class ExportDataScreen(Screen):
    def __init__(self, database):
        super().__init__()
        self._ = return_language(LANG_DIR)
        self.container_insert_data_screen = QVBoxLayout()

        self.stacked_widget = None
        self.init_ui()

    def init_ui(self):
        self.container_insert_data_screen.addSpacing(10)
        self.container_insert_data_screen.addWidget(self.create_menu())
        self.container_insert_data_screen.setContentsMargins(16, 0, 16, 0)
        self.setLayout(self.container_insert_data_screen)

    def create_menu(self):
        window = QWidget()
        window.setProperty('class', 'background-box')
        window_layout = QVBoxLayout()
        random_button = QPushButton()
        random_button.setText(self._('random_button'))
        window_layout.addWidget(random_button)
        window.setLayout(window_layout)
        return window

    def reset_ui(self, _):
        self._ = _
