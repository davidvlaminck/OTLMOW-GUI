import logging

from PyQt6.QtWidgets import QWidget, QMessageBox
import pyperclip as pc


class ErrorScreen(QWidget):

    def __init__(self, error_message):
        self.error_message = error_message
        pc.copy(error_message)
        super().__init__()
        self.init_ui()

    def init_ui(self):
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Unhandled Exception")
        dlg.setText(self.error_message + '\nError message copied to clipboard.')
        button = dlg.exec()
