import logging
from pathlib import Path

from PyQt6.QtWidgets import QFileDialog


class ExportToTemplateWindow:

    @staticmethod
    def export_to_template_window():
        file_picker = QFileDialog()
        file_picker.setModal(True)
        file_picker.setDirectory(str(Path.home()))
        document_loc = file_picker.getSaveFileName(filter="Excel files (*.xlsx);;CSV files (*.csv)")
        if document_loc == ('', ''):
            logging.debug("No file selected")
            return None
        elif document_loc:
            return document_loc[0]

