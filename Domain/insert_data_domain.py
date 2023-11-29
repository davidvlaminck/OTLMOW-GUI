import logging
import ntpath
import os
import tempfile
from pathlib import Path
import warnings

from openpyxl.reader.excel import load_workbook
from otlmow_converter.OtlmowConverter import OtlmowConverter

from Exceptions.NotOTLConformError import NotOTLConformError


class InsertDataDomain:

    @classmethod
    def check_data(cls, data):
        doc_list = []
        asset_list = []
        for i in range(data.topLevelItemCount()):
            item = data.topLevelItem(i)
            doc_list.append(item.text(0))
        print(doc_list)
        for doc in doc_list:
            doc_split = doc.split('.')
            if doc_split[-1] == 'xls' or doc_split[-1] == 'xlsx':
                temp_path = cls.start_excel_changes(doc=doc)
            elif doc_split[-1] == 'csv':
                temp_path = Path(doc)
            try:
                asset = cls.check_document(doc_location=temp_path)
            except ValueError as e:
                logging.debug("Reached")
                warnings.warn("The document is not OTL conform", NotOTLConformError)
                continue
            asset_list.append(asset)
            print(asset_list)
            return asset_list

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
    def return_temp_path(cls, path_to_template_file_and_extension: Path):
        tempdir = Path(tempfile.gettempdir()) / 'temp-otlmow'
        if not tempdir.exists():
            os.makedirs(tempdir)
        doc_name = ntpath.basename(path_to_template_file_and_extension)
        temporary_path = Path(tempdir) / doc_name
        return temporary_path
