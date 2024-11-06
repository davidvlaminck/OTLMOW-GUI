from typing import Optional, Collection

from PyQt6.QtGui import QStandardItem
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QTreeView

from Domain.RelationChangeDomain import RelationChangeDomain
from GUI.Screens.RelationChangeElements.AbstractInstanceListWidget import \
    AbstractInstanceListWidget
from GUI.Screens.RelationChangeElements.FolderTreeView import FolderTreeView
from GUI.Screens.RelationChangeElements.RelationChangeHelpers import RelationChangeHelpers
from UnitTests.TestClasses.Classes.ImplementatieElement.AIMObject import AIMObject


class NewObjectListWidget(AbstractInstanceListWidget):

    def __init__(self, language_settings):
        super().__init__(language_settings,'class_list','object_attributes')
        self.selected_object = None

    def object_selected_listener(self, item) -> None:
      pass

    def on_item_selected(self, selected, deselected):
        # Get the currently selected indexes
        for index in selected.indexes():
            item = self.list_gui.model.itemFromIndex(index)
            if item and item.isSelectable():
                selected_object_id = item.data(self.data_1_index)
                self.selected_object = RelationChangeDomain.get_object(identificator=
                                                                       selected_object_id)
                if self.selected_object is not None:
                    RelationChangeDomain.set_possible_relations(selected_object=
                                                                self.selected_object)
    def create_button(self):
        self.list_button.setEnabled(False)
        self.list_button.setText("hidden")
        self.list_button.setProperty("class", "invisible")
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
        item_list = []
        type_to_instance_dict = {}

        for OTL_object in objects:

            abbr_typeURI = RelationChangeHelpers.get_abbreviated_typeURI(OTL_object)

            if abbr_typeURI in type_to_instance_dict.keys():
                type_to_instance_dict[abbr_typeURI].append(OTL_object)
            else:
                type_to_instance_dict[abbr_typeURI] = [OTL_object]

        for asset_type, objects in type_to_instance_dict.items():
            folder_item = self.create_asset_type_standard_item(asset_type)

            item_list.append(folder_item)

            self.type_to_items_dict[asset_type] = []
            self.type_open_status[asset_type] = False
            for OTL_object in objects:

                screen_name = RelationChangeHelpers.get_screen_name(OTL_object)
                instance_item = QStandardItem(f"     {screen_name}")

                instance_item.setData(OTL_object.assetId.identificator, self.data_1_index)
                instance_item.setData("instance",self.item_type_data_index)

                self.type_to_items_dict[asset_type].append(instance_item)

                instance_item.setEditable(False)  # Make the item name non-editable
                folder_item.appendRow(instance_item)

        # TODO: search is only on the top-level item now (folder name)
        item_list = self.filter_on_search_text(items=item_list)

        for folder_item in item_list:
            self.list_gui.addItem(folder_item)

    def select_object_id(self, selected_object_id: str):
        indexes = self.list_gui.selectionModel().selectedIndexes()
        if indexes:
            index = indexes[0]
            selected_item = self.list_gui.model.itemFromIndex(index)
            if selected_item and selected_item.isSelectable():
                selected_item[0].setSelected(True)