import logging
import os.path
from pathlib import Path

from PyQt6.QtWidgets import QFileDialog


class ExportToTemplateWindow(QFileDialog):

    previous_selected_directory = None

    def __init__(self):
        super().__init__()

        start_dir = str(Path.home() / "Documents")
        if ExportToTemplateWindow.previous_selected_directory:
            start_dir = str(ExportToTemplateWindow.previous_selected_directory)

        self.setModal(True)
        self.setDirectory(start_dir)

    def get_file_location(self) -> str:
        """
        Prompts the user to select a file location for saving.

        This function opens a file dialog that allows the user to choose a location to save a file,
        with options for Excel and CSV formats. It returns the selected file path or None if no
        file was selected.

        Args:
            self: The instance of the class.

        Returns:
            str: The path of the selected file, or None if no file was selected.
        """

        document_loc = self.getSaveFileName(
            filter="Excel files (*.xlsx);;CSV files (*.csv)")
        if document_loc == ('', ''):
            logging.debug("No file selected")
            return None
        elif document_loc:
            ExportToTemplateWindow.previous_selected_directory = os.path.dirname(str(document_loc[0]))

            return document_loc[0]


