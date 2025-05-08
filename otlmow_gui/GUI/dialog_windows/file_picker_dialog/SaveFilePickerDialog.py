from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import QFileDialog

from otlmow_gui.Domain.logger.OTLLogger import OTLLogger
from otlmow_gui.GUI.dialog_windows.file_picker_dialog.AbstractFilePickerDialog import AbstractFilePickerDialog


class SaveFilePickerDialog(AbstractFilePickerDialog):
    def __init__(self, language_settings,title:Optional[str] = None,name_filter:str=None, initial_file_path: Optional[str]=None,
                 exclude_file_types:list[str]=[]):


        super().__init__(language_settings, title, name_filter, initial_file_path)
        if not title:
            self.setWindowTitle(self._("Exporteer bestand(en)"))  # standard title for save dialogs

        if not name_filter:
            for excluded_type in exclude_file_types:
                if excluded_type in self.supported_export_formats:
                    self.supported_export_formats.pop(
                        excluded_type)  # SDF is not yet supported for export in V1.0
        self.setModal(True)
        self.setAcceptMode(QFileDialog.AcceptSave)


    def execute(self):
        if not self.exec():
            return[]

        save_location = self.selectedFiles()

        if not save_location:
            OTLLogger.logger.debug(f"save_file_dialog return: {[]}")
            return []
        if not save_location[0]:
            OTLLogger.logger.debug(f"save_file_dialog return: {[]}")
            return []

        OTLLogger.logger.debug(f"save_file_dialog return: {[Path(save_location[0])]}")
        return [Path(save_location[0])]

    def store_save_filename(self, res: list[str]):
        if len(res):
            if res[0]:
                self.previous_exported_file_name = str(Path(res[0]).stem)

    def set_filename_suggestions(self, project_name):

        if self.previous_exported_file_name:
            initial_filename = self.previous_exported_file_name
        elif project_name:
            initial_filename = self.get_filename_suggestion(project_name)
        else:
            initial_filename = "export"

        self.selectFile(initial_filename)

    def get_filename_suggestion(self, project_name):
        return project_name + "_export"





