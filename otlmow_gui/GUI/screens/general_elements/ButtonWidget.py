from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QPushButton


class ButtonWidget(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
