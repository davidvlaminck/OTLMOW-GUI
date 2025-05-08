from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import QFileDialog

from otlmow_gui.Domain import global_vars
from otlmow_gui.Domain.logger.OTLLogger import OTLLogger
from otlmow_gui.GUI.dialog_windows.file_picker_dialog.AbstractFilePickerDialog import AbstractFilePickerDialog


class LoadFilePickerDialog(AbstractFilePickerDialog):
    def __init__(self, language_settings,title:Optional[str]= None,name_filter:str=None, initial_file_path: Optional[str]=None):



        super().__init__(language_settings, title, name_filter, initial_file_path)
        self.setFileMode(QFileDialog.FileMode.ExistingFiles)

        if not title:
            self.setWindowTitle(self._("Selecteer bestand"))  # standard title for load dialogs

    def getCustomFilters(self) -> str:
        supported_extensions = [f'*.{value}' for value in
                                global_vars.supported_file_formats.values()]
        supported_extensions_string = ' '.join(supported_extensions)
        filters = [self._('Alle ondersteunde bestanden ({supported_extensions_string})').format(
            supported_extensions_string=supported_extensions_string)]

        filters.extend(f"{k} files (*.{v})" for k, v in global_vars.supported_file_formats.items())

        return ";;".join(filters)

    def execute(self) -> list[Path]:
        if self.exec():
            res = [Path(selected_path_str) for selected_path_str in self.selectedFiles() if
             selected_path_str]
            OTLLogger.logger.debug(f"save_file_dialog return: {res}")
            return res
        OTLLogger.logger.debug(f"save_file_dialog return: {[]}")
        return []

