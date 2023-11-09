from pathlib import Path
import qtawesome as qta

from PyQt6.QtWidgets import QVBoxLayout, QPushButton, QFrame, QLabel, QHBoxLayout, QLineEdit

from Domain.language_settings import return_language
from GUI.Screens.screen import Screen

ROOT_DIR = Path(__file__).parent

LANG_DIR = ROOT_DIR.parent.parent / 'locale/'


class ExportDataScreen(Screen):
    def __init__(self):
        super().__init__()
        self._ = return_language(LANG_DIR)
        self.container_insert_data_screen = QVBoxLayout()

        self.stacked_widget = None
        self.init_ui()

    def init_ui(self):
        self.container_insert_data_screen.addWidget(self.create_menu())
        self.container_insert_data_screen.addStretch()
        self.setLayout(self.container_insert_data_screen)

    def create_menu(self):
        window = QFrame()
        window_layout = QVBoxLayout()
        window.setProperty('class', 'background-box')
        title = QLabel()
        title.setText(self._('export_to_davie'))
        convert_btn = QPushButton()
        convert_btn.setText(self._('export'))

        window_layout.addWidget(title)
        window_layout.addWidget(self.input_file_field('file_to_upload'))
        window_layout.addWidget(convert_btn)
        window.setLayout(window_layout)
        return window

    def input_file_field(self, text):
        input_file = QFrame()
        input_file_layout = QHBoxLayout()
        input_file_label = QLabel()
        input_file_label.setText(self._(text))
        input_file_field = QLineEdit()
        input_file_field.setReadOnly(True)
        input_file_button = QPushButton()
        input_file_button.setIcon(qta.icon('mdi.folder-open-outline'))
        input_file_layout.addWidget(input_file_label)
        input_file_layout.addWidget(input_file_field)
        input_file_layout.addWidget(input_file_button)
        input_file.setLayout(input_file_layout)
        return input_file

    def reset_ui(self, _):
        self._ = _
