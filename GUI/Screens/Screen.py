from abc import abstractmethod

from PyQt6.QtWidgets import QWidget


class Screen(QWidget):

    @abstractmethod
    def reset_ui(self, _):
        pass
