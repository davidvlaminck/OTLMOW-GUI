from abc import abstractmethod

from PyQt6.QtWidgets import QWidget


class Screen(QWidget):
    def __init__(self):
        super().__init__()
        self.projects: list = []

    @abstractmethod
    def reset_ui(self, _):
        raise NotImplementedError
