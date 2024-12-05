from pathlib import Path
from typing import List

import qtawesome as qta
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QVBoxLayout, QFrame, QHBoxLayout, QPushButton, \
    QWidget, QLineEdit, QLabel
from otlmow_model.OtlmowModel.Classes.ImplementatieElement.AIMObject import \
    AIMObject
from otlmow_model.OtlmowModel.Classes.ImplementatieElement.RelatieObject import RelatieObject

from Domain.RelationChangeDomain import RelationChangeDomain
from GUI.DialogWindows.DefineHeeftBetrokkeneRelationWindow import \
    DefineHeeftBetrokkeneRelationWindow
from GUI.Screens.RelationChangeElements.ExistingRelationListWidget import \
    ExistingRelationListWidget
from GUI.Screens.RelationChangeElements.ObjectListWidget import ObjectListWidget
from GUI.Screens.RelationChangeElements.PossibleRelationListWidget import \
    PossibleRelationListWidget


from GUI.Screens.RelationChangeElements.RelationChangeHelpers import RelationChangeHelpers
from GUI.Screens.Screen import Screen
from LatestReleaseMulti.OTLWizard.data.otlmow_model.OtlmowModel.Classes.Onderdeel.HeeftBetrokkene import \
    HeeftBetrokkene


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

        self.objects_list_gui = ObjectListWidget(self._,self)
        self.possible_relation_list_gui = PossibleRelationListWidget(self._,self)
        self.existing_relation_list_gui = ExistingRelationListWidget(self._,self)

        self.init_ui()


    def paintEvent(self, a0):
        self.synchronize_subtext_label_heights()
        super().paintEvent(a0)

    def synchronize_subtext_label_heights(self):
        frame_rect_height = self.possible_relation_list_gui.list_subtext_label.frameRect().height()
        frame_rect_object = self.objects_list_gui.list_subtext_label.frameRect()
        frame_rect_exist = self.existing_relation_list_gui.list_subtext_label.frameRect()
        if frame_rect_height != frame_rect_object.height():
            self.objects_list_gui.list_subtext_label.setMinimumHeight(frame_rect_height)
        if frame_rect_height != frame_rect_exist.height():
            self.existing_relation_list_gui.list_subtext_label.setMinimumHeight(frame_rect_height)

    def init_ui(self) -> None:
        # self.container_insert_data_screen.addSpacing(5)
        self.container_insert_data_screen.addWidget(self.create_menu())
        # self.container_insert_data_screen.addStretch()
        self.container_insert_data_screen.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.container_insert_data_screen)

    def create_menu(self) -> QWidget:
        self.window = QWidget()
        self.window.setProperty('class', 'background-box')
        self.window_layout = QVBoxLayout()
        # self.window_layout.addSpacing(10)
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
        self.objects_list_gui.fill_list(None, objects, [])
        
    def fill_existing_relations_list(self, relations_objects: List[RelatieObject], last_added: list[RelatieObject] = None) -> None:
        if last_added is None:
            last_added = []
        self.existing_relation_list_gui.fill_list(None, relations_objects, last_added)

    def fill_possible_relations_list(self, source_object: AIMObject,
                                     relations: dict[str, list[RelatieObject]], last_added=None) -> None:
        if last_added is None:
            last_added = []
        self.possible_relation_list_gui.fill_list(source_object, relations,last_added)

    def horizontal_layout(self):
        frame = QFrame()
        self.frame_layout = QHBoxLayout()
        self.frame_layout.setSpacing(0)
        self.frame_layout.addWidget(self.objects_list_gui.create_object_list_gui())
        self.frame_layout.addWidget(self.possible_relation_list_gui.create_object_list_gui(multi_select=True))
        self.frame_layout.addWidget(self.existing_relation_list_gui.create_object_list_gui(multi_select=True))

        self.frame_layout.setStretch(0, 1)
        self.frame_layout.setStretch(1, 1)
        self.frame_layout.setStretch(2, 1)

        # self.frame_layout.addWidget(self.map_widget())
        # self.frame_layout.addSpacing(20)
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

    def expand_existing_relations_folder_of(self, relation_typeURI:str):
        add_namespace = RelationChangeHelpers.is_unique_across_namespaces(
            relation_typeURI,
            RelationChangeDomain.shown_objects)
        abbr_relation_typeURI = RelationChangeHelpers.get_abbreviated_typeURI(
            typeURI=relation_typeURI,
            add_namespace=add_namespace,
            is_relation=True)
        self.existing_relation_list_gui.expand_folder_of(abbr_relation_typeURI)

    def expand_possible_relations_folder_of(self, relation_typeURI:str):
        add_namespace = RelationChangeHelpers.is_unique_across_namespaces(
            relation_typeURI,
            RelationChangeDomain.shown_objects)
        abbr_relation_typeURI = RelationChangeHelpers.get_abbreviated_typeURI(
            typeURI=relation_typeURI,
            add_namespace=add_namespace,
            is_relation=True)
        self.possible_relation_list_gui.expand_folder_of(abbr_relation_typeURI)

    def showMultiSelectionHeeftBetrokkeneAttributeDialogWindow(self, data_list_and_relation_objects:list):
        dialogWindow = DefineHeeftBetrokkeneRelationWindow(self._, data_list_and_relation_objects)
        dialogWindow.draw_define_heeft_betrokkene_rol_window()
