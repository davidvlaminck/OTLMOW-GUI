from pathlib import Path

from PyQt6.QtWidgets import QWidget, QVBoxLayout

from Domain.language_settings import return_language
from GUI.header_bar import HeaderBar

ROOT_DIR = Path(__file__).parent
LANG_DIR = ROOT_DIR.parent / 'locale/'


class TemplateScreen(QWidget):
    def __init__(self, database):
        super().__init__()
        self.database = database
        self._ = self._ = return_language(LANG_DIR)
        self.header = HeaderBar(self._, self.database, self)
        self.container_template_screen = QVBoxLayout()

        self.init_ui()

    def init_ui(self):
        self.header.header_bar_detail_screen()
        self.container_template_screen.addWidget(self.header)
        self.container_template_screen.addSpacing(39)
        self.container_template_screen.addStretch()
        self.container_template_screen.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.container_template_screen)
        self.show()
