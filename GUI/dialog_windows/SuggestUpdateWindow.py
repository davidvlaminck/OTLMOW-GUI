import logging
import webbrowser

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QDialogButtonBox


class SuggestUpdateWindow:

    def __init__(self, language_settings, local_version, new_version):
        self.local_version = local_version
        self.new_version = new_version
        self._ = language_settings
        self.init_ui()

    def init_ui(self):
        dialog = QDialog()
        dialog.setModal(True)
        dialog.setWindowTitle(self._("update_available_title"))
        layout = QVBoxLayout()
        question_label = QLabel()
        question_label.setText(self._("update_available_text").format(self.local_version,self.new_version))
        layout.addWidget(question_label)
        button_box = self.create_button_box()
        button_box.accepted.connect(lambda: self.remove_project_files(dialog))
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        dialog.setLayout(layout)
        dialog.show()
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