import os.path
from abc import abstractmethod
from copy import deepcopy
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import QFileDialog

from Domain import global_vars


class AbstractFilePickerDialog(QFileDialog):


    def __init__(self, language_settings, action_function,title:Optional[str],name_filter:str=None, initial_file_path: Optional[str]=None):
        super().__init__()
        self._ = language_settings
        self.action_function = action_function
        self.name_filter = name_filter

        self.supported_export_formats: dict = deepcopy(global_vars.supported_file_formats)

        self.setWindowTitle(title)
        if initial_file_path:
            self.setDirectory(initial_file_path)
        else:
            self.setDirectory(str(Path.home()))
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

    def summon(self, chosen_file_format: Optional[str]= "", directory: Optional[str]=None):
        if directory and os.path.exists(directory):
            self.setDirectory(directory)

        if chosen_file_format:
            self.setNameFilter(chosen_file_format)

        self.execute()

    @abstractmethod
    def execute(self):
       pass

    def set_action_function(self,action_function):
        self.action_function = action_function