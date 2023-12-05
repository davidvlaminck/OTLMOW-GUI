import json
import logging
import os
import tempfile
from enum import Enum
from pathlib import Path
from typing import List

from openpyxl.reader.excel import load_workbook
from otlmow_converter.OtlmowConverter import OtlmowConverter

from Domain.Project import Project
from Domain.ProjectFileManager import ProjectFileManager
from Domain.project_file import ProjectFile


class InsertDataDomain:

    @classmethod
    def check_document(cls, doc_location) -> List:
        converter = OtlmowConverter()
        return converter.create_assets_from_file(filepath=Path(doc_location))

    @classmethod
    def start_excel_changes(cls, doc) -> Path:
        wb = load_workbook(doc)
        temp_path = cls.create_temp_path(path_to_template_file_and_extension=doc)
        if 'Keuzelijsten' in wb.sheetnames:
            wb.remove(wb['Keuzelijsten'])
        wb.save(temp_path)
        return temp_path

    @classmethod
    def create_temp_path(cls, path_to_template_file_and_extension: Path) -> Path:
        tempdir = Path(tempfile.gettempdir()) / 'temp-otlmow'
        if not tempdir.exists():
            os.makedirs(tempdir)
        doc_name = Path(path_to_template_file_and_extension).name
        temporary_path = Path(tempdir) / doc_name
        return temporary_path

    @classmethod
    def add_template_file_to_project(cls, filepath: Path, project: Project, state: Enum):
        end_loc = ProjectFileManager().add_template_file_to_project(filepath=filepath)
        logging.debug("test" + str(end_loc))
        template_file = ProjectFile(file_path=end_loc, state=state)
        project.templates_in_memory.append(template_file)

    @classmethod
    def return_temporary_path(cls, file_path: Path) -> Path:
        if Path(file_path).suffix == '.xls' or Path(file_path).suffix == '.xlsx':
            temp_path = cls.start_excel_changes(doc=file_path)
        elif Path(file_path).suffix == '.csv':
            temp_path = cls.create_temp_path(path_to_template_file_and_extension=file_path)
        return temp_path
