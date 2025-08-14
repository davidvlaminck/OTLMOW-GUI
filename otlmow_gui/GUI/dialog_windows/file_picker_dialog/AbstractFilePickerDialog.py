from abc import abstractmethod
from copy import deepcopy
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import QFileDialog

from otlmow_gui.Domain import global_vars


class AbstractFilePickerDialog(QFileDialog):


    def __init__(self, language_settings, title: Optional[str], name_filter: str = None,
                 initial_file_path: Optional[str] = None):
        super().__init__()
        self._ = language_settings
        self.name_filter = name_filter
        self.previous_file_dialog_state = None
        self.previous_exported_file_name = None

        self.supported_export_formats: dict = deepcopy(global_vars.supported_file_formats)

        self.setWindowTitle(title)
        if initial_file_path:
            self.setDirectory(initial_file_path)
        else:
            self.setDirectory(str(Path.home() / "Documents"))
        self.setNameFilter(self.getCustomFilters())

    def getCustomFilters(self) -> str:
        if self.name_filter:
            return self.name_filter

        supported_extensions = [f'*.{value}' for value in
                                self.supported_export_formats.values()]
        supported_extensions_string = ' '.join(supported_extensions)
        filters = [self._('Alle ondersteunde bestanden ({supported_extensions_string})').format(
            supported_extensions_string=supported_extensions_string)]

        filters.extend(f"{k} files (*.{v})" for k, v in self.supported_export_formats.items())

        return ";;".join(filters)

    def summon(self, chosen_file_format: Optional[str]= "", directory: Optional[str|Path]=None,
               supported_export_formats:dict[str,str]=None,project_name:Optional[str] = None):

        if directory:
            if isinstance(directory,str):
                directory = Path(directory)
            if directory.exists():
                self.setDirectory(str(directory))
            elif self.previous_file_dialog_state:
                self.setDirectory(self.previous_file_dialog_state)

        elif self.previous_file_dialog_state:
            self.setDirectory(self.previous_file_dialog_state)

        if chosen_file_format:
            if not supported_export_formats:
                supported_export_formats = self.supported_export_formats

            if chosen_file_format in supported_export_formats:
                file_suffix = supported_export_formats[chosen_file_format]
                filter_filepicker = f"{chosen_file_format} files (*.{file_suffix})"
                self.setNameFilter(filter_filepicker)

        self.set_filename_suggestions(project_name)

        res = self.execute()

        self.previous_file_dialog_state = self.directory().absolutePath()
        self.store_save_filename(res)

        #make sure that loaded files actually have the format that is chosen
        if chosen_file_format and (chosen_file_format in supported_export_formats) and res:
            file_suffix = supported_export_formats[chosen_file_format]

            for i in range(len(res)):
                res[i] = res[i].with_suffix("")
                if res[i].suffix != f".{file_suffix}":
                    res[i]= res[i].with_suffix(f".{file_suffix}")

        return res

    def set_filename_suggestions(self, project_name):
        pass

    @abstractmethod
    def execute(self) -> list[Path]:
       return []

    def store_save_filename(self,res:list[str]):
        pass

    def get_filename_suggestion(self, project_name):
        pass