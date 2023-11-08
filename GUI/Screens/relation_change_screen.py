from pathlib import Path

from PyQt6.QtWidgets import QVBoxLayout

from Domain.language_settings import return_language
from GUI.Screens.screen import Screen
from GUI.header_bar import HeaderBar
from GUI.stepper import StepperWidget

ROOT_DIR = Path(__file__).parent

LANG_DIR = ROOT_DIR.parent.parent / 'locale/'


class RelationChangeScreen(Screen):
    def __init__(self, database):
        super().__init__()
        self._ = return_language(LANG_DIR)
        self.container_insert_data_screen = QVBoxLayout()
        self.header = HeaderBar(database=database, language=self._)
        self.stacked_widget = None
        self.stepper_widget = StepperWidget(self._)
        self.init_ui()

    def init_ui(self):
        button = self.header.header_bar_detail_screen('subtitle_page_3.2')
        button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        self.container_insert_data_screen.addWidget(self.header)
        self.container_insert_data_screen.addSpacing(10)
        self.container_insert_data_screen.addWidget(self.stepper_widget.stepper_widget())
        self.container_insert_data_screen.addStretch()
        self.container_insert_data_screen.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.container_insert_data_screen)

    def reset_ui(self, _):
        self._ = _
        self.header.reset_ui(_, 'subtitle_page_3.2')
        self.stepper_widget.reset_ui(_)
