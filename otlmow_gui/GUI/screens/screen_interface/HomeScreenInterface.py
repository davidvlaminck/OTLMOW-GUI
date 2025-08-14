from abc import abstractmethod

from PyQt6.QtWidgets import QWidget

from otlmow_gui.Domain.project.Project import Project
from otlmow_gui.GUI.screens.Screen import Screen


class HomeScreenInterface(Screen):

    def __init__(self):
        super().__init__()

    @abstractmethod
    def create_main_content_ui(self) -> None:
        pass
    @abstractmethod
    def fill_table(self,projects: [Project]) -> None:
        pass

    @abstractmethod
    def draw_search_bar(self) -> QWidget:
        pass

    @abstractmethod
    def create_input_field(self) -> None:
        pass

    @abstractmethod
    def remove_table_row(self, row_index: int) -> None:
        pass

