from pathlib import Path
import qtawesome as qta

from PyQt6.QtWidgets import QVBoxLayout, QFrame, QHBoxLayout, QPushButton, QWidget, QLineEdit, QLabel, QListWidget

from Domain.language_settings import return_language
from GUI.Screens.screen import Screen

ROOT_DIR = Path(__file__).parent

LANG_DIR = ROOT_DIR.parent.parent / 'locale/'


class RelationChangeScreen(Screen):
    def __init__(self):
        super().__init__()
        self._ = return_language(LANG_DIR)
        self.container_insert_data_screen = QVBoxLayout()
        self.stacked_widget = None
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
        window_layout = QVBoxLayout()
        window_layout.addSpacing(10)
        window_layout.addWidget(self.input_file_field())
        window_layout.addSpacing(10)
        window_layout.addWidget(self.listbox())
        window.setLayout(window_layout)
        return window

    def input_file_field(self):
        frame = QFrame()
        frame_layout = QHBoxLayout()
        input_field = QLineEdit()
        input_field.setReadOnly(True)
        input_field.setPlaceholderText(self._('choose_file'))
        input_file_button = QPushButton()
        input_file_button.setIcon(qta.icon('mdi.folder-open-outline'))
        frame_layout.addWidget(input_field)
        frame_layout.addWidget(input_file_button)
        frame_layout.addStretch()
        frame.setLayout(frame_layout)
        return frame

    def class_list(self):
        frame = QFrame()
        frame_layout = QVBoxLayout()
        class_label = QLabel()
        class_label.setText(self._('class_list'))
        class_list = QListWidget()
        class_list.setProperty('class', 'list')

        frame_layout.addWidget(class_label)
        frame_layout.addWidget(class_list)
        frame.setLayout(frame_layout)
        return frame

    def relations_list(self):
        frame = QFrame()
        frame_layout = QVBoxLayout()
        relations_label = QLabel()
        relations_label.setText(self._('relations_list'))
        class_list = QListWidget()
        class_list.setProperty('class', 'list')

        frame_layout.addWidget(relations_label)
        frame_layout.addWidget(class_list)
        frame.setLayout(frame_layout)
        return frame

    def existing_relations_list(self):
        frame = QFrame()
        frame_layout = QVBoxLayout()
        existing_rel_label = QLabel()
        existing_rel_label.setText(self._('existing_relations_list'))
        class_list = QListWidget()
        class_list.setProperty('class', 'list')

        frame_layout.addWidget(existing_rel_label)
        frame_layout.addWidget(class_list)
        frame.setLayout(frame_layout)
        return frame

    def listbox(self):
        frame = QFrame()
        frame_layout = QHBoxLayout()
        frame_layout.addWidget(self.class_list())
        frame_layout.addWidget(self.relations_list())
        frame_layout.addWidget(self.existing_relations_list())
        frame.setLayout(frame_layout)
        return frame

    def reset_ui(self, _):
        self._ = _
