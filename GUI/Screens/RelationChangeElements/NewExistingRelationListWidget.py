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


class NewExistingRelationListWidget(AbstractInstanceListWidget):

    Text = namedtuple('text', ['relation_typeURI', 'name_source', 'direction', 'name_target'])
    Data = namedtuple('data', ["index"])

    def __init__(self, language_settings):
        super().__init__(language_settings, 'existing_relations_list',
                         'existing_relation_attributes')

    def object_selected_listener(self, item) -> None:
      pass

    def on_item_selected(self, selected, deselected):
        no_item_selected = True
        # Get the currently selected indexes
        for index in selected.indexes():
            item = self.list_gui.model.itemFromIndex(index)
            if item and item.isSelectable():
                no_item_selected = False

        self.existing_relations_selected()
        self.set_list_button_enabled(not no_item_selected)

    def set_list_button_enabled(self, item_selected):
        if not item_selected:
            if self.list_button.isEnabled():
                self.list_button.setEnabled(False)
        elif not self.list_button.isEnabled():
            self.list_button.setEnabled(True)

    def create_button(self):
        self.list_button.setText(self._('remove_relation'))
        self.list_button.setDisabled(True)
        self.list_button.clicked.connect(
            self.remove_existing_relations_listener)
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
                text = f"{text_and_data['text'].relation_typeURI} | {text_and_data['text'].name_source} {text_and_data['text'].direction} {text_and_data['text'].name_target}"
                instance_item = QStandardItem(f"{text}")

                instance_item.setData(text_and_data["data"].index,self.data_1_index)
                instance_item.setData("instance",self.item_type_data_index)

                self.type_to_items_dict[asset_type].append(instance_item)

                instance_item.setEditable(False)  # Make the item name non-editable
                folder_item.appendRow(instance_item)

        #TODO: search is only on the top-level item now (folder name)
        item_list = self.filter_on_search_text(items=item_list)

        for folder_item in item_list:
            self.list_gui.addItem(folder_item)

    def existing_relations_selected(self):
        indices: list[int] = self.get_selected_data()

        RelationChangeDomain.select_existing_relation_indices(indices)

    def get_selected_data(self):
        return [
            self.list_gui.model.itemFromIndex(model_i).data(self.data_1_index)
            for model_i in self.list_gui.selectionModel().selectedIndexes()]

    def remove_existing_relations_listener(self):
        indices: list[int] = sorted(self.get_selected_data(), reverse=True)

        for index in indices:
            RelationChangeDomain.remove_existing_relation(index)

    def extract_text_and_data_per_item(self, source_object, objects):
        list_of_corresponding_values = []
        Text = self.Text
        Data = self.Data

        for i, relation_object in enumerate(objects):

            source_object = RelationChangeDomain.get_object(
                relation_object.bronAssetId.identificator)
            target_object = RelationChangeDomain.get_object(
                relation_object.doelAssetId.identificator)
            screen_name_source = RelationChangeHelpers.get_screen_name(OTL_object=source_object)
            screen_name_target = RelationChangeHelpers.get_screen_name(target_object)

            abbr_typeURI = RelationChangeHelpers.get_abbreviated_typeURI(relation_object)

            direction = RelationChangeHelpers.get_screen_icon_direction("Unspecified")

            if OTLObjectHelper.is_directional_relation(relation_object):
                direction = RelationChangeHelpers.get_screen_icon_direction(
                    "Source -> Destination")

            list_of_corresponding_values.append({
                "text": Text(abbr_typeURI, screen_name_source, direction, screen_name_target),
                "data": Data(i)
            })

        list_of_corresponding_values.sort(key=lambda val: (
            val['text'].relation_typeURI if val['text'].relation_typeURI is not None else "xxx",
            val['text'].name_source if val['text'].name_source is not None else "xxx",
            val['text'].name_target if val['text'].name_target is not None else "xxx"))

        return list_of_corresponding_values