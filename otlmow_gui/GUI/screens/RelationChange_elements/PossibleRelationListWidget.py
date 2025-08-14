from collections import namedtuple
from typing import Union

from PyQt6.QtCore import QItemSelectionModel, Qt
from PyQt6.QtGui import QStandardItem, QPixmap, QIcon, QFont
from PyQt6.QtWidgets import QFrame, QCheckBox
from otlmow_model.OtlmowModel.Helpers import OTLObjectHelper
from otlmow_model.OtlmowModel.BaseClasses.OTLObject import \
    OTLObject

from otlmow_gui.Domain.logger.OTLLogger import OTLLogger
from otlmow_gui.Domain.step_domain.RelationChangeDomain import RelationChangeDomain
from otlmow_gui.GUI.screens.RelationChange_elements.AbstractInstanceListWidget import \
    AbstractInstanceListWidget, IMG_DIR
from otlmow_gui.GUI.screens.RelationChange_elements.RelationChangeHelpers import RelationChangeHelpers
from otlmow_gui.exception_handler.ExceptionHandlers import create_task_reraise_exception


class PossibleRelationListWidget(AbstractInstanceListWidget):

    Text = namedtuple('text', ['typeURI', 'direction', 'screen_name', 'target_typeURI','full_typeURI'])
    Data = namedtuple('data', ['source_id', 'target_id', "index", "last_added"])

    def __init__(self, language_settings, parent):
        self._ = language_settings
        labels = [self._("related_asset"),self._("asset_type")]
        super().__init__(language_settings=language_settings,parent=parent, labels=labels, needs_source_object=True)

        self.list_label_text = self._('relations_list')
        self.list_subtext_label_text = self._("possible_relation_subscription")
        self.attribute_field_label_text = self._("possible_relation_partner_asset_attributes")
        self.show_all_OTL_relations_checkbox = QCheckBox()

    def create_object_list_gui(self, multi_select: bool = False) -> QFrame:
        frame = super().create_object_list_gui(multi_select)
        self.frame_layout.setContentsMargins(0,0,11,0)
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

        # padding_item = QStandardItem("")
        # padding_item.setEditable(False)
        # padding_item.setEnabled(False)
        # padding_item.setSelectable(False)

        # self.list_gui.addItem([place_holder_item,padding_item ])
        self.list_gui.addItem([place_holder_item])
    def create_attribute_field(self):
        attribute_field = super().create_attribute_field()
        attribute_field.setProperty("class","attribute_field_possible_relation")
        return attribute_field

    def object_selected_listener(self, item) -> None:
        pass

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
            # OTLLogger.logger.debug( f"{type_folder_type}: {selected_item_count}")

            type_folder_item = dict_type_to_type_folder_item[type_folder_type]

            item_count = self.update_selected_count_data(type_folder_item=type_folder_item,
                                                         selected_item_count=selected_item_count)

            # apply new information to the folder_item display text
            self.set_type_folder_text(type_folder_item=type_folder_item,
                                      otl_type=type_folder_type,
                                      item_count=item_count,
                                      selected_item_count=selected_item_count)

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

        create_task_reraise_exception(RelationChangeDomain.add_multiple_possible_relations_to_existing_relations(data_list=data_list))


        # for data in data_list:
        #     RelationChangeDomain.add_possible_relation_to_existing_relations(data.source_id,
        #                                                                      data.target_id,
        #                                                                      data.index)

    def possible_relations_selected(self):
        Data = self.Data # a named tuple type defined as variable of the class put into local var
        data_list: list[Data] = self.get_selected_data()

        create_task_reraise_exception(RelationChangeDomain.select_possible_relation_data(data_list))

    def get_selected_data(self):
        return [
            self.Data(self.list_gui.model.itemFromIndex(model_i).data(self.data_1_index)[0],
                      self.list_gui.model.itemFromIndex(model_i).data(self.data_1_index)[1],
                      self.list_gui.model.itemFromIndex(model_i).data(self.data_1_index)[2], False)

            for model_i in self.list_gui.selectionModel().selectedIndexes()
            if model_i.column() == 0] # we want one model_i per row, so only column == 0 is taken


    def extract_text_and_data_per_item(self, source_object: OTLObject, objects: Union[list[OTLObject],dict] , last_added):
        list_of_corresponding_values = []
        for target_identificator, target_relations in objects.items():

            for i, relation in enumerate(target_relations):
                relation_source_id:str = relation.bronAssetId.identificator
                relation_target_id: str = relation.doelAssetId.identificator

                target_object: OTLObject = RelationChangeDomain.get_object(
                                                                identificator=relation_target_id)
                try:
                    if target_object is None:
                        raise ValueError("target_object is None")
                    if source_object is None:
                        raise ValueError("source_object is None")
                except Exception as e:
                    OTLLogger.logger.debug(f"target or source are None in relation {relation.typeURI} \n{e}")
                    continue
                # if the target of the relation is the current selected object then you should
                # display the source object of the relation
                if target_object and source_object and target_object == source_object:
                    target_object =  RelationChangeDomain.get_object(
                                                          identificator=relation_source_id)

                #  if the new target_object is still the same as the source_object something is wrong
                if target_object and source_object and target_object == source_object:
                    raise ValueError()

                # determine the icon that indicates direction
                direction = ""
                if OTLObjectHelper.is_directional_relation(otl_object=relation):
                    if relation_source_id == target_identificator:
                        direction = RelationChangeHelpers.incoming_direction_icon

                    else:
                        direction = RelationChangeHelpers.outgoing_direction_icon
                else:
                    direction = RelationChangeHelpers.unspecified_direction_icon

                real_source_id: str = RelationChangeHelpers.get_corrected_identificator(
                    otl_object=source_object)
                abbr_relation_typeURI: str = RelationChangeHelpers.get_abbreviated_typeURI(
                    typeURI=relation.typeURI,
                    add_namespace=False,
                    is_relation=OTLObjectHelper.is_relation(relation))
                target_screen_name:str = RelationChangeHelpers.get_screen_name(otl_object=target_object)

                try:
                    add_target_namespace:bool = RelationChangeHelpers.is_unique_across_namespaces(
                        typeURI=target_object.typeURI,
                        objects=RelationChangeDomain.shown_objects)
                    abbr_target_object_typeURI:str = RelationChangeHelpers.get_abbreviated_typeURI(
                        typeURI=target_object.typeURI,
                        add_namespace=add_target_namespace,
                        is_relation=OTLObjectHelper.is_relation(target_object))

                    is_last_added:bool =    (relation.assetId.identificator in
                                            [e.assetId.identificator for e in last_added])

                    list_of_corresponding_values.append({
                        "text": self.Text(typeURI=abbr_relation_typeURI,
                                          direction=direction,
                                          screen_name=target_screen_name,
                                          target_typeURI=abbr_target_object_typeURI,
                                          full_typeURI=relation.typeURI),
                        "data": self.Data(source_id=real_source_id ,
                                          target_id=target_identificator,
                                          index=i,
                                          last_added=is_last_added)
                    })
                except Exception as e:
                    target_screen_name: str = RelationChangeHelpers.get_screen_name(
                        otl_object=target_object)
                    abbr_relation_typeURI: str = RelationChangeHelpers.get_abbreviated_typeURI(
                        typeURI=relation.typeURI,
                        add_namespace=False,
                        is_relation=OTLObjectHelper.is_relation(relation))
                    real_source_id: str = RelationChangeHelpers.get_corrected_identificator(
                        otl_object=source_object)
                    OTLLogger.logger.debug(f"Couldn't make relation {abbr_relation_typeURI}: {real_source_id} {direction} {target_screen_name} because \n{e}")
        list_of_corresponding_values.sort(key=lambda val: (
            val['text'].target_typeURI, val['text'].screen_name, val['text'].typeURI))
        return list_of_corresponding_values

    def is_last_added(self, text_and_data: dict):
        return text_and_data["data"].last_added

    def create_asset_type_standard_item(self, asset_type:str, text_and_data_list) -> QStandardItem:
        folder_item = super().create_asset_type_standard_item(asset_type,text_and_data_list)

        if text_and_data_list:
            full_typeURI = text_and_data_list[0]["text"].full_typeURI
            self.add_colored_relation_bol_icon_to_item(folder_item, full_typeURI)
        return folder_item

    def get_no_instance_selected_message(self) -> str:
        return self._("no_relation_selected")

    def add_extra_elements_to_list_subtext_layout(self) -> None:
        self.show_all_OTL_relations_checkbox.setText(self._("Toon all OTL-relaties"))
        self.show_all_OTL_relations_checkbox.setToolTip(self._("Toon alle mogelijke relaties met het geselecteerde asset in het volledige OTL (i.p.v. alleen subset)"))
        self.show_all_OTL_relations_checkbox.stateChanged.connect(self.state_change_OTL_relations_checkbox)

        self.list_subtext_layout.addWidget(self.show_all_OTL_relations_checkbox)


    def is_show_all_OTL_relations_checked(self) -> bool:
        return self.show_all_OTL_relations_checkbox.isChecked()

    def state_change_OTL_relations_checkbox(self,state:int) -> None:

        if state == Qt.CheckState.Unchecked.value:
            RelationChangeDomain.set_search_full_OTL_mode(state=False)
        elif state == Qt.CheckState.Checked.value:
            RelationChangeDomain.set_search_full_OTL_mode(state=True)
        else:
            # In case of an unexpected state, default to False.
            RelationChangeDomain.set_search_full_OTL_mode(state=False)

        RelationChangeDomain.update_frontend()

    def update_this_gui_list_content(self):
        RelationChangeDomain.update_frontend_possible_relations()


