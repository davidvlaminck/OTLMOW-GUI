from typing import Optional

from PyQt6.QtWidgets import QWidget, QMessageBox, QDialogButtonBox


class YesOrNoNotificationWindow(QMessageBox):

    def __init__(self, message:str, title:str = "notification", alt_yes_text: Optional[str] = None, alt_no_text : Optional[str] = None):
        self.message = message
        self.title = title
        super().__init__()

        self.setWindowTitle(self.title)
        self.setText(self.message)
        self.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if alt_yes_text:
            self.button(QMessageBox.StandardButton.Yes).setText(alt_yes_text)
        if alt_no_text:
            self.button(QMessageBox.StandardButton.No).setText(alt_no_text)