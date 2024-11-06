from collections import namedtuple
from typing import Optional, Collection

from PyQt6.QtGui import QStandardItem
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QTreeView
from otlmow_model.OtlmowModel.Helpers import OTLObjectHelper

from Domain.RelationChangeDomain import RelationChangeDomain
from GUI.Screens.RelationChangeElements.AbstractInstanceListWidget import \
    AbstractInstanceListWidget
from GUI.Screens.RelationChangeElements.FolderTreeView import FolderTreeView
from GUI.Screens.RelationChangeElements.RelationChangeHelpers import RelationChangeHelpers
from UnitTests.TestClasses.Classes.ImplementatieElement.AIMObject import AIMObject


class NewPossibleRelationListWidget(AbstractInstanceListWidget):

    Text = namedtuple('text', ['relation_typeURI', 'direction', 'screen_name', 'target_typeURI'])
    Data = namedtuple('data', ['source_id', 'target_id', "index"])

    def __init__(self, language_settings):
        super().__init__(language_settings,'relations_list','possible_relation_attributes')



    def object_selected_listener(self, item) -> None:
      pass

    def on_item_selected(self, selected, deselected):
        no_item_selected = True
        # Get the currently selected indexes
        for index in selected.indexes():
            item = self.list_gui.model.itemFromIndex(index)
            if item and item.isSelectable():
                no_item_selected = False
                self.possible_relations_selected()

        self.set_list_button_enabled(not no_item_selected)

    def set_list_button_enabled(self, item_selected):
        if not item_selected:
            if self.list_button.isEnabled():
                self.list_button.setEnabled(False)
        elif not self.list_button.isEnabled():
            self.list_button.setEnabled(True)

    def create_button(self):
        self.list_button.setText(self._('add_relation'))
        self.list_button.setDisabled(True)
        self.list_button.clicked.connect(
            self.add_possible_relation_to_existing_relations_listener)
        self.list_button.setProperty('class', 'primary-button')
        return self.list_button

    def create_object_list_gui(self, multi_select: bool = False) -> QFrame:
        frame = QFrame()
        frame_layout = QVBoxLayout()
        list_label = QLabel()
        list_label.setText(self.list_label_text)
        self.list_gui = FolderTreeView()
        self.list_gui.setProperty('class', 'list')
        self.list_gui.selectionModel().selectionChanged.connect(self.on_item_selected)
        if multi_select:
            self.list_gui.setSelectionMode(QTreeView.SelectionMode.MultiSelection)

        frame_layout.addWidget(list_label)
        frame_layout.addWidget(self.create_search_bar())
        frame_layout.addWidget(self.list_gui)

        object_attribute_label = QLabel()
        object_attribute_label.setText(self.attribute_field_label_text)
        frame_layout.addWidget(self.create_button())
        frame_layout.addWidget(object_attribute_label)

        frame_layout.addWidget(self.create_attribute_field())
        frame.setLayout(frame_layout)

        return frame

    def fill_list(self, source_object: Optional[AIMObject], objects: Collection) -> None:
        # sourcery skip: remove-dict-keys
        # objects = RelationChangeDomain.objects
        self.list_gui.clear()

        text_and_data_per_element = self.extract_text_and_data_per_item(source_object, objects)

        item_list = []
        type_to_instance_dict = {}

        for text_and_data in text_and_data_per_element:

            abbr_typeURI = text_and_data['text'].relation_typeURI

            if abbr_typeURI in type_to_instance_dict.keys():
                type_to_instance_dict[abbr_typeURI].append(text_and_data)
            else:
                type_to_instance_dict[abbr_typeURI] = [text_and_data]

        for asset_type, text_and_data_list in type_to_instance_dict.items():
            folder_item = self.create_asset_type_standard_item(asset_type)

            item_list.append(folder_item)

            self.type_to_items_dict[asset_type] = []
            self.type_open_status[asset_type] = False
            for text_and_data in text_and_data_list:
                text = f"{text_and_data['text'].direction} {text_and_data['text'].screen_name} | {text_and_data['text'].target_typeURI}"
                instance_item = QStandardItem(f"{text}")

                instance_item.setData(text_and_data['data'].source_id,self.data_1_index)
                instance_item.setData(text_and_data['data'].target_id,self.data_2_index)
                instance_item.setData(text_and_data['data'].index,self.data_3_index)
                instance_item.setData("instance",self.item_type_data_index)

                self.type_to_items_dict[asset_type].append(instance_item)

                instance_item.setEditable(False)  # Make the item name non-editable
                folder_item.appendRow(instance_item)

        #TODO: search is only on the top-level item now (folder name)
        item_list = self.filter_on_search_text(items=item_list)

        for folder_item in item_list:
            self.list_gui.addItem(folder_item)

    def add_possible_relation_to_existing_relations_listener(self):
        Data = self.Data
        data_list: list[Data] = sorted(self.get_selected_data(), reverse=True)

        for data in data_list:
            RelationChangeDomain.add_possible_relation_to_existing_relations(data.source_id,
                                                                             data.target_id,
                                                                             data.index)

    def possible_relations_selected(self):
        Data = self.Data
        data_list: list[Data] = self.get_selected_data()

        RelationChangeDomain.select_possible_relation_data(data_list)

    def get_selected_data(self):
        return [
            self.Data(self.list_gui.model.itemFromIndex(model_i).data(self.data_1_index),
                      self.list_gui.model.itemFromIndex(model_i).data(self.data_2_index),
                      self.list_gui.model.itemFromIndex(model_i).data(self.data_3_index))
            for model_i in self.list_gui.selectionModel().selectedIndexes()]

    def extract_text_and_data_per_item(self, source_object, objects):
        list_of_corresponding_values = []
        for target_identificator, target_relations in objects.items():

            for i, relation in enumerate(target_relations):

                target_object: AIMObject = RelationChangeDomain.get_object(
                    relation.doelAssetId.identificator)

                direction = ""
                if OTLObjectHelper.is_directional_relation(relation):
                    if relation.bronAssetId.identificator == target_identificator:
                        direction = RelationChangeHelpers.get_screen_icon_direction(
                            "Destination -> Source")
                        target_object = RelationChangeDomain.get_object(
                            relation.bronAssetId.identificator)
                    else:
                        direction = RelationChangeHelpers.get_screen_icon_direction(
                            "Source -> Destination")

                else:
                    direction = RelationChangeHelpers.get_screen_icon_direction("Unspecified")

                screen_name = RelationChangeHelpers.get_screen_name(target_object)

                abbr_target_object_typeURI = RelationChangeHelpers.get_abbreviated_typeURI(
                    target_object)

                abbr_relation_typeURI = RelationChangeHelpers.get_abbreviated_typeURI(relation)

                list_of_corresponding_values.append({
                    "text": self.Text(abbr_relation_typeURI, direction, screen_name,
                                      abbr_target_object_typeURI),
                    "data": self.Data(source_object.assetId.identificator, target_identificator, i)
                })
        list_of_corresponding_values.sort(key=lambda val: (
            val['text'].target_typeURI, val['text'].screen_name, val['text'].relation_typeURI))
        return list_of_corresponding_values