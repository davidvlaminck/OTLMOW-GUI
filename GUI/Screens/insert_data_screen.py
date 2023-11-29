import logging
from pathlib import Path

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QVBoxLayout, QWidget, QLabel, QPushButton, QFrame, QHBoxLayout, QLineEdit, QListWidget, \
    QFileDialog, QListWidgetItem, QTreeWidget, QTreeWidgetItem
from otlmow_model.OtlmowModel.Helpers.OTLObjectHelper import count_assets_by_type

from Domain.insert_data_domain import InsertDataDomain
from Domain.language_settings import return_language
from Exceptions.NotOTLConformError import NotOTLConformError
from GUI.ButtonWidget import ButtonWidget
from GUI.Screens.screen import Screen
import qtawesome as qta

ROOT_DIR = Path(__file__).parent

LANG_DIR = ROOT_DIR.parent.parent / 'locale/'


class InsertDataScreen(Screen):
    def __init__(self):
        super().__init__()
        self._ = return_language(LANG_DIR)
        self.container_insert_data_screen = QVBoxLayout()
        self.feedback_message_box = QFrame()
        self.stacked_widget = None
        self.message_icon = QLabel()
        self.message = QLabel()
        self.input_file_label = QLabel()
        self.control_button = ButtonWidget()
        self.input_file_field = QTreeWidget()
        self.asset_info = QListWidget()

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
        self.control_button.setText(self._('control_button'))
        self.control_button.setDisabled(True)
        self.control_button.clicked.connect(lambda: self.validate_documents(self.input_file_field))
        self.control_button.setProperty('class', 'primary-button')
        reset_button = QPushButton()
        reset_button.setIcon(qta.icon('mdi.refresh', color='#0E5A69'))
        reset_button.setProperty('class', 'secondary-button')
        reset_button.clicked.connect(lambda: self.clear_list())
        button_frame_layout.addWidget(self.control_button)
        button_frame_layout.addWidget(reset_button)
        button_frame_layout.addStretch()
        button_frame.setLayout(button_frame_layout)
        return button_frame

    def validate_documents(self, documents):
        self.asset_info.clear()
        try:
            assets = InsertDataDomain().check_data(documents)
            self.fill_feedback_list(assets)
            self.positive_feedback_message()
        except NotOTLConformError as e:
            self.negative_feedback_message()
            self.add_error_to_feedback_list(e)

    def add_input_file_field(self):
        input_file = QFrame()
        input_file_layout = QHBoxLayout()
        self.input_file_label.setText(self._('input_file'))
        input_file_button = QPushButton()
        input_file_button.setIcon(qta.icon('mdi.folder-open-outline'))
        input_file_button.clicked.connect(lambda: self.open_file_picker())
        self.input_file_field.setColumnCount(2)
        self.input_file_field.setHeaderHidden(True)
        input_file_layout.addWidget(self.input_file_label)
        input_file_layout.addWidget(self.input_file_field)
        input_file_layout.addWidget(input_file_button)
        input_file.setLayout(input_file_layout)
        return input_file

    def left_side(self):
        left_side = QFrame()
        left_side_layout = QVBoxLayout()
        left_side_layout.addSpacing(100)
        left_side_layout.addWidget(self.add_input_file_field(), alignment=Qt.AlignmentFlag.AlignBottom)
        left_side_layout.addWidget(self.button_set(), alignment=Qt.AlignmentFlag.AlignTop)
        left_side_layout.addSpacing(30)
        self.construct_feedback_message()
        left_side_layout.addWidget(self.feedback_message_box)
        left_side_layout.addStretch()
        left_side.setLayout(left_side_layout)
        return left_side

    def construct_feedback_message(self):
        frame_layout = QHBoxLayout()
        frame_layout.addWidget(self.message_icon)
        self.message.setProperty('class', 'feedback-message')
        frame_layout.addWidget(self.message)
        frame_layout.addStretch()
        self.feedback_message_box.setLayout(frame_layout)

    def add_list(self):
        frame = QFrame()
        frame_layout = QHBoxLayout()
        frame_layout.addWidget(self.asset_info)
        frame_layout.setContentsMargins(0, 30, 50, 85)
        frame.setLayout(frame_layout)
        return frame

    def positive_feedback_message(self):
        self.message_icon.setPixmap(qta.icon('mdi.check', color="white").pixmap(QSize(48, 48)))
        self.message.setText(self._('all_info_correct'))
        self.feedback_message_box.setStyleSheet('background-color: #1DCA94; border-radius: 10px;')

    def warning_feedback_message(self):
        self.message_icon.setPixmap(qta.icon('mdi.alert', color="white").pixmap(QSize(48, 48)))
        self.message.setText(self._('warning'))
        self.feedback_message_box.setStyleSheet('background-color: #F8AA62; border-radius: 10px;')

    def negative_feedback_message(self):
        self.message_icon.setPixmap(qta.icon('mdi.alert-circle-outline', color="white").pixmap(QSize(48, 48)))
        self.message.setText(self._('error'))
        self.feedback_message_box.setStyleSheet('background-color: #CC3300; border-radius: 10px;')

    def reset_ui(self, _):
        self._ = _
        self.input_file_label.setText(self._('input_file'))
        self.control_button.setText(self._('control_button'))

    def open_file_picker(self):
        file_path = str(Path.home())
        file_picker = QFileDialog()
        file_picker.setWindowTitle("Selecteer bestand")
        file_picker.setDirectory(file_path)
        if file_picker.exec():
            self.add_file_to_list(file_picker.selectedFiles()[0])

    def add_file_to_list(self, param):
        self.control_button.setDisabled(False)
        test = QTreeWidgetItem()
        test.setText(0, param)
        self.input_file_field.addTopLevelItem(test)
        self.input_file_field.resizeColumnToContents(0)
        button = QPushButton()
        button.clicked.connect(lambda: self.delete_file_from_list())
        button.setIcon(qta.icon('mdi.close'))
        self.input_file_field.setItemWidget(test, 1, button)

    def delete_file_from_list(self):
        items = self.input_file_field.selectedItems()
        self.input_file_field.removeItemWidget(items[0], 1)
        self.input_file_field.takeTopLevelItem(self.input_file_field.indexOfTopLevelItem(items[0]))
        if self.input_file_field.topLevelItemCount() == 0:
            self.control_button.setDisabled(True)

    def clear_list(self):
        self.input_file_field.clear()
        self.asset_info.clear()
        self.control_button.setDisabled(True)

    def add_error_to_feedback_list(self, e):
        error_widget = QListWidgetItem()
        error_widget.setText(str(e))
        self.asset_info.addItem(error_widget)

    def fill_feedback_list(self, assets):
        total_assets = 0
        if assets is None:
            return
        asset_dict = count_assets_by_type(assets[0])
        for key, value in asset_dict.items():
            key_split = key.split('#')
            asset_widget = QListWidgetItem()
            asset_widget.setText(f'{value} objecten van het type {key_split[-1]} ingeladen\n')
            total_assets += value
            self.asset_info.addItem(asset_widget)
        asset_widget = QListWidgetItem()
        asset_widget.setText(f'In het totaal zijn er {total_assets} objecten ingeladen die conform zijn met de OTL standaard\n')
        self.asset_info.addItem(asset_widget)
