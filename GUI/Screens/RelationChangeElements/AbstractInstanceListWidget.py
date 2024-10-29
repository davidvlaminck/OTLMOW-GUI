import abc
from typing import Optional, Collection

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QTreeWidget, QFrame, QVBoxLayout, QLabel, QListWidget, QListWidgetItem, \
    QHeaderView, QTreeWidgetItem, QWidget, QHBoxLayout, QLineEdit, QPushButton
from otlmow_model.OtlmowModel.Helpers.OTLObjectHelper import is_relation

import qtawesome as qta
from Domain.RelationChangeDomain import RelationChangeDomain
from GUI.ButtonWidget import ButtonWidget
from GUI.Screens.RelationChangeElements.RelationChangeHelpers import RelationChangeHelpers
from UnitTests.TestClasses.Classes.ImplementatieElement.AIMObject import AIMObject

MULTI_SELECTION = QListWidget.SelectionMode.MultiSelection
class AbstractInstanceListWidget:

    def __init__(self,language_settings, class_list_label_key: str, attribute_field_label_key:str):
        self._ = language_settings
        self.search_text = ""

        self.search_bar = None
        self.clear_search_bar_button = None

        self.object_list_gui = None
        self.listButton = ButtonWidget()

        self.list_label_text = self._(class_list_label_key)
        self.attribute_field_label_text = self._(attribute_field_label_key)
        self.attribute_field: QTreeWidget = QTreeWidget()

    def create_object_list_gui(self,multi_select: bool = False) -> QFrame:
        frame = QFrame()
        frame_layout = QVBoxLayout()
        list_label = QLabel()
        list_label.setText(self.list_label_text)
        self.object_list_gui = QListWidget()
        self.object_list_gui.setProperty('class', 'list')
        self.object_list_gui.itemSelectionChanged.connect(self.object_selected_listener)
        if multi_select:
            self.object_list_gui.setSelectionMode(QListWidget.SelectionMode.MultiSelection)

        frame_layout.addWidget(list_label)
        frame_layout.addWidget(self.create_search_bar())
        frame_layout.addWidget(self.object_list_gui)

        object_attribute_label = QLabel()
        object_attribute_label.setText(self.attribute_field_label_text)
        frame_layout.addWidget(self.create_button())
        frame_layout.addWidget(object_attribute_label)

        frame_layout.addWidget(self.create_attribute_field())
        frame.setLayout(frame_layout)

        return frame

    @abc.abstractmethod
    def fill_list(self, source_object: Optional[AIMObject], objects: Collection) -> None:
        raise NotImplementedError


    def object_selected_listener(self) -> None:
        for item_index in range(self.object_list_gui.count()):
            list_item: QListWidgetItem = self.object_list_gui.item(item_index)
            if list_item.isSelected():
                # Change style for selected item
                # list_item.setData(Qt.ItemDataRole.UserRole, QColor(0, 0, 255))  # Change to blue
                list_item.setBackground(QColor(0, 0, 255))
                list_item.setForeground(QColor(255, 255, 255))  # Change text color to white
            else:
                # Reset style for unselected items
                # list_item.setData(Qt.ItemDataRole.UserRole, )  # Change back to white
                list_item.setBackground(QColor(255, 255, 255))
                list_item.setForeground(QColor(0, 0, 0))  # Change text color to black

    @abc.abstractmethod
    def create_button(self):
        raise NotImplementedError

    def create_attribute_field(self):

        self.attribute_field.setColumnCount(2)
        self.attribute_field.setProperty('class', 'list')
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
        self.search_bar.textChanged.connect(self.search)

        self.clear_search_bar_button = QPushButton()
        self.clear_search_bar_button.setIcon(qta.icon('mdi.close'))
        self.clear_search_bar_button.clicked.connect(self.clear_search)
        self.clear_search_bar_button.setProperty('class', 'secondary-button')

        frame_layout.addWidget(self.search_bar)
        frame_layout.addWidget(self.clear_search_bar_button)
        frame.setLayout(frame_layout)
        return frame

    def search(self,text:str):
        self.search_text = text.lower()
        RelationChangeDomain.update_frontend()

    def clear_search(self):
        self.search_bar.setText("")
        RelationChangeDomain.update_frontend()

    def filter_on_search_text(self, items:list[QListWidgetItem]) -> list[QListWidgetItem]:
        return  list(filter(lambda item: self.search_text in item.text().lower(),items))

    @classmethod
    def fill_attribute_field(cls, field, object_attribute_dict):
        field.clear()
        for attribute, value in object_attribute_dict.items():
            list_item = QTreeWidgetItem()
            list_item.setText(0, attribute)
            list_item.setText(1, str(value))
            field.addTopLevelItem(list_item)

