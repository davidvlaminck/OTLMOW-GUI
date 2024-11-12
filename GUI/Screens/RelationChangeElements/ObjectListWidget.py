from collections import namedtuple

from PyQt6.QtCore import QItemSelectionModel
from PyQt6.QtGui import QStandardItem, QPixmap, QIcon
from PyQt6.QtWidgets import QFrame
from otlmow_model.OtlmowModel.Helpers import OTLObjectHelper

from Domain.RelationChangeDomain import RelationChangeDomain
from GUI.Screens.RelationChangeElements.AbstractInstanceListWidget import \
    AbstractInstanceListWidget, IMG_DIR

from GUI.Screens.RelationChangeElements.RelationChangeHelpers import RelationChangeHelpers


class ObjectListWidget(AbstractInstanceListWidget):
    Text = namedtuple('text', ['typeURI', 'screen_name', 'full_typeURI'])
    Data = namedtuple('data', ['selected_object_id'])

    def __init__(self, language_settings):
        super().__init__(language_settings,'class_list','object_attributes')

    def create_object_list_gui(self, multi_select: bool = False) -> QFrame:
        frame = super().create_object_list_gui(multi_select)
        self.frame_layout.setContentsMargins(11,11,0,11)
        self.list_gui.setProperty('class', 'object-list')
        return frame

    def on_item_selected_listener(self, selected, deselected):
        # Get the currently selected indexes
        self.selected_object = None
        for index in self.list_gui.selectionModel().selectedIndexes():
            if index.column() == 0:
                item = self.list_gui.model.itemFromIndex(index)
                if item and item.isSelectable():
                    selected_object_id = item.data(self.data_1_index)
                    self.selected_object = RelationChangeDomain.get_object(identificator=
                                                                       selected_object_id)

        RelationChangeDomain.set_possible_relations(selected_object=self.selected_object)

    def create_button(self):
        self.list_button.setEnabled(False)
        self.list_button.setText("hidden")
        self.list_button.setProperty("class", "invisible")
        return self.list_button

    def is_previously_selected_requirement(self, text_and_data):
        return self.selected_object and self.selected_object.assetId.identificator == text_and_data['data'].selected_object_id

    def extract_text_and_data_per_item(self, source_object, objects):
        list_of_corresponding_values = []

        for OTL_object in objects:
            screen_name = RelationChangeHelpers.get_screen_name(OTL_object)
            abbr_typeURI = RelationChangeHelpers.get_abbreviated_typeURI(OTL_object.typeURI,OTLObjectHelper.is_relation(OTL_object))

            list_of_corresponding_values.append({
                "text": self.Text(abbr_typeURI,screen_name,OTL_object.typeURI),
                "data": self.Data(OTL_object.assetId.identificator)
            })
        return list_of_corresponding_values
    def create_instance_standard_item(self, text_and_data):
        text = f"{text_and_data['text'].screen_name}"
        instance_item = QStandardItem(text)
        instance_item.setData(text_and_data['data'].selected_object_id, self.data_1_index)
        instance_item.setData("instance", self.item_type_data_index)

        return instance_item,

    def select_object_id(self, previously_selected_item: QStandardItem):
        if previously_selected_item:
            previously_selected_item_index = self.list_gui.model.indexFromItem(
                previously_selected_item)
            if previously_selected_item_index:
                self.list_gui.selectionModel().setCurrentIndex(previously_selected_item_index,
                                                               QItemSelectionModel.SelectionFlag.SelectCurrent)