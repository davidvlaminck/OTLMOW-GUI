from typing import Optional

from otlmow_gui.GUI.dialog_windows.file_picker_dialog.LoadFilePickerDialog import LoadFilePickerDialog


class SubsetLoadFilePickerDialog(LoadFilePickerDialog):

    instance = None

    def __init__(self, language_settings,title:Optional[str]=None,name_filter:str=None, initial_file_path: Optional[str]=None):
        super().__init__(language_settings,title,name_filter, initial_file_path)

        if not title:
            self.setWindowTitle(self._("Selecteer subset"))
        if not name_filter:
            self.setNameFilter(self._("Database files (*.db)"))

        SubsetLoadFilePickerDialog.instance = self
        #so you can easily access this from UpsertProjectWindow and ChangeSubsetWindow