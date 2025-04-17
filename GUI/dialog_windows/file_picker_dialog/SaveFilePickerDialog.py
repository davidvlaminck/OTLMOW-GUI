from copy import deepcopy
from pathlib import Path
from typing import Optional

from Domain.logger.OTLLogger import OTLLogger
from GUI.dialog_windows.file_picker_dialog.AbstractFilePickerDialog import AbstractFilePickerDialog


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
                        excluded_type)  # SDF is not yet supported for export in V0.7.2
        self.setModal(True)


    def execute(self):
        save_location = self.getSaveFileName(filter=";;".join(self.nameFilters()))
        if not save_location:
            OTLLogger.logger.debug(f"save_file_dialog return: {[]}")
            return []
        if not save_location[0]:
            OTLLogger.logger.debug(f"save_file_dialog return: {[]}")
            return []

        OTLLogger.logger.debug(f"save_file_dialog return: {[Path(save_location[0])]}")
        return [Path(save_location[0])]



