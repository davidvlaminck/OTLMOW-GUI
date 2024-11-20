from collections import namedtuple
from typing import Optional, Collection

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItem
from otlmow_model.OtlmowModel.Helpers import OTLObjectHelper

from Domain.RelationChangeDomain import RelationChangeDomain
from GUI.Screens.RelationChangeElements.AbstractInstanceListWidget import \
    AbstractInstanceListWidget, IMG_DIR

from GUI.Screens.RelationChangeElements.RelationChangeHelpers import RelationChangeHelpers
from UnitTests.TestClasses.Classes.ImplementatieElement.AIMObject import AIMObject


class ExistingRelationListWidget(AbstractInstanceListWidget):

    Text = namedtuple('text', ['typeURI', 'name_source', 'direction', 'name_target','full_typeURI'])
    Data = namedtuple('data', ["index", "last_added"])

    def __init__(self, language_settings):
        super().__init__(language_settings=language_settings)

        self.list_label_text = self._("existing_relations_list")
        self.list_subtext_label_text = self._("existing_relations_description")
        self.attribute_field_label_text = self._("existing_relation_attributes")

    def on_item_selected_listener(self, selected, deselected):
        no_item_selected = True
        # Get the currently selected indexes
        for index in self.list_gui.selectionModel().selectedIndexes():
            if index.column() == 0:
                item = self.list_gui.model.itemFromIndex(index)
                if item and item.isSelectable():
                    no_item_selected = False

        self.existing_relations_selected()
        self.set_list_button_enabled(not no_item_selected)

    def set_list_button_enabled(self, item_selected:bool):
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
        self.list_button.setProperty('class', 'remove_relation-button')
        return self.list_button

    def create_instance_standard_item(self, text_and_data):
        text = f"{text_and_data['text'].name_source}"
        instance_item = QStandardItem(text)
        instance_item.setData(text_and_data["data"].index, self.data_1_index)
        instance_item.setData("instance", self.item_type_data_index)
        instance_item.setData(text_and_data["data"].last_added, self.data_last_added_index)

        instance_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)

        text2 = f"{text_and_data['text'].name_target}"
        instance_item2 = QStandardItem(text2)
        instance_item2.setTextAlignment(Qt.AlignmentFlag.AlignTop)
        # instance_item2.setData(text_and_data["data"].index, self.data_1_index)
        # instance_item2.setData("instance", self.item_type_data_index)

        self.add_direction_icon_to_item(instance_item=instance_item2,
                                        direction=text_and_data['text'].direction,
                                        typeURI= text_and_data['text'].full_typeURI)

        return instance_item, instance_item2

    def existing_relations_selected(self):
        indices: list[int] = self.get_selected_data()

        RelationChangeDomain.select_existing_relation_indices(indices)

    def get_selected_data(self):
        return [
            self.list_gui.model.itemFromIndex(model_i).data(self.data_1_index)
            for model_i in self.list_gui.selectionModel().selectedIndexes() if model_i.column() == 0]

    def remove_existing_relations_listener(self):
        indices: list[int] = sorted(self.get_selected_data(), reverse=True)

        # for index in indices:
        #     RelationChangeDomain.remove_existing_relation(index)
        RelationChangeDomain.remove_existing_relations(indices)

    def extract_text_and_data_per_item(self, source_object, objects, last_added):
        list_of_corresponding_values = []
        Text = self.Text
        Data = self.Data

        for i, relation_object in enumerate(objects):

            source_object = RelationChangeDomain.get_object(
                identificator=relation_object.bronAssetId.identificator)
            target_object = RelationChangeDomain.get_object(
                identificator=relation_object.doelAssetId.identificator)
            screen_name_source = RelationChangeHelpers.get_screen_name(OTL_object=source_object)
            screen_name_target = RelationChangeHelpers.get_screen_name(OTL_object=target_object)
            add_namespace = RelationChangeHelpers.is_unique_across_namespaces(
                typeURI=relation_object.typeURI,
                objects=RelationChangeDomain.objects)
            abbr_typeURI = RelationChangeHelpers.get_abbreviated_typeURI(
                typeURI=relation_object.typeURI,
                add_namespace=add_namespace,
                is_relation=OTLObjectHelper.is_relation(relation_object))

            direction = RelationChangeHelpers.get_screen_icon_direction("Unspecified")

            if OTLObjectHelper.is_directional_relation(relation_object):
                direction = RelationChangeHelpers.get_screen_icon_direction(
                    "Source -> Destination")

            list_of_corresponding_values.append({
                "text": Text(abbr_typeURI, screen_name_source, direction, screen_name_target,relation_object.typeURI),
                "data": Data(i,relation_object in last_added)
            })

        list_of_corresponding_values.sort(key=lambda val: (
            val['text'].typeURI if val['text'].typeURI is not None else "xxx",
            val['text'].name_source if val['text'].name_source is not None else "xxx",
            val['text'].name_target if val['text'].name_target is not None else "xxx"))

        return list_of_corresponding_values

    def is_last_added(self, text_and_data: dict):
        return text_and_data["data"].last_added

    def create_asset_type_standard_item(self, asset_type, text_and_data_list):
        folder_item = super().create_asset_type_standard_item(asset_type, text_and_data_list)

        if text_and_data_list:
            full_typeURI = text_and_data_list[0]["text"].full_typeURI
            self.add_colored_relation_bol_icon_to_item(folder_item, full_typeURI)
        return folder_item