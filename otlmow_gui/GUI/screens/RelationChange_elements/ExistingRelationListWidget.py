from collections import namedtuple

from PyQt6.QtCore import Qt, QItemSelectionModel
from PyQt6.QtGui import QStandardItem
from PyQt6.QtWidgets import QFrame
from otlmow_model.OtlmowModel.Helpers import OTLObjectHelper

from otlmow_gui.Domain.logger.OTLLogger import OTLLogger
from otlmow_gui.Domain.step_domain.RelationChangeDomain import RelationChangeDomain
from otlmow_gui.GUI.screens.RelationChange_elements.AbstractInstanceListWidget import \
    AbstractInstanceListWidget

from otlmow_gui.GUI.screens.RelationChange_elements.RelationChangeHelpers import RelationChangeHelpers
from otlmow_gui.exception_handler.ExceptionHandlers import create_task_reraise_exception


class ExistingRelationListWidget(AbstractInstanceListWidget):

    Text = namedtuple('text', ['typeURI', 'name_source', 'direction', 'name_target','full_typeURI'])
    Data = namedtuple('data', ["index", "last_added"])

    def __init__(self, language_settings,parent):
        self._ = language_settings
        labels = [self._("source_asset"),self._("target_asset")]
        super().__init__(language_settings=language_settings,parent=parent,labels=labels)

        self.list_label_text = self._("existing_relations_list")
        self.list_subtext_label_text = self._("existing_relations_description")
        self.attribute_field_label_text = self._("existing_relation_attributes")

    def create_object_list_gui(self, multi_select: bool = False) -> QFrame:
        frame = super().create_object_list_gui(multi_select)
        self.frame_layout.setContentsMargins(11, 0, 0, 0)
        return frame

    def on_item_selectionChange_listener(self, selected: QItemSelectionModel, deselected:QItemSelectionModel):
        no_item_selected = True

        for index in deselected.indexes():
            if index.column() == 0:
                item = self.list_gui.model.itemFromIndex(index)
                if item and item.isSelectable():
                    type_folder_item = item.parent()
                    self.reset_selected_item_count(type_folder_item=type_folder_item)

        dict_type_to_type_folder_item = {}
        dict_type_to_selected_item_count = {}
        # Get the currently selected indexes
        for index in self.list_gui.selectionModel().selectedIndexes():
            if index.column() == 0:
                item = self.list_gui.model.itemFromIndex(index)
                if item and item.isSelectable():
                    no_item_selected = False

                    # keep count of selected items in folder
                    parent_type_folder_item = item.parent()
                    parent_type_folder_type = parent_type_folder_item.data(self.data_1_index)
                    if parent_type_folder_type in dict_type_to_selected_item_count.keys():
                        dict_type_to_selected_item_count[parent_type_folder_type] += 1
                    else:
                        dict_type_to_selected_item_count[parent_type_folder_type] = 1
                        dict_type_to_type_folder_item[
                            parent_type_folder_type] = parent_type_folder_item

        # update the selected_counts on all type_folder_items
        for type_folder_type, selected_item_count in dict_type_to_selected_item_count.items():
            OTLLogger.logger.debug(f"{type_folder_type}: {selected_item_count}")

            type_folder_item = dict_type_to_type_folder_item[type_folder_type]

            item_count = self.update_selected_count_data(type_folder_item=type_folder_item,
                                                         selected_item_count=selected_item_count)

            # apply new information to the folder_item display text
            self.set_type_folder_text(type_folder_item=type_folder_item,
                                      otl_type=type_folder_type,
                                      item_count=item_count,
                                      selected_item_count=selected_item_count)

        self.existing_relations_selected()
        self.set_list_button_enabled(not no_item_selected)

    def set_list_button_enabled(self, item_selected:bool):
        if not item_selected:
            if self.list_button.isEnabled():
                self.list_button.setEnabled(False)
        elif not self.list_button.isEnabled():
            self.list_button.setEnabled(True)

    def create_button(self):
        self.list_button.setText(self._('remove_relation'))
        self.list_button.setDisabled(True)
        self.list_button.clicked.connect(
            self.remove_existing_relations_listener)
        self.list_button.setProperty('class', 'remove_relation-button')
        return self.list_button

    def create_instance_standard_item(self, text_and_data):
        text = f"{text_and_data['text'].name_source}"
        instance_item = QStandardItem(text)
        instance_item.setData(text_and_data["data"].index, self.data_1_index)
        instance_item.setData("instance", self.item_type_data_index)
        instance_item.setData(text_and_data["data"].last_added, self.data_last_added_index)

        instance_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)

        text2 = f"{text_and_data['text'].name_target}"
        instance_item2 = QStandardItem(text2)
        instance_item2.setTextAlignment(Qt.AlignmentFlag.AlignTop)
        # instance_item2.setData(text_and_data["data"].index, self.data_1_index)
        # instance_item2.setData("instance", self.item_type_data_index)

        self.add_direction_icon_to_item(instance_item=instance_item2,
                                        direction=text_and_data['text'].direction,
                                        typeURI= text_and_data['text'].full_typeURI)

        return instance_item, instance_item2

    def existing_relations_selected(self):
        indices: list[int] = self.get_selected_data()
        create_task_reraise_exception(
        RelationChangeDomain.select_existing_relation_indices(indices))

    def get_selected_data(self):
        return [
            self.list_gui.model.itemFromIndex(model_i).data(self.data_1_index)
            for model_i in self.list_gui.selectionModel().selectedIndexes() if model_i.column() == 0]

    def remove_existing_relations_listener(self):
        indices: list[int] = sorted(self.get_selected_data(), reverse=True)

        # for index in indices:
        #     RelationChangeDomain.remove_existing_relation(index)
        create_task_reraise_exception(RelationChangeDomain.remove_multiple_existing_relations(indices))


    def extract_text_and_data_per_item(self, source_object, objects, last_added):
        list_of_corresponding_values = []
        Text = self.Text
        Data = self.Data

        for i, relation_object in enumerate(objects):

            source_object = RelationChangeDomain.get_object(
                identificator=relation_object.bronAssetId.identificator)
            target_object = RelationChangeDomain.get_object(
                identificator=relation_object.doelAssetId.identificator)
            screen_name_source = RelationChangeHelpers.get_screen_name(otl_object=source_object)
            screen_name_target = RelationChangeHelpers.get_screen_name(otl_object=target_object)
            add_namespace = RelationChangeHelpers.is_unique_across_namespaces(
                typeURI=relation_object.typeURI,
                objects=RelationChangeDomain.shown_objects)
            abbr_typeURI = RelationChangeHelpers.get_abbreviated_typeURI(
                typeURI=relation_object.typeURI,
                add_namespace=add_namespace,
                is_relation=OTLObjectHelper.is_relation(relation_object))

            direction = RelationChangeHelpers.get_screen_icon_direction("Unspecified")

            if OTLObjectHelper.is_directional_relation(relation_object):
                direction = RelationChangeHelpers.get_screen_icon_direction(
                    "Source -> Destination")

            list_of_corresponding_values.append({
                "text": Text(abbr_typeURI, screen_name_source, direction, screen_name_target,relation_object.typeURI),
                "data": Data(i,relation_object in last_added)
            })

        list_of_corresponding_values.sort(key=lambda val: (
            val['text'].typeURI if val['text'].typeURI is not None else "xxx",
            val['text'].name_source if val['text'].name_source is not None else "xxx",
            val['text'].name_target if val['text'].name_target is not None else "xxx"))

        return list_of_corresponding_values

    def is_last_added(self, text_and_data: dict):
        return text_and_data["data"].last_added

    def create_asset_type_standard_item(self, asset_type, text_and_data_list):
        folder_item = super().create_asset_type_standard_item(asset_type, text_and_data_list)

        if text_and_data_list:
            full_typeURI = text_and_data_list[0]["text"].full_typeURI
            self.add_colored_relation_bol_icon_to_item(folder_item, full_typeURI)
        return folder_item

    def get_no_instance_selected_message(self):
        return self._("no_relation_selected")

    def update_this_gui_list_content(self):
        RelationChangeDomain.update_frontend_existing_relations()

