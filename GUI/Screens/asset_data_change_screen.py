from pathlib import Path
import qtawesome as qta

from PyQt6.QtWidgets import QVBoxLayout, QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton, QWidget, QTableWidget

from Domain.language_settings import return_language
from GUI.Screens.screen import Screen

ROOT_DIR = Path(__file__).parent

LANG_DIR = ROOT_DIR.parent.parent / 'locale/'


class AssetDataChangeScreen(Screen):
    def __init__(self):
        super().__init__()
        self._ = return_language(LANG_DIR)
        self.container_insert_data_screen = QVBoxLayout()
        self.stacked_widget = None
        self.original_file_label = QLabel()
        self.new_file_label = QLabel()
        self.control_button = QPushButton()
        self.export_button = QPushButton()
        self.page2_btn = QPushButton()
        self.page1_btn = QPushButton()
        self.init_ui()

    def init_ui(self):
        self.container_insert_data_screen.addSpacing(10)
        self.container_insert_data_screen.addWidget(self.create_menu())
        self.container_insert_data_screen.addStretch()
        self.container_insert_data_screen.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.container_insert_data_screen)

    def create_menu(self):
        window = QWidget()
        window.setProperty('class', 'background-box')
        window_layout = QHBoxLayout()
        window_layout.addWidget(self.left_side())
        window_layout.addWidget(self.right_side())
        window.setLayout(window_layout)
        return window

    def left_side(self):
        frame = QFrame()
        frame_layout = QVBoxLayout()
        frame_layout.addWidget(self.input_original_file_field())
        frame_layout.addWidget(self.input_new_file_field())
        frame_layout.addWidget(self.button_group())
        frame_layout.addStretch()
        frame.setLayout(frame_layout)
        return frame

    def right_side(self):
        frame = QFrame()
        frame_layout = QVBoxLayout()
        frame_layout.addWidget(self.change_table())
        frame.setLayout(frame_layout)
        return frame

    def input_original_file_field(self):
        input_file = QFrame()
        input_file_layout = QHBoxLayout()
        self.original_file_label.setText(self._('original_file_load'))
        input_file_field = QLineEdit()
        input_file_field.setReadOnly(True)
        input_file_button = QPushButton()
        input_file_button.setIcon(qta.icon('mdi.folder-open-outline'))
        input_file_layout.addWidget(self.original_file_label)
        input_file_layout.addWidget(input_file_field)
        input_file_layout.addWidget(input_file_button)
        input_file.setLayout(input_file_layout)
        return input_file

    def input_new_file_field(self):
        input_file = QFrame()
        input_file_layout = QHBoxLayout()
        self.new_file_label.setText(self._('new_file_load'))
        input_file_field = QLineEdit()
        input_file_field.setReadOnly(True)
        input_file_button = QPushButton()
        input_file_button.setIcon(qta.icon('mdi.folder-open-outline'))
        input_file_layout.addWidget(self.new_file_label)
        input_file_layout.addWidget(input_file_field)
        input_file_layout.addWidget(input_file_button)
        input_file.setLayout(input_file_layout)
        return input_file

    def button_group(self):
        frame = QFrame()
        frame_layout = QHBoxLayout()
        self.control_button.setText(self._('control'))
        self.control_button.setProperty('class', 'primary-button')

        self.export_button.setText(self._('export'))
        self.export_button.setProperty('class', 'secondary-button')

        refresh_button = QPushButton()
        refresh_button.setIcon(qta.icon('mdi.refresh', color="#0E5A69"))
        refresh_button.setProperty('class', 'secondary-button')

        frame_layout.addWidget(self.control_button)
        frame_layout.addWidget(self.export_button)
        frame_layout.addWidget(refresh_button)
        frame_layout.addStretch()

        frame.setLayout(frame_layout)
        return frame

    def change_table(self):
        table = QTableWidget()
        table.setProperty('class', 'change-table')
        table.setRowCount(5)
        table.setColumnCount(2)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setStretchLastSection(True)
        table.setHorizontalHeaderLabels(
            [self._('id'), self._('action')])
        return table

    def reset_ui(self, _):
        self._ = _
        self.original_file_label.setText(self._('original_file_load'))
        self.new_file_label.setText(self._('new_file_load'))
        self.control_button.setText(self._('control'))
        self.export_button.setText(self._('export'))
        self.page2_btn.setText(self._('update_relations'))
        self.page1_btn.setText(self._('update_files'))
