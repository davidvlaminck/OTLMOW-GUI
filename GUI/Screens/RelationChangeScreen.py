from collections import namedtuple
from pathlib import Path
from typing import List, Optional

import qtawesome as qta
from PyQt6.QtGui import QPixmap, QPalette, QColorConstants
from PyQt6.QtWidgets import QVBoxLayout, QFrame, QHBoxLayout, QPushButton, \
    QWidget, QLineEdit, QLabel, QListWidget, QListWidgetItem, QHeaderView, QTreeWidget, \
    QTreeWidgetItem
from otlmow_converter.DotnotationDictConverter import DotnotationDictConverter
from otlmow_model.OtlmowModel.Classes.ImplementatieElement.AIMObject import \
    AIMObject
from otlmow_model.OtlmowModel.Classes.ImplementatieElement.RelatieObject import RelatieObject
from otlmow_model.OtlmowModel.Helpers.OTLObjectHelper import is_directional_relation

from Domain.RelationChangeDomain import RelationChangeDomain
from GUI.ButtonWidget import ButtonWidget
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

        self.object_list_gui = None
        self.object_attribute_field: QTreeWidget = QTreeWidget()
        self.hidden_object_list_button = ButtonWidget()

        self.possible_relation_list_gui = None
        self.add_possible_relation_to_existing_button = ButtonWidget()
        self.possible_relation_attribute_field: QTreeWidget = QTreeWidget()

        self.existing_relation_list_gui = None
        self.remove_existing_relation_button = ButtonWidget()
        self.existing_relation_attribute_field: QTreeWidget = QTreeWidget()

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
        self.window_layout.addWidget(self.input_file_selector())
        self.window_layout.addSpacing(10)
        self.window_layout.addWidget(self.horizontal_layout())
        self.window.setLayout(self.window_layout)


        # self.fill_relations_list()

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

    def create_object_list_gui(self) -> QFrame:
        frame = QFrame()
        frame_layout = QVBoxLayout()
        class_label = QLabel()
        class_label.setText(self._('class_list'))
        self.object_list_gui = QListWidget()
        self.object_list_gui.setProperty('class', 'list')
        self.object_list_gui.itemSelectionChanged.connect(self.object_selected)

        frame_layout.addWidget(class_label)
        frame_layout.addWidget(self.object_list_gui)

        object_attribute_label = QLabel()
        object_attribute_label.setText(self._('object_attributes'))
        frame_layout.addWidget(self.create_hidden_button())
        frame_layout.addWidget(object_attribute_label)


        frame_layout.addWidget(self.create_object_attribute_field(self.object_attribute_field))
        frame.setLayout(frame_layout)

        return frame

    def create_hidden_button(self):
        self.hidden_object_list_button.setEnabled(False)
        self.hidden_object_list_button.setText("hidden")
        self.hidden_object_list_button.setProperty("class", "invisible")
        return self.hidden_object_list_button

    def fill_object_list(self, objects: List[AIMObject]) -> None:
        self.object_list_gui.clear()
        for OTL_object in objects:
            item = QListWidgetItem()
            item.setData(1, OTL_object.assetId.identificator)
            # item.clicked.connect(self.object_selected)

            screen_name = self.get_screen_name(OTL_object)

            abbr_typeURI = OTL_object.typeURI.replace("https://wegenenverkeer.data.vlaanderen.be/ns/","")

            item.setText(f"{screen_name} | {abbr_typeURI}")

            self.object_list_gui.addItem(item)

    def object_selected(self) -> None:
        
        for i in range(self.object_list_gui.count()):
            if self.object_list_gui.item(i).isSelected():
                self.selected_object_col1 = RelationChangeDomain.get_object(
                                        identificator=self.object_list_gui.item(i).data(1))
                if self.selected_object_col1 is not None:
                    RelationChangeDomain.set_possible_relations(
                        selected_object=self.selected_object_col1)


                break

    def fill_existing_relations_list(self, relations_objects: List[RelatieObject]) -> None:
        self.existing_relation_list_gui.clear()

        Text = namedtuple('text', ['relation_typeURI', 'name_source', 'direction', 'name_target'])
        Data = namedtuple('data', ["index"])

        list_of_corresponding_values = []
        for i,relation_object  in enumerate(relations_objects):

            source_object = RelationChangeDomain.get_object(relation_object.bronAssetId.identificator)
            target_object = RelationChangeDomain.get_object(relation_object.doelAssetId.identificator)
            screen_name_source = self.get_screen_name(OTL_object=source_object)
            screen_name_target = self.get_screen_name(target_object)

            abbr_typeURI = relation_object.typeURI.replace(
                "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#", "")

            direction = self.get_screen_icon_direction("Unspecified")

            if is_directional_relation(relation_object):
                direction = self.get_screen_icon_direction("Source -> Destination")

            list_of_corresponding_values.append({
                "text": Text(abbr_typeURI, screen_name_source, direction, screen_name_target),
                "data": Data(i)
            })

        list_of_corresponding_values.sort(key=lambda val: (
            val['text'].relation_typeURI if val['text'].relation_typeURI is not None else "xxx",
            val['text'].name_source if val['text'].name_source is not None else "xxx",
            val['text'].name_target if val['text'].name_target is not None else "xxx"))

        for val in list_of_corresponding_values:
            item = QListWidgetItem()
            item.setText(f"{val['text'].relation_typeURI} | {val['text'].name_source} {val['text'].direction} {val['text'].name_target}")
            item.setData(3,val["data"].index)
            self.existing_relation_list_gui.addItem(item)

    def get_screen_name(self, OTL_object:AIMObject) -> Optional[str]:
        if OTL_object is None:
            return None

        return (
            OTL_object.naam
            if hasattr(OTL_object, 'naam') and OTL_object.naam
            else str(OTL_object.assetId.identificator)
        )

    def fill_possible_relations_list(self, source_object: AIMObject,
                                     relations: dict[str, list[RelatieObject]]) -> None:

        # sourcery skip: remove-dict-keys
        self.possible_relation_list_gui.clear()

        Text = namedtuple('text', ['source_typeURI', 'direction', 'screen_name','target_typeURI'])
        Data = namedtuple('data', ['source_id','target_id',"index"])

        list_of_corresponding_values = []
        for target_identificator, target_relations  in relations.items():

            for i, relation in  enumerate(target_relations):

                target_object: AIMObject = RelationChangeDomain.get_object(
                    relation.doelAssetId.identificator)

                direction = ""
                if (is_directional_relation(relation)):
                    if (relation.bronAssetId.identificator == target_identificator):
                        direction = self.get_screen_icon_direction("Destination -> Source")
                        target_object = RelationChangeDomain.get_object(
                    relation.bronAssetId.identificator)
                    else:
                        direction = self.get_screen_icon_direction("Source -> Destination")

                else:
                    direction = self.get_screen_icon_direction("Unspecified")

                screen_name = self.get_screen_name(target_object)

                abbr_target_object_typeURI = target_object.typeURI.replace(
                    "https://wegenenverkeer.data.vlaanderen.be/ns/", "")

                abbr_relation_typeURI = relation.typeURI.replace(
                    "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#", "")


                list_of_corresponding_values.append({
                    "text":Text(abbr_relation_typeURI, direction, screen_name,abbr_target_object_typeURI),
                    "data":Data(source_object.assetId.identificator,target_identificator,i)
                })

        list_of_corresponding_values.sort(key=lambda val: (val['text'].target_typeURI, val['text'].screen_name, val['text'].source_typeURI))

        for val in list_of_corresponding_values:
            item = QListWidgetItem()
            text = f"{val['text'].source_typeURI} {val['text'].direction} {val['text'].screen_name} | {val['text'].target_typeURI}"
            item.setText(text)

            # item.setData(1,text_args['data'][0])
            # item.setData(2, text_args['data'][1])
            item.setData(3, val['data'].source_id)
            item.setData(4, val['data'].target_id)
            item.setData(5, val['data'].index)

            self.possible_relation_list_gui.addItem(item)

    def add_possible_relation_to_existing_relations(self):
        Data = namedtuple('data', ['source_id', 'target_id', "index"])
        data_list: list[Data] = [
            Data(item.data(3), item.data(4), item.data(5))
            for item in self.possible_relation_list_gui.selectedItems()]

        for data in data_list:
            RelationChangeDomain.add_possible_relation_to_existing_relations(data.source_id,data.target_id,data.index)

    def get_screen_icon_direction(self, input_richting:str):
        richting = "<->"
        if input_richting == "Source -> Destination":
            richting = "-->"
        elif input_richting == "Destination -> Source":
            richting = "<--"
        return richting

    def create_relations_list_gui(self):
        frame = QFrame()
        frame_layout = QVBoxLayout()
        relations_label = QLabel()
        relations_label.setText(self._('relations_list'))
        self.possible_relation_list_gui = QListWidget()
        self.possible_relation_list_gui.setProperty('class', 'list')
        self.possible_relation_list_gui.itemSelectionChanged.connect(self.enable_add_relations_button_if_possible_relations_selected)
        self.possible_relation_list_gui.setSelectionMode(QListWidget.SelectionMode.MultiSelection)

        self.add_possible_relation_to_existing_button.setText(self._('add_relation'))
        self.add_possible_relation_to_existing_button.setDisabled(True)
        self.add_possible_relation_to_existing_button.clicked.connect(self.add_possible_relation_to_existing_relations)
        self.add_possible_relation_to_existing_button.setProperty('class', 'primary-button')

        frame_layout.addWidget(relations_label)
        frame_layout.addWidget(self.possible_relation_list_gui)
        frame_layout.addWidget(self.add_possible_relation_to_existing_button)

        possible_relation_attribute_label = QLabel()
        possible_relation_attribute_label.setText(self._('possible_relation_attributes'))
        frame_layout.addWidget(possible_relation_attribute_label)
        frame_layout.addWidget(self.create_object_attribute_field(self.possible_relation_attribute_field))

        frame.setLayout(frame_layout)
        return frame

    # def fill_relations_list(self):
    #     self.relation_list_gui.clear()
    #     item = QListWidgetItem()
    #     item.setText(self._("loading"))
    #     self.relation_list_gui.addItem(item)

    def enable_add_relations_button_if_possible_relations_selected(self) -> None:
        """Check the selection state of possible relations and update the button accordingly.

        This function enables or disables the 'add possible relation to existing' button based on whether
        any items are selected in the possible relation list. If items are selected, the button is enabled;
        if no items are selected, the button is disabled.

        Args:
            self: The instance of the class.

        Returns:
            None
        """

        self.add_possible_relation_to_existing_button.isEnabled()
        if len(list(self.possible_relation_list_gui.selectedItems())):
            if not self.add_possible_relation_to_existing_button.isEnabled():
                self.add_possible_relation_to_existing_button.setEnabled(True)
        elif self.add_possible_relation_to_existing_button.isEnabled():
            self.add_possible_relation_to_existing_button.setEnabled(False)

        self.possible_relations_selected()

    def enable_remove_relations_button_if_existing_relations_selected(self) -> None:

        self.remove_existing_relation_button.isEnabled()
        if len(list(self.existing_relation_list_gui.selectedItems())):
            if not self.remove_existing_relation_button.isEnabled():
                self.remove_existing_relation_button.setEnabled(True)
        elif self.remove_existing_relation_button.isEnabled():
            self.remove_existing_relation_button.setEnabled(False)

        self.existing_relations_selected()

    def create_existing_relations_list_gui(self):
        frame = QFrame()
        frame_layout = QVBoxLayout()
        existing_rel_label = QLabel()
        existing_rel_label.setText(self._('existing_relations_list'))
        self.existing_relation_list_gui = QListWidget()
        self.existing_relation_list_gui.setProperty('class', 'list')
        self.existing_relation_list_gui.itemSelectionChanged.connect(
            self.enable_remove_relations_button_if_existing_relations_selected)
        self.existing_relation_list_gui.setSelectionMode(QListWidget.SelectionMode.MultiSelection)

        self.remove_existing_relation_button.setText(self._('remove_relation'))
        self.remove_existing_relation_button.setDisabled(True)
        self.remove_existing_relation_button.clicked.connect(
            self.remove_existing_relations)
        self.remove_existing_relation_button.setProperty('class', 'primary-button')

        frame_layout.addWidget(existing_rel_label)
        frame_layout.addWidget(self.existing_relation_list_gui)
        frame_layout.addWidget(self.remove_existing_relation_button)
        existing_relation_attribute_label = QLabel()
        existing_relation_attribute_label.setText(self._('existing_relation_attributes'))
        frame_layout.addWidget(existing_relation_attribute_label)
        frame_layout.addWidget(self.create_object_attribute_field(self.existing_relation_attribute_field))

        frame.setLayout(frame_layout)
        return frame

    def remove_existing_relations(self):
        indices: list[int] = [
            item.data(3)
            for item in self.existing_relation_list_gui.selectedItems()]

        for index in indices:
            RelationChangeDomain.remove_existing_relation(index)

    def existing_relations_selected(self):
        indices: list[int] = [
            item.data(3)
            for item in self.existing_relation_list_gui.selectedItems()]

        RelationChangeDomain.select_existing_relation_indices(indices)

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

    def create_object_attribute_field(self, attribute_field: QTreeWidget):

        attribute_field.setColumnCount(2)
        attribute_field.setProperty('class', 'list')
        attribute_field.setHeaderHidden(True)

        header = attribute_field.header()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setStretchLastSection(False)

        return attribute_field

    def fill_object_attribute_field(self, object_attribute_dict:dict):
        self.fill_attribute_field(self.object_attribute_field, object_attribute_dict)

    def fill_possible_relation_attribute_field(self, possible_relation_attribute_dict:dict):
        self.fill_attribute_field(self.possible_relation_attribute_field, possible_relation_attribute_dict)

    def fill_existing_relation_attribute_field(self, existing_relation_attribute_dict: dict):
        self.fill_attribute_field(self.existing_relation_attribute_field, existing_relation_attribute_dict)

    def fill_attribute_field(self, field, object_attribute_dict):
        field.clear()
        for attribute, value in object_attribute_dict.items():
            list_item = QTreeWidgetItem()
            list_item.setText(0, attribute)
            list_item.setText(1, str(value))
            field.addTopLevelItem(list_item)

    def possible_relations_selected(self):
        Data = namedtuple('data', ['source_id', 'target_id', "index"])
        data_list: list[Data] = [
            Data(item.data(3), item.data(4), item.data(5))
            for item in self.possible_relation_list_gui.selectedItems()]

        RelationChangeDomain.select_possible_relation_keys(data_list)
