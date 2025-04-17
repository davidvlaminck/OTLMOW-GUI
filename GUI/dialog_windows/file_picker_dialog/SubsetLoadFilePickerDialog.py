from typing import Optional

from PyQt6.QtWidgets import QFileDialog

from GUI.dialog_windows.file_picker_dialog.LoadFilePickerDialog import LoadFilePickerDialog


class SubsetFilePickerDialog(LoadFilePickerDialog):

    instance = None

    def __init__(self, language_settings, action_function,title:Optional[str],name_filter:str=None, initial_file_path: Optional[str]=None):
        super().__init__(language_settings, action_function,title,name_filter, initial_file_path)

        if not title:
            self.setWindowTitle(self._("Selecteer subset"))
        if not name_filter:
            self.setNameFilter(self._("Database files (*.db)"))

        SubsetFilePickerDialog.instance = self
        #so you can easily access this from UpsertProjectWindow and ChangeSubsetWindow