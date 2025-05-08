from PyQt6.QtWidgets import QMessageBox, QPushButton

from otlmow_gui.Domain.step_domain.ExportFilteredDataSubDomain import ExportFilteredDataSubDomain


class ChooseFileNameWindow:

    def __init__(self, language_settings, project, new_files):
        self._ = language_settings
        self.project = project
        self.new_files = new_files

    def accept(self, dialog_window):
        file_name = "changed_files.json"
        ExportFilteredDataSubDomain().replace_files_with_diff_report(project=self.project, original_documents=self.new_files,
                                                                     file_name=file_name)
        dialog_window.close()

    def warning_overwrite_screen(self):
        dlg = QMessageBox()
        dlg.setWindowTitle(self._("warning overwriting files"))
        dlg.setText(self._("warning overwriting files text"))
        dlg.setIcon(QMessageBox.Icon.Warning)
        dlg.addButton(QPushButton(self._("yes")), QMessageBox.ButtonRole.YesRole)
        dlg.addButton(QPushButton(self._("no")), QMessageBox.ButtonRole.NoRole)
        dlg.exec()
        reply = dlg.buttonRole(dlg.clickedButton())
        if reply == QMessageBox.ButtonRole.YesRole:
            self.accept(dlg)
