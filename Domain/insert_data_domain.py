import os
import tempfile
from pathlib import Path
from typing import List

from openpyxl.reader.excel import load_workbook
from otlmow_converter.OtlmowConverter import OtlmowConverter


class InsertDataDomain:

    @classmethod
    def check_document(cls, doc_location) -> List:
        converter = OtlmowConverter()
        return converter.create_assets_from_file(filepath=Path(doc_location))

    @classmethod
    def start_excel_changes(cls, doc) -> Path:
        wb = load_workbook(doc)
        temp_path = cls.return_temp_path(path_to_template_file_and_extension=doc)
        if 'Keuzelijsten' in wb.sheetnames:
            wb.remove(wb['Keuzelijsten'])
        wb.save(temp_path)
        return temp_path

    @classmethod
    def return_temp_path(cls, path_to_template_file_and_extension: Path) -> Path:
        tempdir = Path(tempfile.gettempdir()) / 'temp-otlmow'
        if not tempdir.exists():
            os.makedirs(tempdir)
        doc_name = Path(path_to_template_file_and_extension) .name
        temporary_path = Path(tempdir) / doc_name
        return temporary_path