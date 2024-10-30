from typing import Optional, Collection

from PyQt6.QtWidgets import QFrame, QListWidgetItem

from Domain.InsertDataDomain import InsertDataDomain
from Domain.RelationChangeDomain import RelationChangeDomain
from GUI.Screens.RelationChangeElements.AbstractInstanceListWidget import \
    AbstractInstanceListWidget
from GUI.Screens.RelationChangeElements.RelationChangeHelpers import RelationChangeHelpers
from UnitTests.TestClasses.Classes.ImplementatieElement.AIMObject import AIMObject


class ObjectListWidget(AbstractInstanceListWidget):
    def __init__(self, language_settings):
        super().__init__(language_settings,'class_list','object_attributes')

    def fill_list(self, source_object: Optional[AIMObject], objects: Collection) -> None:
        # objects = RelationChangeDomain.objects

        self.object_list_gui.clear()
        item_list = []
        for OTL_object in objects:
            item = QListWidgetItem()
            item.setData(1, OTL_object.assetId.identificator)
            # item.clicked.connect(self.object_selected)

            screen_name = RelationChangeHelpers.get_screen_name(OTL_object)

            abbr_typeURI = RelationChangeHelpers.get_abbreviated_typeURI(OTL_object)

            item.setText(f"{screen_name} | {abbr_typeURI}")
            item_list.append(item)

        item_list = self.filter_on_search_text(items=item_list)

        for item in item_list:
            self.object_list_gui.addItem(item)


    def object_selected_listener(self) -> None:
        super().object_selected_listener()
        for i in range(self.object_list_gui.count()):
            if self.object_list_gui.item(i).isSelected():
                selected_object_id = self.object_list_gui.item(i).data(1)
                self.selected_object_col1 = RelationChangeDomain.get_object(
                    identificator=selected_object_id)
                if self.selected_object_col1 is not None:
                    RelationChangeDomain.set_possible_relations(
                        selected_object=self.selected_object_col1)

                break

    def create_button(self):
        self.listButton.setEnabled(False)
        self.listButton.setText("hidden")
        self.listButton.setProperty("class", "invisible")
        return self.listButton

    def select_object_id(self, selected_object_id: str):
        selected_item: list[QListWidgetItem] = [self.object_list_gui.item(i)  for i in range(self.object_list_gui.count()) if selected_object_id==self.object_list_gui.item(i).data(1)]
        if selected_item:
            selected_item[0].setSelected(True)