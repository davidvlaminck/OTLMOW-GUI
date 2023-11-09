from pathlib import Path

from PyQt6.QtWidgets import QVBoxLayout

from Domain.language_settings import return_language
from GUI.Screens.screen import Screen
from GUI.header_bar import HeaderBar
from GUI.stepper import StepperWidget

ROOT_DIR = Path(__file__).parent

LANG_DIR = ROOT_DIR.parent.parent / 'locale/'


class ConversionScreen(Screen):
    def __init__(self, database):
        super().__init__()
        self._ = return_language(LANG_DIR)
        self.container_insert_data_screen = QVBoxLayout()
        self.init_ui()

    def init_ui(self):
        self.container_insert_data_screen.addSpacing(10)

        self.container_insert_data_screen.addStretch()
        self.container_insert_data_screen.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.container_insert_data_screen)

    def reset_ui(self, _):
        self._ = _
