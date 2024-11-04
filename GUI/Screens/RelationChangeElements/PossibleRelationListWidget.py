from collections import namedtuple
from typing import Optional, Collection

from PyQt6.QtWidgets import QFrame, QListWidget, QListWidgetItem
from otlmow_model.OtlmowModel.Helpers.OTLObjectHelper import is_directional_relation

from Domain.RelationChangeDomain import RelationChangeDomain
from GUI.Screens.RelationChangeElements.AbstractInstanceListWidget import \
    AbstractInstanceListWidget, MULTI_SELECTION
from GUI.Screens.RelationChangeElements.RelationChangeHelpers import RelationChangeHelpers
from UnitTests.TestClasses.Classes.ImplementatieElement.AIMObject import AIMObject


class PossibleRelationListWidget(AbstractInstanceListWidget):
    def __init__(self, language_settings):
        super().__init__(language_settings,'relations_list','possible_relation_attributes')

    def fill_list(self, source_object: Optional[AIMObject], objects: Collection) -> None:
        # sourcery skip: remove-dict-keys
        self.list_gui.clear()


        Text = namedtuple('text', ['source_typeURI', 'direction', 'screen_name', 'target_typeURI'])
        Data = namedtuple('data', ['source_id', 'target_id', "index"])
        
        list_of_corresponding_values = []
        for target_identificator, target_relations in objects.items():

            for i, relation in enumerate(target_relations):

                target_object: AIMObject = RelationChangeDomain.get_object(
                    relation.doelAssetId.identificator)

                direction = ""
                if is_directional_relation(relation):
                    if relation.bronAssetId.identificator == target_identificator:
                        direction = RelationChangeHelpers.get_screen_icon_direction("Destination -> Source")
                        target_object = RelationChangeDomain.get_object(
                            relation.bronAssetId.identificator)
                    else:
                        direction = RelationChangeHelpers.get_screen_icon_direction("Source -> Destination")

                else:
                    direction = RelationChangeHelpers.get_screen_icon_direction("Unspecified")

                screen_name = RelationChangeHelpers.get_screen_name(target_object)

                abbr_target_object_typeURI = RelationChangeHelpers.get_abbreviated_typeURI(
                    target_object)

                abbr_relation_typeURI = RelationChangeHelpers.get_abbreviated_typeURI(relation)

                list_of_corresponding_values.append({
                    "text": Text(abbr_relation_typeURI, direction, screen_name,
                                 abbr_target_object_typeURI),
                    "data": Data(source_object.assetId.identificator, target_identificator, i)
                })

        list_of_corresponding_values.sort(key=lambda val: (
        val['text'].target_typeURI, val['text'].screen_name, val['text'].source_typeURI))

        item_list = []
        for val in list_of_corresponding_values:
            item = QListWidgetItem()
            text = f"{val['text'].source_typeURI} {val['text'].direction} {val['text'].screen_name} | {val['text'].target_typeURI}"
            item.setText(text)

            # item.setData(1,text_args['data'][0])
            # item.setData(2, text_args['data'][1])
            item.setData(3, val['data'].source_id)
            item.setData(4, val['data'].target_id)
            item.setData(5, val['data'].index)

            item_list.append(item)

        item_list = self.filter_on_search_text(items=item_list)

        for item in item_list:
            self.list_gui.addItem(item)


    def object_selected_listener(self) -> None:
        """Check the selection state of possible relations and update the button accordingly.

        This function enables or disables the 'add possible relation to existing' button based on whether
        any items are selected in the possible relation list. If items are selected, the button is enabled;
        if no items are selected, the button is disabled.
        
        Args:
           self: The instance of the class.
        
        Returns:
           None
        """
        super().object_selected_listener()
        self.listButton.isEnabled()
        if len(list(self.list_gui.selectedItems())):
            if not self.listButton.isEnabled():
                self.listButton.setEnabled(True)
        elif self.listButton.isEnabled():
            self.listButton.setEnabled(False)

        self.possible_relations_selected()

    def create_button(self):
        self.listButton.setText(self._('add_relation'))
        self.listButton.setDisabled(True)
        self.listButton.clicked.connect(
            self.add_possible_relation_to_existing_relations_listener)
        self.listButton.setProperty('class', 'primary-button')
        return self.listButton

    def add_possible_relation_to_existing_relations_listener(self):
        Data = namedtuple('data', ['source_id', 'target_id', "index"])
        data_list: list[Data] = sorted([
            Data(item.data(3), item.data(4), item.data(5))
            for item in self.list_gui.selectedItems()],reverse=True)

        for data in data_list:
            RelationChangeDomain.add_possible_relation_to_existing_relations(data.source_id,
                                                                             data.target_id,
                                                                             data.index)

    def possible_relations_selected(self):
        Data = namedtuple('data', ['source_id', 'target_id', "index"])
        data_list: list[Data] = [
            Data(item.data(3), item.data(4), item.data(5))
            for item in self.list_gui.selectedItems()]

        RelationChangeDomain.select_possible_relation_keys(data_list)