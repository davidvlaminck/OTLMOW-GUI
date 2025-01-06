from abc import abstractmethod

from PyQt6.QtWidgets import QFrame, QWidget

from Domain.project.Project import Project
from GUI.screens.Screen import Screen


class TemplateScreenInterface(Screen):

    def __init__(self):
        super().__init__()


    @abstractmethod
    def init_ui(self) -> None:
        pass


    @abstractmethod
    def options_menu(self) -> QFrame:
        pass


    @abstractmethod
    def create_example_generation_container(self) -> QFrame:
        pass


    @abstractmethod
    def template_menu(self) -> QWidget:
        pass


    @abstractmethod
    def subset_title_and_button(self)  -> QFrame:
        pass


    @abstractmethod
    def create_operator_info_field(self) -> QFrame:
        pass


    @abstractmethod
    def create_otl_version_field(self) -> QFrame:
        pass


    @abstractmethod
    def create_subset_name_field(self) -> QFrame:
        pass


    @abstractmethod
    def subset_info_list(self) -> QFrame:
        pass


    @abstractmethod
    def create_list(self) -> QFrame:
        pass


    @abstractmethod
    def update_project_info(self, project:Project) -> None:
        pass


    @abstractmethod
    def update_label_under_list(self) -> None:
        pass


    @abstractmethod
    def select_all_classes_clicked(self) -> None:
        pass

    @abstractmethod
    def reset_ui(self, _):
        pass


    @abstractmethod
    def set_gui_list_to_loading_state(self) -> None:
        pass

    @abstractmethod
    def set_gui_list_to_no_classes_found(self) -> None:
        pass

    @abstractmethod
    def set_classes(self, classes, has_a_class_with_deprecated_attributes) -> None:
        pass