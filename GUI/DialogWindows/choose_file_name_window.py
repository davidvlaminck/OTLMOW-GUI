from PyQt6.QtWidgets import QDialog, QLabel, QVBoxLayout, QLineEdit, QFrame, QHBoxLayout, QComboBox, QDialogButtonBox

from Domain.asset_change_domain import AssetChangeDomain


class ChooseFileNameWindow:

    def __init__(self, language_settings, project, new_files):
        self._ = language_settings
        self.project = project
        self.new_files = new_files
        self.file_name = QLineEdit()
        self.extension_picker = QComboBox()

    def file_name_window(self):
        dialog_window = QDialog()
        dialog_window_layout = QVBoxLayout()
        dialog_window.setModal(True)
        dialog_window.setWindowTitle(self._("choose_file_name"))
        dialog_window_layout.addWidget(self.file_name_layout())
        dialog_window_layout.addWidget(self.file_extension_picker())
        button_box = self.create_button_box()
        dialog_window_layout.addWidget(button_box)
        button_box.accepted.connect(lambda: self.accept(dialog_window))
        button_box.rejected.connect(dialog_window.reject)
        dialog_window.setLayout(dialog_window_layout)
        dialog_window.show()
        dialog_window.exec()

    def file_name_layout(self):
        frame = QFrame()
        frame_layout = QHBoxLayout()
        file_label = QLabel()
        file_label.setText(self._("choose_file_name") + ":")
        frame_layout.addWidget(file_label)
        frame_layout.addWidget(self.file_name)
        frame.setLayout(frame_layout)
        return frame

    def file_extension_picker(self):
        frame = QFrame()
        frame_layout = QHBoxLayout()
        extension_label = QLabel()
        extension_label.setText(self._("choose_file_extension") + ":")
        self.extension_picker.addItems([".csv", ".xlsx", ".json"])
        frame_layout.addWidget(extension_label)
        frame_layout.addWidget(self.extension_picker)
        frame.setLayout(frame_layout)
        return frame

    def create_button_box(self):
        button_box = QDialogButtonBox()
        button_box.setStandardButtons(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.setProperty('class', 'button-box')
        button_box.button(QDialogButtonBox.StandardButton.Ok).setText(self._('submit'))
        button_box.button(QDialogButtonBox.StandardButton.Ok).setProperty('class', 'primary-button')
        button_box.button(QDialogButtonBox.StandardButton.Cancel).setText(self._('cancel'))
        return button_box

    def accept(self, dialog_window):
        file_name = self.file_name.text()
        file_extension = self.extension_picker.currentText()
        AssetChangeDomain().replace_files_with_diff_report(project=self.project, original_documents=self.new_files,
                                                           file_name=file_name, extension=file_extension)
        dialog_window.close()
