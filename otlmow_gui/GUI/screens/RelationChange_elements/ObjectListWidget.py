from collections import namedtuple

from PyQt6.QtCore import QItemSelectionModel
from PyQt6.QtGui import QStandardItem, QFont
from PyQt6.QtWidgets import QFrame
from otlmow_model.OtlmowModel.Helpers import OTLObjectHelper

from otlmow_gui.Domain.step_domain.RelationChangeDomain import RelationChangeDomain
from otlmow_gui.GUI.dialog_windows.AddExternalAssetWindow import AddExternalAssetWindow
from otlmow_gui.GUI.screens.RelationChange_elements.AbstractInstanceListWidget import \
    AbstractInstanceListWidget

from otlmow_gui.GUI.screens.RelationChange_elements.RelationChangeHelpers import RelationChangeHelpers
from otlmow_gui.exception_handler.ExceptionHandlers import create_task_reraise_exception


class ObjectListWidget(AbstractInstanceListWidget):
    Text = namedtuple('text', ['typeURI', 'screen_name', 'full_typeURI'])
    Data = namedtuple('data', ['selected_object_id','last_added'])

    def __init__(self, language_settings,parent):
        self._ = language_settings
        labels = [ self._("OTL_asset")]
        super().__init__(language_settings=language_settings,parent=parent,labels=labels)

        self.list_label_text = self._('class_list')
        self.list_subtext_label_text = self._("otl_asset_description")
        self.attribute_field_label_text = self._("object_attributes")

    def create_object_list_gui(self, multi_select: bool = False) -> QFrame:
        frame = super().create_object_list_gui(multi_select)
        self.frame_layout.setContentsMargins(11,0,0,0)
        self.list_gui.setProperty('class', 'object-list')
        return frame

    def on_item_selectionChange_listener(self, selected: QItemSelectionModel, deselected:QItemSelectionModel):
        # sourcery skip: remove-dict-keys

        if self.selected_item:
            type_folder_item = self.selected_item.parent()
            self.reset_selected_item_count(type_folder_item=type_folder_item)

        # Get the currently selected indexes
        self.selected_object = None
        dict_type_to_type_folder_item = {}
        dict_type_to_selected_item_count = {}
        for index in self.list_gui.selectionModel().selectedIndexes():
            if index.column() == 0:
                item = self.list_gui.model.itemFromIndex(index)
                if item and item.isSelectable():
                    selected_object_id = item.data(self.data_1_index)

                    self.selected_object = RelationChangeDomain.get_object(
                        identificator=selected_object_id)
                    self.selected_item = item



                    # keep count of selected items in folder
                    parent_type_folder_item = item.parent()
                    parent_type_folder_type = parent_type_folder_item.data(self.data_1_index)
                    if parent_type_folder_type in dict_type_to_selected_item_count.keys():
                        dict_type_to_selected_item_count[parent_type_folder_type] += 1
                    else:
                        dict_type_to_selected_item_count[parent_type_folder_type] = 1
                        dict_type_to_type_folder_item[parent_type_folder_type] = parent_type_folder_item

        # update the selected_counts on all type_folder_items
        for type_folder_type, selected_item_count in dict_type_to_selected_item_count.items():
            # OTLLogger.logger.debug( f"{type_folder_type}: {selected_item_count}")

            type_folder_item = dict_type_to_type_folder_item[type_folder_type]

            item_count = self.update_selected_count_data(type_folder_item=type_folder_item,
                                                         selected_item_count=selected_item_count)

            # apply new information to the folder_item display text
            self.set_type_folder_text(type_folder_item=type_folder_item,
                                      otl_type=type_folder_type,
                                      item_count=item_count,
                                      selected_item_count=selected_item_count)

        create_task_reraise_exception(RelationChangeDomain.set_possible_relations(selected_object=self.selected_object))

    def select_item_via_identificator(self,identificator):
        for i in range(self.list_gui.model.rowCount()):

            folder_item = self.list_gui.model.item(i)
            for j in range(folder_item.rowCount()):
                item = folder_item.child(j)
                if item.data(self.data_1_index) == identificator:
                    self.select_object_id(item)
                    self.parent.set_existing_relation_search_bar_text(item.text())

    def create_button(self):
        self.list_button.setEnabled(True)
        self.list_button.setText(self._("add_external_asset"))
        self.list_button.clicked.connect(
            self.add_external_asset)
        self.list_button.setProperty("class", 'add-external-button')
        return self.list_button

    def add_external_asset(self):
        add_asset_window = AddExternalAssetWindow(self._)
        add_asset_window.draw_add_external_asset_window()

    def is_previously_selected_requirement(self, text_and_data):
        return self.selected_object and RelationChangeHelpers.get_corrected_identificator(self.selected_object) == text_and_data['data'].selected_object_id

    def extract_text_and_data_per_item(self, source_object, objects, last_added):
        list_of_corresponding_values = []
        self.id_to_object_with_text_and_data_dict.clear() # for usage in MapScreen

        for OTL_object in objects:
            screen_name = RelationChangeHelpers.get_screen_name(OTL_object)
            add_namespace = RelationChangeHelpers.is_unique_across_namespaces(
                OTL_object.typeURI,
                RelationChangeDomain.shown_objects)
            abbr_typeURI = RelationChangeHelpers.get_abbreviated_typeURI(
                OTL_object.typeURI,
                add_namespace,
                OTLObjectHelper.is_relation(OTL_object))

            correct_id:str = RelationChangeHelpers.get_corrected_identificator(OTL_object)
            text_and_data = {
                "text": self.Text(abbr_typeURI,screen_name,OTL_object.typeURI),
                "data": self.Data(correct_id, False)
            }
            list_of_corresponding_values.append(text_and_data)

            self.id_to_object_with_text_and_data_dict[correct_id] = [OTL_object,text_and_data]
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
                # renew selected_item before new selection
                self.selected_item = previously_selected_item

                self.list_gui.selectionModel().setCurrentIndex(
                    previously_selected_item_index,
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

    def asset_clicked_listener(self):
        # automatically set the 3rd column (existing relations) to search for
        # the selected asset
        if self.selected_item:
            self.parent.set_existing_relation_search_bar_text(self.selected_item.text())

            # highlight on map
            if self.parent.map_window:

                selected_object_id = self.selected_item.data(self.data_1_index)
                self.selected_object = RelationChangeDomain.get_object(
                    identificator=selected_object_id)
                selected_id = RelationChangeHelpers.get_corrected_identificator(
                    otl_object=self.selected_object)

                if selected_id:
                    self.parent.map_window.activate_highlight_layer_by_id(selected_id)

    def update_this_gui_list_content(self):
        RelationChangeDomain.update_frontend_objects()

