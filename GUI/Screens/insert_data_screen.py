from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QVBoxLayout, QWidget, QLabel, QPushButton, QFrame, QHBoxLayout, QLineEdit, QListWidget

from Domain.language_settings import return_language
from GUI.Screens.screen import Screen
from GUI.header_bar import HeaderBar
from GUI.stepper import StepperWidget

import qtawesome as qta

ROOT_DIR = Path(__file__).parent

LANG_DIR = ROOT_DIR.parent.parent / 'locale/'


class InsertDataScreen(Screen):
    def __init__(self, database):
        super().__init__()
        self._ = return_language(LANG_DIR)
        self.container_insert_data_screen = QVBoxLayout()
        self.header = HeaderBar(database=database, language=self._)
        self.stacked_widget = None
        self.stepper_widget = StepperWidget(self._)
        self.init_ui()

    def init_ui(self):
        button = self.header.header_bar_detail_screen('subtitle_page_2')
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
        window_layout = QHBoxLayout()
        left_side = self.left_side()
        right_side = self.add_list()
        window_layout.setContentsMargins(32, 0, 16, 0)
        window_layout.addWidget(left_side)
        window_layout.addWidget(right_side)
        window.setLayout(window_layout)
        return window

    def button_set(self):
        button_frame = QFrame()
        button_frame_layout = QHBoxLayout()
        control_button = QPushButton()
        control_button.setText(self._('control_button'))
        control_button.setProperty('class', 'primary-button')
        reset_button = QPushButton()
        reset_button.setIcon(qta.icon('mdi.refresh', color='#0E5A69'))
        reset_button.setProperty('class', 'secondary-button')
        button_frame_layout.addWidget(control_button)
        button_frame_layout.addWidget(reset_button)
        button_frame_layout.addStretch()
        button_frame.setLayout(button_frame_layout)
        return button_frame

    def input_file_field(self):
        input_file = QFrame()
        input_file_layout = QHBoxLayout()
        input_file_label = QLabel()
        input_file_label.setText(self._('input_file'))
        input_file_field = QLineEdit()
        input_file_field.setReadOnly(True)
        input_file_button = QPushButton()
        input_file_button.setIcon(qta.icon('mdi.folder-open-outline'))
        input_file_layout.addWidget(input_file_label)
        input_file_layout.addWidget(input_file_field)
        input_file_layout.addWidget(input_file_button)
        input_file.setLayout(input_file_layout)
        return input_file

    def left_side(self):
        left_side = QFrame()
        left_side_layout = QVBoxLayout()
        left_side_layout.addSpacing(100)
        left_side_layout.addWidget(self.input_file_field(), alignment=Qt.AlignmentFlag.AlignBottom)
        left_side_layout.addWidget(self.button_set(), alignment=Qt.AlignmentFlag.AlignTop)
        left_side_layout.addStretch()
        left_side.setLayout(left_side_layout)
        return left_side

    @staticmethod
    def add_list():
        frame = QFrame()
        frame_layout = QHBoxLayout()
        asset_info = QListWidget()
        frame_layout.addWidget(asset_info)
        frame_layout.setContentsMargins(0, 30, 50, 85)
        frame.setLayout(frame_layout)
        return frame

    def reset_ui(self, _):
        self._ = _
        self.header.reset_ui(_, 'subtitle_page_2')
        self.stepper_widget.reset_ui(_)
