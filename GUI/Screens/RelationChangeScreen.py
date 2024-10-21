from pathlib import Path
from typing import List, Optional

import qtawesome as qta
from PyQt6.QtGui import QPixmap

from PyQt6.QtWidgets import QVBoxLayout, QFrame, QHBoxLayout, QPushButton, \
    QWidget, QLineEdit, QLabel, QListWidget, QListWidgetItem
from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLObject
from otlmow_model.OtlmowModel.Classes.ImplementatieElement.AIMObject import \
    AIMObject
from otlmow_modelbuilder.SQLDataClasses.OSLORelatie import OSLORelatie

from Domain.RelationChangeDomain import RelationChangeDomain
from GUI.Screens.Screen import Screen
from UnitTests.TestClasses.Classes.ImplementatieElement.RelatieObject import RelatieObject


class RelationChangeScreen(Screen):
    def __init__(self, language_settings=None):
        super().__init__()
        self._ = language_settings

        #gui elements
        self.container_insert_data_screen = QVBoxLayout()
        self.window = None
        self.window_layout = None

        self.input_field = None

        self.frame_layout = None
        self.object_list_gui = None
        self.relation_list_gui = None
        self.existing_relation_list_gui = None

        self.init_ui()



    def init_ui(self):
        self.container_insert_data_screen.addSpacing(10)
        self.container_insert_data_screen.addWidget(self.create_menu())
        self.container_insert_data_screen.addStretch()
        self.container_insert_data_screen.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.container_insert_data_screen)

    def create_menu(self):
        self.window = QWidget()
        self.window.setProperty('class', 'background-box')
        self.window_layout = QVBoxLayout()
        self.window_layout.addSpacing(10)
        self.window_layout.addWidget(self.input_file_field())
        self.window_layout.addSpacing(10)
        self.window_layout.addWidget(self.horizontal_layout())
        self.window.setLayout(self.window_layout)

        # self.fill_relations_list()

        return self.window

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

    def create_object_list_gui(self):
        frame = QFrame()
        frame_layout = QVBoxLayout()
        class_label = QLabel()
        class_label.setText(self._('class_list'))
        self.object_list_gui = QListWidget()
        self.object_list_gui.setProperty('class', 'list')
        self.object_list_gui.itemSelectionChanged.connect(self.object_selected)

        frame_layout.addWidget(class_label)
        frame_layout.addWidget(self.object_list_gui)
        frame.setLayout(frame_layout)
        return frame

    def fill_object_list(self, objects: List[AIMObject]):
        self.object_list_gui.clear()
        for OTL_object in objects:
            item = QListWidgetItem()
            item.setData(1, OTL_object.assetId.identificator)
            # item.clicked.connect(self.object_selected)

            screen_name = str(OTL_object.assetId.identificator)
            if hasattr(OTL_object, 'naam') and OTL_object.naam:
                screen_name = OTL_object.naam

            abbr_typeURI = OTL_object.typeURI.replace("https://wegenenverkeer.data.vlaanderen.be/ns/","")

            item.setText("{0} | {1}".format(abbr_typeURI,screen_name))

            self.object_list_gui.addItem(item)


    def object_selected(self):
        
        for i in range(self.object_list_gui.count()):
            if self.object_list_gui.item(i).isSelected():
                if selected_object := RelationChangeDomain.get_object(
                                        identificator=self.object_list_gui.item(i).data(1)):
                    RelationChangeDomain.set_possible_relations(selected_object)
                break

        
        
    def fill_existing_relations_list(self, relations_objects: List[RelatieObject]):
        self.existing_relation_list_gui.clear()
        for relation_object in relations_objects:
            item = QListWidgetItem()
            item.setText(self._(
                relation_object.typeURI.replace("https://wegenenverkeer.data.vlaanderen.be/ns/",
                                           "")))  # + "/" + str(OTL_object.assetId.identificator)))


            self.existing_relation_list_gui.addItem(item)

    def fill_possible_relations_list(self, relations: dict[str,list[OSLORelatie]]):

        # sourcery skip: remove-dict-keys
        self.relation_list_gui.clear()
        for identificator in relations.keys():
            OTL_object: AIMObject = RelationChangeDomain.get_object(identificator)
            for relation in relations[identificator]:

                item = QListWidgetItem()
                screen_name = str(OTL_object.assetId.identificator)
                if hasattr(OTL_object, 'naam') and OTL_object.naam:
                    screen_name = OTL_object.naam

                abbr_target_object_typeURI = OTL_object.typeURI.replace(
                    "https://wegenenverkeer.data.vlaanderen.be/ns/", "")

                abbr_relation_typeURI = relation.objectUri.replace(
                    "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#", "")

                richting = "<->"
                if relation.richting == "Source -> Destination":
                    richting = "-->"
                elif relation.richting == "Destination -> Source":
                    richting = "<--"

                item.setText("{0} {1} {2} | {3}".format(abbr_relation_typeURI,richting, screen_name,abbr_target_object_typeURI))

                self.relation_list_gui.addItem(item)

    def create_relations_list_gui(self):
        frame = QFrame()
        frame_layout = QVBoxLayout()
        relations_label = QLabel()
        relations_label.setText(self._('relations_list'))
        self.relation_list_gui = QListWidget()
        self.relation_list_gui.setProperty('class', 'list')

        frame_layout.addWidget(relations_label)
        frame_layout.addWidget(self.relation_list_gui)
        frame.setLayout(frame_layout)
        return frame

    # def fill_relations_list(self):
    #     self.relation_list_gui.clear()
    #     item = QListWidgetItem()
    #     item.setText(self._("loading"))
    #     self.relation_list_gui.addItem(item)

    def create_existing_relations_list_gui(self):
        frame = QFrame()
        frame_layout = QVBoxLayout()
        existing_rel_label = QLabel()
        existing_rel_label.setText(self._('existing_relations_list'))
        self.existing_relation_list_gui = QListWidget()
        self.existing_relation_list_gui.setProperty('class', 'list')

        frame_layout.addWidget(existing_rel_label)
        frame_layout.addWidget(self.existing_relation_list_gui)
        frame.setLayout(frame_layout)
        return frame

    def horizontal_layout(self):
        frame = QFrame()
        self.frame_layout = QHBoxLayout()
        self.frame_layout.addWidget(self.create_object_list_gui())
        self.frame_layout.addWidget(self.create_relations_list_gui())
        self.frame_layout.addWidget(self.create_existing_relations_list_gui())
        # self.frame_layout.addWidget(self.map_widget())
        self.frame_layout.addSpacing(20)
        frame.setLayout(self.frame_layout)
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
