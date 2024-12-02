from collections import namedtuple

from PyQt6.QtCore import QItemSelectionModel
from PyQt6.QtGui import QStandardItem, QPixmap, QIcon, QFont
from PyQt6.QtWidgets import QFrame
from otlmow_model.OtlmowModel.Classes.ImplementatieElement.AIMObject import AIMObject
from otlmow_model.OtlmowModel.Helpers import OTLObjectHelper

from Domain.RelationChangeDomain import RelationChangeDomain
from GUI.DialogWindows.AddExternalAssetWindow import AddExternalAssetWindow
from GUI.Screens.RelationChangeElements.AbstractInstanceListWidget import \
    AbstractInstanceListWidget, IMG_DIR

from GUI.Screens.RelationChangeElements.RelationChangeHelpers import RelationChangeHelpers


class ObjectListWidget(AbstractInstanceListWidget):
    Text = namedtuple('text', ['typeURI', 'screen_name', 'full_typeURI'])
    Data = namedtuple('data', ['selected_object_id','last_added'])

    def __init__(self, language_settings,parent):
        labels = [ language_settings("OTL_asset")]
        super().__init__(language_settings=language_settings,parent=parent,labels=labels)

        self.list_label_text = self._('class_list')
        self.list_subtext_label_text = self._("otl_asset_description")
        self.attribute_field_label_text = self._("object_attributes")

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
        self.list_button.setEnabled(True)
        self.list_button.setText(self._("add_external_asset"))
        self.list_button.clicked.connect(
            self.add_external_asset)
        self.list_button.setProperty("class", "primary-button")
        return self.list_button

    def add_external_asset(self):
        add_asset_window = AddExternalAssetWindow(self._)
        add_asset_window.draw_add_external_asset_window()

    def is_previously_selected_requirement(self, text_and_data):
        return self.selected_object and RelationChangeHelpers.get_correct_identificator(self.selected_object) == text_and_data['data'].selected_object_id

    def extract_text_and_data_per_item(self, source_object, objects, last_added):
        list_of_corresponding_values = []

        for OTL_object in objects:
            screen_name = RelationChangeHelpers.get_screen_name(OTL_object)
            add_namespace = RelationChangeHelpers.is_unique_across_namespaces(
                OTL_object.typeURI,
                RelationChangeDomain.shown_objects)
            abbr_typeURI = RelationChangeHelpers.get_abbreviated_typeURI(
                OTL_object.typeURI,
                add_namespace,
                OTLObjectHelper.is_relation(OTL_object))

            list_of_corresponding_values.append({
                "text": self.Text(abbr_typeURI,screen_name,OTL_object.typeURI),
                "data": self.Data(RelationChangeHelpers.get_correct_identificator(OTL_object),False)
            })
        return list_of_corresponding_values
    def create_instance_standard_item(self, text_and_data):
        text = f"{text_and_data['text'].screen_name}"
        instance_item = QStandardItem(text)
        instance_item.setData(text_and_data['data'].selected_object_id, self.data_1_index)
        instance_item.setData("instance", self.item_type_data_index)
        instance_item.setData(text_and_data["data"].last_added, self.data_last_added_index)

        return instance_item,

    def select_object_id(self, previously_selected_item: QStandardItem):
        if previously_selected_item:
            previously_selected_item_index = self.list_gui.model.indexFromItem(
                previously_selected_item)
            if previously_selected_item_index:
                self.list_gui.selectionModel().setCurrentIndex(previously_selected_item_index,
                                                               QItemSelectionModel.SelectionFlag.SelectCurrent)

    def is_last_added(self, text_and_data: dict):
        pass

    def add_no_options_placeholder(self):
        place_holder_item = QStandardItem(
            self._("no_options_available"))
        place_holder_item.setEditable(False)
        place_holder_item.setEnabled(False)
        place_holder_item.setSelectable(False)

        placeholder_font = QFont()
        placeholder_font.setItalic(True)
        place_holder_item.setFont(placeholder_font)

        self.list_gui.addItem(place_holder_item)