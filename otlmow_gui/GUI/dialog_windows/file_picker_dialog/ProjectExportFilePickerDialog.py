from typing import Optional

from otlmow_gui.GUI.dialog_windows.file_picker_dialog.SaveFilePickerDialog import SaveFilePickerDialog


class ProjectExportFilePickerDialog(SaveFilePickerDialog):

    def __init__(self, language_settings, title: Optional[str]=None,
                 name_filter: str = None, initial_file_path: Optional[str] = None,
                 exclude_file_types: list[str] = []):

        super().__init__(language_settings, title, name_filter, initial_file_path,
                         exclude_file_types)
        if not title:
            self.setWindowTitle(self._("export_OTL_project"))
        if not name_filter:
            self.setNameFilter(self._("OTLWizard project files (*.otlw)"))

    def get_filename_suggestion(self, project_name):
        return project_name + "_project"

    def store_save_filename(self, res: list[str]):
        pass

