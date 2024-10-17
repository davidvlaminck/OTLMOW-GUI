from pathlib import Path
from typing import List

import qtawesome as qta
from PyQt6.QtGui import QPixmap

from PyQt6.QtWidgets import QVBoxLayout, QFrame, QHBoxLayout, QPushButton, \
    QWidget, QLineEdit, QLabel, QListWidget, QListWidgetItem
from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLObject
from otlmow_model.OtlmowModel.Classes.ImplementatieElement.AIMObject import \
    AIMObject

from GUI.Screens.Screen import Screen



class RelationChangeScreen(Screen):
    def __init__(self, language_settings=None):
        super().__init__()
        self._ = language_settings
        self.container_insert_data_screen = QVBoxLayout()
        self.main_window = None
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
        window_layout.addWidget(self.horizontal_layout())
        window.setLayout(window_layout)

        self.fill_relations_list()

        return window

    def input_file_field(self):
        frame = QFrame()
        frame_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setReadOnly(True)
        self.input_field.setPlaceholderText(self._('functionality under development'))
        self.input_file_button = QPushButton()
        self.input_file_button.setIcon(qta.icon('mdi.folder-open-outline'))
        self.input_file_button.setDisabled(True)
        frame_layout.addWidget(self.input_field)
        frame_layout.addWidget(self.input_file_button)
        frame_layout.addStretch()
        frame.setLayout(frame_layout)
        return frame

    def class_list(self):
        frame = QFrame()
        frame_layout = QVBoxLayout()
        class_label = QLabel()
        class_label.setText(self._('class_list'))
        self.class_list = QListWidget()
        self.class_list.setProperty('class', 'list')

        frame_layout.addWidget(class_label)
        frame_layout.addWidget(self.class_list)
        frame.setLayout(frame_layout)
        return frame

    def fill_class_list(self,objects: List[AIMObject]):
        self.class_list.clear()
        for OTL_object in objects:
            item = QListWidgetItem()
            screen_name = str(OTL_object.assetId.identificator)
            if hasattr(OTL_object, 'naam') and OTL_object.naam:
                screen_name = OTL_object.naam

            abbr_typeURI = OTL_object.typeURI.replace("https://wegenenverkeer.data.vlaanderen.be/ns/","")

            item.setText("{0}/{1}".format(abbr_typeURI,screen_name))

            self.class_list.addItem(item)

    def fill_possible_relations_list(self, objects: List[AIMObject]):
        self.relation_list.clear()
        for OTL_object in objects:
            item = QListWidgetItem()
            item.setText(self._(
                OTL_object.typeURI.replace("https://wegenenverkeer.data.vlaanderen.be/ns/",""))) #+ "/" + str(OTL_object.assetId.identificator)))
            self.relation_list.addItem(item)

    def relations_list(self):
        frame = QFrame()
        frame_layout = QVBoxLayout()
        relations_label = QLabel()
        relations_label.setText(self._('relations_list'))
        self.relation_list = QListWidget()
        self.relation_list.setProperty('class', 'list')

        frame_layout.addWidget(relations_label)
        frame_layout.addWidget(self.relation_list)
        frame.setLayout(frame_layout)
        return frame

    def fill_relations_list(self):
        self.relation_list.clear()
        item = QListWidgetItem()
        item.setText(self._("loading"))
        self.relation_list.addItem(item)

    def existing_relations_list(self):
        frame = QFrame()
        frame_layout = QVBoxLayout()
        existing_rel_label = QLabel()
        existing_rel_label.setText(self._('existing_relations_list'))
        self.existing_relation_list = QListWidget()
        self.existing_relation_list.setProperty('class', 'list')

        frame_layout.addWidget(existing_rel_label)
        frame_layout.addWidget(self.existing_relation_list)
        frame.setLayout(frame_layout)
        return frame

    def horizontal_layout(self):
        frame = QFrame()
        frame_layout = QHBoxLayout()
        frame_layout.addWidget(self.class_list())
        frame_layout.addWidget(self.relations_list())
        frame_layout.addWidget(self.existing_relations_list())
        frame_layout.addWidget(self.map_widget())
        frame_layout.addSpacing(20)
        frame.setLayout(frame_layout)
        return frame

    def map_widget(self):
        root_dir = Path(__file__).parent
        img_dir = root_dir.parent.parent / 'img/'
        pixmap = QPixmap(str(img_dir) + '/Dienstkaart-cropped-resized.png')
        image_label = QLabel()
        image_label.setPixmap(pixmap)
        return image_label

    def reset_ui(self, _):
        self._ = _
