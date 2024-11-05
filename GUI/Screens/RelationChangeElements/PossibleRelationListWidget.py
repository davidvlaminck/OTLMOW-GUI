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

    Text = namedtuple('text', ['relation_typeURI', 'direction', 'screen_name', 'target_typeURI'])
    Data = namedtuple('data', ['source_id', 'target_id', "index"])

    def fill_list(self, source_object: Optional[AIMObject], objects: Collection) -> None:
        # sourcery skip: remove-dict-keys
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

            item = self.create_asset_type_item(asset_type)
            item_list.append(item)
         
            self.type_to_items_dict[asset_type] = []
            self.type_open_status[asset_type] = False
            
            for text_and_data in text_and_data_list:
                instance_item = QListWidgetItem()

                text = f"   {text_and_data['text'].relation_typeURI} {text_and_data['text'].direction} {text_and_data['text'].screen_name} | {text_and_data['text'].target_typeURI}"
                instance_item.setText(text)
    
                # instance_item.setData(1,text_args['data'][0])
                # instance_item.setData(2, text_args['data'][1])
                instance_item.setData(self.data_1_index, text_and_data['data'].source_id)
                instance_item.setData(self.data_2_index, text_and_data['data'].target_id)
                instance_item.setData(self.data_3_index, text_and_data['data'].index)
                instance_item.setData(self.item_type_data_index, "instance")

                self.type_to_items_dict[asset_type].append(instance_item)

        item_list = self.filter_on_search_text(items=item_list)

        for item in item_list:
            self.list_gui.addItem(item)

    def extract_text_and_data_per_item(self, source_object, objects):
        list_of_corresponding_values = []
        for target_identificator, target_relations in objects.items():

            for i, relation in enumerate(target_relations):

                target_object: AIMObject = RelationChangeDomain.get_object(
                    relation.doelAssetId.identificator)

                direction = ""
                if is_directional_relation(relation):
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

    def object_selected_listener(self,item) -> None:
        """Check the selection state of possible relations and update the button accordingly.

        This function enables or disables the 'add possible relation to existing' button based on whether
        any items are selected in the possible relation list. If items are selected, the button is enabled;
        if no items are selected, the button is disabled.
        
        Args:
           self: The instance of the class.
        
        Returns:
           None
        """
        super().object_selected_listener(item)

        type_of_item = item.data(self.item_type_data_index)



        self.listButton.isEnabled()
        if len([item for item in self.list_gui.selectedItems()
                if item.data(self.item_type_data_index) == "instance"]):
            if not self.listButton.isEnabled():
                self.listButton.setEnabled(True)
        elif self.listButton.isEnabled():
            self.listButton.setEnabled(False)

        if type_of_item == "type":
            asset_type = item.data(self.data_1_index)
            self.type_open_status[asset_type] = not self.type_open_status[asset_type]
            indexSelectedItem = self.list_gui.indexFromItem(item).row()

            if self.type_open_status[asset_type]:
                for i,instance_item in enumerate(self.type_to_items_dict[asset_type]):
                    self.list_gui.insertItem(indexSelectedItem+i+1,instance_item)
            else:
                for instance_item in self.type_to_items_dict[asset_type]:
                    self.list_gui.takeItem(self.list_gui.indexFromItem(instance_item).row())
            if item.isSelected():
                item.setSelected(False)

        if type_of_item == "instance":
            self.possible_relations_selected()

    def create_button(self):
        self.listButton.setText(self._('add_relation'))
        self.listButton.setDisabled(True)
        self.listButton.clicked.connect(
            self.add_possible_relation_to_existing_relations_listener)
        self.listButton.setProperty('class', 'primary-button')
        return self.listButton

    def add_possible_relation_to_existing_relations_listener(self):
        Data = self.Data
        data_list: list[Data] = sorted([
            Data(item.data(self.data_1_index), item.data(self.data_2_index), item.data(self.data_3_index))
            for item in self.list_gui.selectedItems() if item.data(self.item_type_data_index) == "instance"],reverse=True)

        for data in data_list:
            RelationChangeDomain.add_possible_relation_to_existing_relations(data.source_id,
                                                                             data.target_id,
                                                                             data.index)

    def possible_relations_selected(self):
        Data =self.Data
        data_list: list[Data] = [
            self.Data(item.data(self.data_1_index), item.data(self.data_2_index), item.data(self.data_3_index))
            for item in self.list_gui.selectedItems() if item.data(self.item_type_data_index) == "instance"]

        RelationChangeDomain.select_possible_relation_keys(data_list)