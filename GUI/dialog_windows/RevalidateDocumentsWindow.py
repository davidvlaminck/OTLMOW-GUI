import asyncio

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QDialogButtonBox


class RevalidateDocumentsWindow:

    def __init__(self, screen, language_settings):
        self.screen =screen
        self._ = language_settings
        self.init_ui()

    def init_ui(self):
        dialog = QDialog()
        dialog.setModal(True)
        dialog.setWindowTitle(self._("revalidate_documents_files_title"))
        layout = QVBoxLayout()
        question_label = QLabel()
        question_label.setText(self._("revalidate_documents_files_question"))
        layout.addWidget(question_label)
        button_box = self.create_button_box()
        button_box.accepted.connect(lambda: self.validate_documents_again(dialog))
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        dialog.setLayout(layout)
        dialog.show()
        dialog.exec()

    def create_button_box(self):
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.setProperty("class", "button-box")
        button_box.button(QDialogButtonBox.StandardButton.Ok).setProperty("class", "primary-button")
        button_box.button(QDialogButtonBox.StandardButton.Ok).setText(self._('continue'))
        button_box.button(QDialogButtonBox.StandardButton.Cancel).setProperty("class", "secondary-button")
        button_box.button(QDialogButtonBox.StandardButton.Cancel).setText(self._("cancel"))
        return button_box

    def validate_documents_again(self, dialog):
        event_loop = asyncio.get_event_loop()
        event_loop.create_task(self.screen.validate_documents())
        dialog.close()

