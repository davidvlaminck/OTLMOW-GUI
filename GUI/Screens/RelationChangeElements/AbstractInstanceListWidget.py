import abc
from typing import Optional, Collection

from PyQt6.QtCore import Qt, QModelIndex
from PyQt6.QtGui import QColor, QStandardItem
from PyQt6.QtWidgets import QTreeWidget, QFrame, QVBoxLayout, QLabel, QListWidget, QListWidgetItem, \
    QHeaderView, QTreeWidgetItem, QWidget, QHBoxLayout, QLineEdit, QPushButton, QTreeView
from otlmow_model.OtlmowModel.Helpers.OTLObjectHelper import is_relation

import qtawesome as qta
from Domain.RelationChangeDomain import RelationChangeDomain
from GUI.ButtonWidget import ButtonWidget
from GUI.Screens.RelationChangeElements.FolderTreeView import FolderTreeView
from GUI.Screens.RelationChangeElements.RelationChangeHelpers import RelationChangeHelpers
from UnitTests.TestClasses.Classes.ImplementatieElement.AIMObject import AIMObject

MULTI_SELECTION = QListWidget.SelectionMode.MultiSelection
class AbstractInstanceListWidget:

    def __init__(self,language_settings, class_list_label_key: str, attribute_field_label_key:str):
        self._ = language_settings
        self.search_text = ""

        self.search_bar = None
        self.clear_search_bar_button = None

        self.list_gui = None
        self.list_button = ButtonWidget()

        self.list_label_text = self._(class_list_label_key)
        self.attribute_field_label_text = self._(attribute_field_label_key)
        self.attribute_field: QTreeWidget = QTreeWidget()
        self.attribute_field.setSelectionMode(QTreeWidget.SelectionMode.NoSelection)

        self.type_to_items_dict = {}
        self.type_open_status = {}
        self.selected_object = None

        self.item_type_data_index = 3
        self.data_1_index = 4
        self.data_2_index = 5
        self.data_3_index = 6

    def create_object_list_gui(self, multi_select: bool = False) -> QFrame:
        frame = QFrame()
        frame_layout = QVBoxLayout()
        list_label = QLabel()
        list_label.setText(self.list_label_text)
        self.list_gui = FolderTreeView()
        self.list_gui.setProperty('class', 'list')
        self.list_gui.selectionModel().selectionChanged.connect(self.on_item_selected_listener)
        self.list_gui.expanded.connect(self.record_expanse_listener)
        self.list_gui.collapsed.connect(self.record_collapse_listener)
        self.list_gui.clicked.connect(self.clicked_item_listener)
        self.list_gui.setExpandsOnDoubleClick(False)
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

    def clicked_item_listener(self, model_index: QModelIndex):
        if self.list_gui.model.itemFromIndex(model_index).hasChildren():
            if self.list_gui.isExpanded(model_index):
                self.list_gui.collapse(model_index)
            else:
                self.list_gui.expand(model_index)

    def fill_list(self, source_object: Optional[AIMObject], objects: Collection) -> None:
        # sourcery skip: remove-dict-keys
        # objects = RelationChangeDomain.objects
        self.list_gui.setSortingEnabled(False)
        self.list_gui.clear()
        item_list = []
        type_to_instance_dict = {}

        text_and_data_per_element = self.extract_text_and_data_per_item(source_object, objects)

        for text_and_data in text_and_data_per_element:

            abbr_typeURI = text_and_data['text'].typeURI

            if abbr_typeURI in type_to_instance_dict.keys():
                type_to_instance_dict[abbr_typeURI].append(text_and_data)
            else:
                type_to_instance_dict[abbr_typeURI] = [text_and_data]

        folder_items_expanded = []
        previously_selected_item = None
        for asset_type, text_and_data_list in type_to_instance_dict.items():

            add_folder_based_on_search_text = False
            folder_item = self.create_asset_type_standard_item(asset_type)
            self.type_to_items_dict[asset_type] = []

            if asset_type not in self.type_open_status:
                self.type_open_status[asset_type] = False
            elif self.type_open_status[asset_type]:
                folder_items_expanded.append(folder_item)

            for text_and_data in text_and_data_list:

                instance_item = self.create_instance_standard_item(text_and_data)

                if (    self.search_text in instance_item.text().lower() or
                        self.search_text in folder_item.text().lower()):
                    if self.is_previously_selected_requirement(text_and_data):
                        previously_selected_item = instance_item

                    self.type_to_items_dict[asset_type].append(instance_item)
                    instance_item.setEditable(False)  # Make the item name non-editable

                    folder_item.appendRow(instance_item)
                    add_folder_based_on_search_text = True

                    if self.search_text:
                        #if you are searching then open all the folders that have the results
                        folder_items_expanded.append(folder_item)

            if add_folder_based_on_search_text:
                item_list.append(folder_item)


        for folder_item in item_list:
            folder_item.sortChildren(0,Qt.SortOrder.AscendingOrder)
            self.list_gui.addItem(folder_item)

        self.list_gui.setSortingEnabled(True)
        self.list_gui.sortByColumn(0, Qt.SortOrder.AscendingOrder)

        # expand previously expanded items
        for folder_item in folder_items_expanded:
            folder_item_index = self.list_gui.model.indexFromItem(folder_item)
            self.list_gui.expand(folder_item_index)

        # select previously selected item
        self.select_object_id(previously_selected_item=previously_selected_item)
        if not previously_selected_item:
            self.set_list_button_enabled( False)

    @abc.abstractmethod
    def create_instance_standard_item(self, text_and_data):
        raise NotImplementedError

    @abc.abstractmethod
    def create_button(self):
        raise NotImplementedError

    @abc.abstractmethod
    def extract_text_and_data_per_item(self, source_object, objects):
        raise NotImplementedError

    @abc.abstractmethod
    def on_item_selected_listener(self, selected, deselected):
        raise NotImplementedError

    def create_attribute_field(self):

        self.attribute_field.setColumnCount(2)
        self.attribute_field.setProperty('class', 'attribute_field')
        self.attribute_field.setHeaderHidden(True)

        header = self.attribute_field.header()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setStretchLastSection(False)

        return self.attribute_field

    def fill_object_attribute_field(self, object_attribute_dict:dict):
        self.fill_attribute_field(self.attribute_field, object_attribute_dict)

    def create_search_bar(self) -> QFrame:
        frame = QFrame()
        frame.setContentsMargins(0, 0, 0, 0)
        frame_layout = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText(self._('search'))
        self.search_bar.textChanged.connect(self.search_listener)

        self.clear_search_bar_button = QPushButton()
        self.clear_search_bar_button.setIcon(qta.icon('mdi.close'))
        self.clear_search_bar_button.clicked.connect(self.clear_search_listener)
        self.clear_search_bar_button.setProperty('class', 'secondary-button')

        frame_layout.addWidget(self.search_bar)
        frame_layout.addWidget(self.clear_search_bar_button)
        frame.setLayout(frame_layout)
        return frame

    def search_listener(self,text:str):
        self.search_text = text.lower()
        if not self.search_text:
            self.set_all_folder_items_collapsed()

        RelationChangeDomain.update_frontend()

    def clear_search_listener(self):
        self.search_bar.setText("")
        RelationChangeDomain.update_frontend()

    def filter_on_search_text(self, items:list[QListWidgetItem]) -> list[QListWidgetItem]:

        return   [item for item in items
                  if self.search_text in item.text().lower()]

    @classmethod
    def fill_attribute_field(cls, field, object_attribute_dict):
        field.clear()
        for attribute, value in object_attribute_dict.items():
            list_item = QTreeWidgetItem()
            list_item.setText(0, attribute)
            list_item.setText(1, str(value))
            field.addTopLevelItem(list_item)

    def create_asset_type_item(self, asset_type):
        item = QListWidgetItem()
        item.setText(f"{asset_type}")
        item.setData(self.data_1_index, asset_type)
        item.setData(self.item_type_data_index, "type")
        return item

    def create_asset_type_standard_item(self, asset_type):
        item = QStandardItem(f"{asset_type}")
        item.setEditable(False)  # Make the folder name non-editable
        item.setSelectable(False)  # Optional: make the folder itself non-selectable

        item.setData(asset_type,self.data_1_index)
        item.setData("type", self.item_type_data_index)
        return item

    def select_object_id(self, previously_selected_item: QStandardItem):
        pass

    def is_previously_selected_requirement(self, text_and_data):
        return False

    def record_expanse_listener(self, index):

        expanded_folder_item = self.list_gui.model.itemFromIndex(index)
        self.type_open_status[expanded_folder_item.text()] = True

    def record_collapse_listener(self, index):

        collapsed_folder_item = self.list_gui.model.itemFromIndex(index)
        self.type_open_status[collapsed_folder_item.text()] = False


    def expand_folder_of(self,typeURI: str):
        self.type_open_status[typeURI] = True

    def set_list_button_enabled(self, item_selected:bool):
        pass

    def set_all_folder_items_collapsed(self):
        self.type_open_status.clear()