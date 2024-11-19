from collections import namedtuple
from typing import Optional, Collection

from PyQt6.QtGui import QStandardItem, QPixmap, QIcon, QFont
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QTreeView
from otlmow_model.OtlmowModel.Helpers import OTLObjectHelper

from Domain.RelationChangeDomain import RelationChangeDomain
from GUI.Screens.RelationChangeElements.AbstractInstanceListWidget import \
    AbstractInstanceListWidget, IMG_DIR
from GUI.Screens.RelationChangeElements.FolderTreeView import FolderTreeView
from GUI.Screens.RelationChangeElements.RelationChangeHelpers import RelationChangeHelpers
from UnitTests.TestClasses.Classes.ImplementatieElement.AIMObject import AIMObject


class PossibleRelationListWidget(AbstractInstanceListWidget):

    Text = namedtuple('text', ['typeURI', 'direction', 'screen_name', 'target_typeURI','full_typeURI'])
    Data = namedtuple('data', ['source_id', 'target_id', "index", "last_added"])

    def __init__(self, language_settings):
        super().__init__(language_settings=language_settings,needs_source_object=True)

        self.list_label_text = self._('relations_list')
        self.list_subtext_label_text = self._("possible_relation_subscription")
        self.attribute_field_label_text = self._("possible_relation_attributes")

    def create_object_list_gui(self, multi_select: bool = False) -> QFrame:
        frame = super().create_object_list_gui(multi_select)
        self.frame_layout.setContentsMargins(0,11,11,11)
        self.list_gui.setProperty('class', 'possible-relation-list')

        self.add_no_asset_selected_placeholder()

        return frame

    def add_no_asset_selected_placeholder(self):
        place_holder_item = QStandardItem(
            self._("Select_an_OTL-asset_to_see_possible_relations"))
        place_holder_item.setEditable(False)
        place_holder_item.setEnabled(False)
        place_holder_item.setSelectable(False)

        placeholder_font = QFont()
        placeholder_font.setItalic(True)
        place_holder_item.setFont(placeholder_font)

        padding_item = QStandardItem("")
        padding_item.setEditable(False)
        padding_item.setEnabled(False)
        padding_item.setSelectable(False)

        self.list_gui.addItem([place_holder_item,padding_item ])

    def create_attribute_field(self):
        attribute_field = super().create_attribute_field()
        attribute_field.setProperty("class","attribute_field_possible_relation")
        return attribute_field

    def object_selected_listener(self, item) -> None:
        pass

    def on_item_selected_listener(self, selected, deselected):
        no_item_selected = True
        # Get the currently selected indexes
        for index in self.list_gui.selectionModel().selectedIndexes():
            if index.column() == 0:
                item = self.list_gui.model.itemFromIndex(index)
                if item and item.isSelectable():
                    no_item_selected = False

        self.possible_relations_selected()

        self.set_list_button_enabled(not no_item_selected)

    def set_list_button_enabled(self, item_selected:bool):
        if not item_selected:
            if self.list_button.isEnabled():
                self.list_button.setEnabled(False)
        elif not self.list_button.isEnabled():
            self.list_button.setEnabled(True)

    def create_button(self):
        self.list_button.setText(self._('add_relation'))
        self.list_button.setDisabled(True)
        self.list_button.clicked.connect(
            self.add_possible_relation_to_existing_relations_listener)
        self.list_button.setProperty('class', 'add_relation-button')
        return self.list_button

    def create_instance_standard_item(self, text_and_data):
        text = f"{text_and_data['text'].screen_name}"
        instance_item = QStandardItem(f"{text}")
        instance_item.setData([text_and_data['data'].source_id,text_and_data['data'].target_id,text_and_data['data'].index], self.data_1_index)
        # instance_item.setData(text_and_data['data'].source_id, self.data_1_index)
        # instance_item.setData(text_and_data['data'].target_id, self.data_2_index)
        # instance_item.setData(text_and_data['data'].index, self.data_3_index)
        instance_item.setData("instance", self.item_type_data_index)
        instance_item.setData(text_and_data["data"].last_added, self.data_last_added_index)

        text2 = f"{text_and_data['text'].target_typeURI}"
        instance_item2 = QStandardItem(text2)

        pixmap = QPixmap(f'{str(IMG_DIR)}/bar_pipe.png')
        instance_item2.setIcon(QIcon(pixmap))

        self.add_direction_icon_to_item(instance_item=instance_item,
                                        direction=text_and_data['text'].direction,
                                        typeURI=text_and_data['text'].full_typeURI)

        return instance_item,instance_item2



    def add_possible_relation_to_existing_relations_listener(self):
        Data = self.Data
        data_list: list[Data] = sorted(self.get_selected_data(), reverse=True)

        RelationChangeDomain.add_possible_relations_to_existing_relations(data_list=data_list)

        # for data in data_list:
        #     RelationChangeDomain.add_possible_relation_to_existing_relations(data.source_id,
        #                                                                      data.target_id,
        #                                                                      data.index)

    def possible_relations_selected(self):
        Data = self.Data
        data_list: list[Data] = self.get_selected_data()

        RelationChangeDomain.select_possible_relation_data(data_list)

    def get_selected_data(self):
        return [
            self.Data(self.list_gui.model.itemFromIndex(model_i).data(self.data_1_index)[0],
                      self.list_gui.model.itemFromIndex(model_i).data(self.data_1_index)[1],
                      self.list_gui.model.itemFromIndex(model_i).data(self.data_1_index)[2], False)
            # self.Data(self.list_gui.model.itemFromIndex(model_i).data(self.data_1_index),
            #           self.list_gui.model.itemFromIndex(model_i).data(self.data_2_index),
            #           self.list_gui.model.itemFromIndex(model_i).data(self.data_3_index),False)
            for model_i in self.list_gui.selectionModel().selectedIndexes()
            if model_i.column() == 0]

    def extract_text_and_data_per_item(self, source_object, objects, last_added):
        list_of_corresponding_values = []
        for target_identificator, target_relations in objects.items():

            for i, relation in enumerate(target_relations):

                target_object: AIMObject = RelationChangeDomain.get_object(
                    relation.doelAssetId.identificator)

                # if the target of the relation is the current selected object then you should
                # display the source object of the relation
                if target_object == source_object:
                    target_object =  RelationChangeDomain.get_object(
                    relation.bronAssetId.identificator)

                #  if the new target_object is still the same as the source_object something is wrong
                if target_object == source_object:
                    raise ValueError()


                direction = ""
                if OTLObjectHelper.is_directional_relation(relation):
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
                    target_object.typeURI, OTLObjectHelper.is_relation(target_object))

                abbr_relation_typeURI = RelationChangeHelpers.get_abbreviated_typeURI(
                    relation.typeURI,OTLObjectHelper.is_relation(relation))

                list_of_corresponding_values.append({
                    "text": self.Text(abbr_relation_typeURI, direction, screen_name,
                                      abbr_target_object_typeURI,relation.typeURI),
                    "data": self.Data(source_object.assetId.identificator, target_identificator, i,relation in last_added)
                })
        list_of_corresponding_values.sort(key=lambda val: (
            val['text'].target_typeURI, val['text'].screen_name, val['text'].typeURI))
        return list_of_corresponding_values

    def is_last_added(self, text_and_data: dict):
        return text_and_data["data"].last_added

    def create_asset_type_standard_item(self, asset_type, text_and_data_list):
        folder_item = super().create_asset_type_standard_item(asset_type,text_and_data_list)

        if text_and_data_list:
            full_typeURI = text_and_data_list[0]["text"].full_typeURI
            self.add_colored_relation_bol_icon_to_item(folder_item, full_typeURI)
        return folder_item
