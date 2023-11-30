import os
import tempfile
from pathlib import Path

from openpyxl.reader.excel import load_workbook
from otlmow_converter.OtlmowConverter import OtlmowConverter


class InsertDataDomain:

    @classmethod
    def check_document(cls, doc_location):
        converter = OtlmowConverter()
        assets = converter.create_assets_from_file(filepath=Path(doc_location))
        return assets

    @classmethod
    def start_excel_changes(cls, doc):
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
        doc_name = path_to_template_file_and_extension.name
        temporary_path = Path(tempdir) / doc_name
        return temporary_path
