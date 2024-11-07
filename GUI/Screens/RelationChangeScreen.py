from pathlib import Path
from typing import List

import qtawesome as qta
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QVBoxLayout, QFrame, QHBoxLayout, QPushButton, \
    QWidget, QLineEdit, QLabel
from otlmow_model.OtlmowModel.Classes.ImplementatieElement.AIMObject import \
    AIMObject
from otlmow_model.OtlmowModel.Classes.ImplementatieElement.RelatieObject import RelatieObject

from GUI.Screens.RelationChangeElements.ExistingRelationListWidget import \
    ExistingRelationListWidget
from GUI.Screens.RelationChangeElements.NewExistingRelationListWidget import \
    NewExistingRelationListWidget
from GUI.Screens.RelationChangeElements.NewObjectListWidget import NewObjectListWidget
from GUI.Screens.RelationChangeElements.NewPossibleRelationListWidget import \
    NewPossibleRelationListWidget

from GUI.Screens.RelationChangeElements.ObjectListWidget import ObjectListWidget
from GUI.Screens.RelationChangeElements.PossibleRelationListWidget import \
    PossibleRelationListWidget
from GUI.Screens.RelationChangeElements.RelationChangeHelpers import RelationChangeHelpers
from GUI.Screens.Screen import Screen


class RelationChangeScreen(Screen):
    def __init__(self, language_settings=None):
        super().__init__()
        self._ = language_settings

        self.selected_object_col1 = None

        #gui elements
        self.container_insert_data_screen = QVBoxLayout()
        self.window = None
        self.window_layout = None

        self.input_field = None

        self.frame_layout = None

        self.objects_list_gui = NewObjectListWidget(self._)
        self.possible_relation_list_gui = NewPossibleRelationListWidget(self._)
        self.existing_relation_list_gui = NewExistingRelationListWidget(self._)

        self.init_ui()


    def init_ui(self) -> None:
        self.container_insert_data_screen.addSpacing(10)
        self.container_insert_data_screen.addWidget(self.create_menu())
        self.container_insert_data_screen.addStretch()
        self.container_insert_data_screen.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.container_insert_data_screen)

    def create_menu(self) -> QWidget:
        self.window = QWidget()
        self.window.setProperty('class', 'background-box')
        self.window_layout = QVBoxLayout()
        self.window_layout.addSpacing(10)
        self.window_layout.addWidget(self.horizontal_layout())
        self.window.setLayout(self.window_layout)

        return self.window

    def input_file_selector(self) -> QFrame:
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

    def fill_object_list(self, objects: List[AIMObject]) -> None:
        self.objects_list_gui.fill_list(None,objects)
        
    def fill_existing_relations_list(self, relations_objects: List[RelatieObject]) -> None:
        self.existing_relation_list_gui.fill_list(None,relations_objects)

    def fill_possible_relations_list(self, source_object: AIMObject,
                                     relations: dict[str, list[RelatieObject]]) -> None:
        self.possible_relation_list_gui.fill_list(source_object,relations)

    def horizontal_layout(self):
        frame = QFrame()
        self.frame_layout = QHBoxLayout()
        self.frame_layout.addWidget(self.objects_list_gui.create_object_list_gui())
        self.frame_layout.addWidget(self.possible_relation_list_gui.create_object_list_gui(multi_select=True))
        self.frame_layout.addWidget(self.existing_relation_list_gui.create_object_list_gui(multi_select=True))
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

    def fill_object_attribute_field(self, object_attribute_dict:dict):
        self.objects_list_gui.fill_object_attribute_field(object_attribute_dict)

    def fill_possible_relation_attribute_field(self, possible_relation_attribute_dict:dict):
        self.possible_relation_list_gui.fill_object_attribute_field(possible_relation_attribute_dict)

    def fill_existing_relation_attribute_field(self, existing_relation_attribute_dict: dict):
        self.existing_relation_list_gui.fill_object_attribute_field(
            existing_relation_attribute_dict)

    def expand_existing_relations_folder_of(self,OTL_object:AIMObject):
        abbr_relation_typeURI = RelationChangeHelpers.get_abbreviated_typeURI(otl_object=OTL_object)
        self.existing_relation_list_gui.expand_folder_of(abbr_relation_typeURI)