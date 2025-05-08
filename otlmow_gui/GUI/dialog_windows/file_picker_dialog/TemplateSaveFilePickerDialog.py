from typing import Optional

from otlmow_gui.GUI.dialog_windows.file_picker_dialog.SaveFilePickerDialog import SaveFilePickerDialog


class TemplateSaveFilePickerDialog(SaveFilePickerDialog):


    def __init__(self, language_settings, title: Optional[str] = None,
                 name_filter: str = None, initial_file_path: Optional[str] = None,
                 exclude_file_types: list[str] = []):

        exclude_file_types.extend(['GeoJSON',"JSON"])

        super().__init__(language_settings, title, name_filter, initial_file_path,
                         exclude_file_types)

        if not title:
            self.setWindowTitle(self._("Sla template op"))

    def get_filename_suggestion(self, project_name):
        return project_name + "_template"



