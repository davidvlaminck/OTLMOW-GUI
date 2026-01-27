from typing import Optional

from otlmow_gui.GUI.dialog_windows.file_picker_dialog.LoadFilePickerDialog import LoadFilePickerDialog


class ProjectImportFilePickerDialog(LoadFilePickerDialog):


    def __init__(self, language_settings, title: Optional[str] = None,
                 name_filter: str = None, initial_file_path: Optional[str] = None):
        
        super().__init__(language_settings, title, name_filter, initial_file_path)
        if not title:
            self.setWindowTitle(self._("select_OTL_project"))
        if not name_filter:
            self.setNameFilter(self._("OTLWizard project files (*.otlw)"))