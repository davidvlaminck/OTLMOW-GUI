from collections import namedtuple
from typing import Optional, Collection

from PyQt6.QtWidgets import QFrame, QListWidgetItem, QListWidget
from otlmow_model.OtlmowModel.Helpers.OTLObjectHelper import is_directional_relation

from Domain.RelationChangeDomain import RelationChangeDomain
from GUI.Screens.RelationChangeElements.AbstractInstanceListWidget import \
    AbstractInstanceListWidget
from GUI.Screens.RelationChangeElements.RelationChangeHelpers import RelationChangeHelpers
from UnitTests.TestClasses.Classes.ImplementatieElement.AIMObject import AIMObject


class ExistingRelationListWidget(AbstractInstanceListWidget):
    def __init__(self, language_settings):
        super().__init__(language_settings,'existing_relations_list','existing_relation_attributes')

    def fill_list(self, source_object: Optional[AIMObject], objects: Collection) -> None:
        self.list_gui.clear()

        Text = namedtuple('text', ['relation_typeURI', 'name_source', 'direction', 'name_target'])
        Data = namedtuple('data', ["index"])

        list_of_corresponding_values = []
        for i, relation_object in enumerate(objects):

            source_object = RelationChangeDomain.get_object(
                relation_object.bronAssetId.identificator)
            target_object = RelationChangeDomain.get_object(
                relation_object.doelAssetId.identificator)
            screen_name_source = RelationChangeHelpers.get_screen_name(OTL_object=source_object)
            screen_name_target = RelationChangeHelpers.get_screen_name(target_object)

            abbr_typeURI = RelationChangeHelpers.get_abbreviated_typeURI(relation_object)

            direction = RelationChangeHelpers.get_screen_icon_direction("Unspecified")

            if is_directional_relation(relation_object):
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


        item_list = []
        for val in list_of_corresponding_values:
            item = QListWidgetItem()
            item.setText(f"{val['text'].relation_typeURI} | {val['text'].name_source} {val['text'].direction} {val['text'].name_target}")
            item.setData(3, val["data"].index)
            item_list.append(item)

        item_list = self.filter_on_search_text(items=item_list)

        for item in item_list:
            self.list_gui.addItem(item)

    def object_selected_listener(self) -> None:
        super().object_selected_listener()
        self.listButton.isEnabled()
        if len(list(self.list_gui.selectedItems())):
            if not self.listButton.isEnabled():
                self.listButton.setEnabled(True)
        elif self.listButton.isEnabled():
            self.listButton.setEnabled(False)

        self.existing_relations_selected()

    def create_button(self):
        self.listButton.setText(self._('remove_relation'))
        self.listButton.setDisabled(True)
        self.listButton.clicked.connect(
            self.remove_existing_relations_listener)
        self.listButton.setProperty('class', 'primary-button')
        return self.listButton

    def existing_relations_selected(self):
        indices: list[int] = [
            item.data(3)
            for item in self.list_gui.selectedItems()]

        RelationChangeDomain.select_existing_relation_indices(indices)

    def remove_existing_relations_listener(self):
        indices: list[int] = sorted([
            item.data(3)
            for item in self.list_gui.selectedItems()],reverse=True)

        for index in indices:
            RelationChangeDomain.remove_existing_relation(index)