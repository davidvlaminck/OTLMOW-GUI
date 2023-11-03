from pathlib import Path

from PyQt6.QtCore import Qt, QLine
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QStackedWidget, QFrame

from Domain.language_settings import return_language
from GUI.header_bar import HeaderBar
from GUI.stepper import StepperWidget

ROOT_DIR = Path(__file__).parent
LANG_DIR = ROOT_DIR.parent / 'locale/'


class TemplateScreen(QWidget):
    def __init__(self, database):
        super().__init__()
        self.database = database
        self._ = self._ = return_language(LANG_DIR)
        self.header = HeaderBar(self._, self.database, self)
        self.container_template_screen = QVBoxLayout()
        self.stacked_widget = QStackedWidget()
        self.stepper_widget = StepperWidget(self._)

        self.init_ui()

    def init_ui(self):
        button = self.header.header_bar_detail_screen()
        button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        self.container_template_screen.addWidget(self.header)
        self.container_template_screen.addSpacing(10)
        self.container_template_screen.addWidget(self.stepper_widget.stepper_widget())
        self.container_template_screen.addStretch()
        self.container_template_screen.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.container_template_screen)


