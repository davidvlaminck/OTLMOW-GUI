import logging
import webbrowser

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QDialogButtonBox


class SuggestUpdateWindow:


    def __init__(self, language_settings, local_version:str, new_version:str,otl_model_out_of_date:bool = False):
        self.local_version:str = local_version
        self.new_version:str = new_version
        self._ = language_settings

        if otl_model_out_of_date:
            self.dialog_title:str = self._("otl_model_out_of_date_title")
            self.dialog_text:str = self._("otl_model_out_of_date_text").format(self.local_version,self.new_version)
        else:
            self.dialog_title:str  = self._("update_available_title")
            self.dialog_text:str  = self._("update_available_text").format(self.local_version,self.new_version)
        self.init_ui()

    def init_ui(self):
        dialog = QDialog()
        dialog.setModal(True)
        dialog.setWindowTitle(self.dialog_title)
        layout = QVBoxLayout()
        question_label = QLabel()
        question_label.setText(self.dialog_text)
        layout.addWidget(question_label)
        button_box = self.create_button_box()
        button_box.accepted.connect(lambda: self.remove_project_files(dialog))
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        dialog.setLayout(layout)

        dialog.setWindowFlags(dialog.windowFlags() | Qt.WindowStaysOnTopHint)  # Keep it on top

        dialog.raise_()
        dialog.activateWindow()

        dialog.exec()

    def create_button_box(self):
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.setProperty("class", "button-box")
        button_box.button(QDialogButtonBox.StandardButton.Ok).setProperty("class", "primary-button")
        button_box.button(QDialogButtonBox.StandardButton.Ok).setText(self._("yes"))
        button_box.button(QDialogButtonBox.StandardButton.Cancel).setProperty("class", "secondary-button")
        button_box.button(QDialogButtonBox.StandardButton.Cancel).setText(self._("no"))
        return button_box

    def remove_project_files(self, dialog):
        logging.info("User choose to update")
        self.open_wiki()
        dialog.close()


    @staticmethod
    def open_wiki():
        webbrowser.open('https://github.com/davidvlaminck/otlmow-gui/wiki/Installation')
