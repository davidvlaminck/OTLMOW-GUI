from collections import namedtuple
from typing import Optional, Collection

from PyQt6.QtGui import QStandardItem
from otlmow_model.OtlmowModel.Helpers import OTLObjectHelper

from Domain.RelationChangeDomain import RelationChangeDomain
from GUI.Screens.RelationChangeElements.AbstractInstanceListWidget import \
    AbstractInstanceListWidget

from GUI.Screens.RelationChangeElements.RelationChangeHelpers import RelationChangeHelpers


class ExistingRelationListWidget(AbstractInstanceListWidget):

    Text = namedtuple('text', ['typeURI', 'name_source', 'direction', 'name_target'])
    Data = namedtuple('data', ["index"])

    def __init__(self, language_settings):
        super().__init__(language_settings, 'existing_relations_list',
                         'existing_relation_attributes')

    def on_item_selected_listener(self, selected, deselected):
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

    def create_instance_standard_item(self, text_and_data):
        text = f"{text_and_data['text'].typeURI} | {text_and_data['text'].name_source} {text_and_data['text'].direction} {text_and_data['text'].name_target}"
        instance_item = QStandardItem(f"{text}")
        instance_item.setData(text_and_data["data"].index, self.data_1_index)
        instance_item.setData("instance", self.item_type_data_index)
        return instance_item

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

            abbr_typeURI = RelationChangeHelpers.get_abbreviated_typeURI(relation_object.typeURI,OTLObjectHelper.is_relation(relation_object))

            direction = RelationChangeHelpers.get_screen_icon_direction("Unspecified")

            if OTLObjectHelper.is_directional_relation(relation_object):
                direction = RelationChangeHelpers.get_screen_icon_direction(
                    "Source -> Destination")

            list_of_corresponding_values.append({
                "text": Text(abbr_typeURI, screen_name_source, direction, screen_name_target),
                "data": Data(i)
            })

        list_of_corresponding_values.sort(key=lambda val: (
            val['text'].typeURI if val['text'].typeURI is not None else "xxx",
            val['text'].name_source if val['text'].name_source is not None else "xxx",
            val['text'].name_target if val['text'].name_target is not None else "xxx"))

        return list_of_corresponding_values