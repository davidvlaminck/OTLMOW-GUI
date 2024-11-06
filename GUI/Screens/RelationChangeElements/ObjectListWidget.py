from typing import Optional, Collection

from PyQt6.QtWidgets import QFrame, QListWidgetItem

from Domain.RelationChangeDomain import RelationChangeDomain
from GUI.Screens.RelationChangeElements.AbstractInstanceListWidget import \
    AbstractInstanceListWidget
from GUI.Screens.RelationChangeElements.RelationChangeHelpers import RelationChangeHelpers
from UnitTests.TestClasses.Classes.ImplementatieElement.AIMObject import AIMObject


class ObjectListWidget(AbstractInstanceListWidget):

    def __init__(self, language_settings):
        super().__init__(language_settings,'class_list','object_attributes')

    def fill_list(self, source_object: Optional[AIMObject], objects: Collection) -> None:
        # sourcery skip: remove-dict-keys
        # objects = RelationChangeDomain.objects

        self.list_gui.clear()
        item_list = []
        type_to_instance_dict = {}

        for OTL_object in objects:

            abbr_typeURI = RelationChangeHelpers.get_abbreviated_typeURI(OTL_object)

            if abbr_typeURI in type_to_instance_dict.keys():
                type_to_instance_dict[abbr_typeURI].append(OTL_object)
            else:
                type_to_instance_dict[abbr_typeURI] = [OTL_object]

        for asset_type, objects in type_to_instance_dict.items():
            item = self.create_asset_type_item(asset_type)

            item_list.append(item)

            self.type_to_items_dict[asset_type] = []
            self.type_open_status[asset_type] = False
            for OTL_object in objects:
                item = QListWidgetItem()
                screen_name = RelationChangeHelpers.get_screen_name(OTL_object)

                item.setText(f"{screen_name}")

                item.setData(self.data_1_index, OTL_object.assetId.identificator)
                item.setData(self.item_type_data_index, "instance")

                self.type_to_items_dict[asset_type].append(item)

        item_list = self.filter_on_search_text(items=item_list)

        for item in item_list:
            self.list_gui.addItem(item)



    def object_selected_listener(self,item) -> None:
        super().object_selected_listener(item)

        type_of_item = item.data(self.item_type_data_index)
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

        if type_of_item == "instance":
            selected_object_id = item.data(self.data_1_index)
            self.selected_object_col1 = RelationChangeDomain.get_object(
                identificator=selected_object_id)
            if self.selected_object_col1 is not None:
                RelationChangeDomain.set_possible_relations(
                    selected_object=self.selected_object_col1)

    def create_button(self):
        self.list_button.setEnabled(False)
        self.list_button.setText("hidden")
        self.list_button.setProperty("class", "invisible")
        return self.list_button

    def select_object_id(self, selected_object_id: str):
        selected_item: list[QListWidgetItem] = [self.list_gui.item(i) for i in range(self.list_gui.count()) if selected_object_id == self.list_gui.item(i).data(self.data_1_index)]
        if selected_item:
            selected_item[0].setSelected(True)