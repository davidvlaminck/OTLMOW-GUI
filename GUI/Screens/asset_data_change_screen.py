from pathlib import Path
import qtawesome as qta

from PyQt6.QtWidgets import QVBoxLayout, QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton, QWidget

from Domain.language_settings import return_language
from GUI.Screens.screen import Screen
from GUI.header_bar import HeaderBar
from GUI.stepper import StepperWidget

ROOT_DIR = Path(__file__).parent

LANG_DIR = ROOT_DIR.parent.parent / 'locale/'


class AssetDataChangeScreen(Screen):
    def __init__(self, database):
        super().__init__()
        self._ = return_language(LANG_DIR)
        self.container_insert_data_screen = QVBoxLayout()
        self.header = HeaderBar(database=database, language=self._)
        self.stacked_widget = None
        self.stepper_widget = StepperWidget(self._)
        self.init_ui()

    def init_ui(self):
        button = self.header.header_bar_detail_screen('subtitle_page_3.1')
        button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        self.container_insert_data_screen.addWidget(self.header)
        self.container_insert_data_screen.addSpacing(10)
        self.container_insert_data_screen.addWidget(self.stepper_widget.stepper_widget())
        self.container_insert_data_screen.addSpacing(10)
        self.container_insert_data_screen.addWidget(self.create_menu())
        self.container_insert_data_screen.addStretch()
        self.container_insert_data_screen.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.container_insert_data_screen)

    def create_menu(self):
        window = QWidget()
        window.setProperty('class', 'background-box')
        window_layout = QVBoxLayout()
        window_layout.addWidget(self.input_file_field('original_file_load'))
        window_layout.addWidget(self.input_file_field('new_file_load'))
        window_layout.addWidget(self.button_group())
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

    def button_group(self):
        frame = QFrame()
        frame_layout = QHBoxLayout()
        control_button = QPushButton()
        control_button.setText(self._('control'))
        control_button.setProperty('class', 'primary-button')

        export_button = QPushButton()
        export_button.setText(self._('export'))
        export_button.setProperty('class', 'secondary-button')

        refresh_button = QPushButton()
        refresh_button.setIcon(qta.icon('mdi.refresh', color="#0E5A69"))
        refresh_button.setProperty('class', 'secondary-button')

        frame_layout.addWidget(control_button)
        frame_layout.addWidget(export_button)
        frame_layout.addWidget(refresh_button)
        frame_layout.addStretch()

        frame.setLayout(frame_layout)
        return frame

    def reset_ui(self, _):
        self._ = _
        self.header.reset_ui(_, 'subtitle_page_3.1')
        self.stepper_widget.reset_ui(_)
