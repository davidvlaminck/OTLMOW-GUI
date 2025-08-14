from typing import Optional, List

from PyQt6.QtWidgets import QWidget, QFrame
from otlmow_model.OtlmowModel.BaseClasses.RelationInteractor import RelationInteractor
from otlmow_model.OtlmowModel.Classes.ImplementatieElement.RelatieObject import RelatieObject

from otlmow_gui.GUI.screens.Screen import Screen

class RelationChangeScreenInterface(Screen):
    def set_gui_lists_to_loading_state(self) -> None:
        pass

    def paintEvent(self, a0):
        pass
    def synchronize_subtext_label_heights(self) -> None:
        pass
    def init_ui(self) -> None:
        pass

    def create_menu(self) -> QWidget:
        pass

    def fill_object_list(self, objects: List[RelationInteractor]) -> None:
        pass

    def fill_existing_relations_list(self, relations_objects: List[RelatieObject],
                                     last_added: list[RelatieObject] = None) -> None:
        pass

    def fill_possible_relations_list(self, source_object: Optional[RelationInteractor],
                                     relations: dict[str, list[RelatieObject]],
                                     last_added=None) -> None:
        pass

    def horizontal_layout(self) -> QFrame:
        pass


    def fill_object_attribute_field(self, object_attribute_dict: dict) -> None:
        pass

    def fill_possible_relation_attribute_field(self,
                                               possible_relation_attribute_dict: dict) -> None:
        pass
    def fill_existing_relation_attribute_field(self,
                                               existing_relation_attribute_dict: dict) -> None:
        pass

    def expand_existing_relations_folder_of(self, relation_typeURI: str) -> None:
        pass

    def expand_possible_relations_folder_of(self, relation_typeURI: str) -> None:
        pass

    def showMultiSelectionHeeftBetrokkeneAttributeDialogWindow(self,
                                                               data_list_and_relation_objects: list) -> None:
        pass

    def clear_possible_relation_elements(self):
        pass

    def get_current_object_list_content_dict(self) -> dict[str, list]:
        pass

    def set_selected_object(self, identificator: str):
        pass

    def is_show_all_OTL_relations_checked(self) -> bool:
        pass