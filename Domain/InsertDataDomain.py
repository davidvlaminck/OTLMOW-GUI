import logging
import os
import tempfile
from pathlib import Path
from typing import List, Iterable

from openpyxl.reader.excel import load_workbook
from otlmow_converter.OtlmowConverter import OtlmowConverter
from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLObject

from Domain import global_vars
from Domain.Project import Project
from Domain.ProjectFileManager import ProjectFileManager
from Domain.RelationChangeDomain import RelationChangeDomain
from Domain.enums import FileState
from Domain.ProjectFile import ProjectFile
from Exceptions.ExcelFileUnavailableError import ExcelFileUnavailableError
from GUI.DialogWindows.NotificationWindow import NotificationWindow
from GUI.translation.GlobalTranslate import GlobalTranslate
from UnitTests.TestClasses.Classes.ImplementatieElement.AIMObject import AIMObject


class InsertDataDomain:

    @classmethod
    def check_document(cls, doc_location) -> Iterable[OTLObject]:
        return OtlmowConverter.from_file_to_objects(file_path=Path(doc_location))

    @classmethod
    def start_excel_changes(cls, doc) -> Path:
        logging.debug("starting excel changes")
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
        return Path(tempdir) / doc_name

    @classmethod
    def add_template_file_to_project(cls, filepath: Path, project: Project, state: FileState):
        if Path(filepath).suffix in ['.xls', '.xlsx']:
            filepath = cls.start_excel_changes(doc=filepath)
        end_loc = ProjectFileManager.add_template_file_to_project(filepath=filepath)
        template_file = ProjectFile(file_path=end_loc, state=state)
        project.saved_objects_lists.append(template_file)

    @classmethod
    def return_temporary_path(cls, file_path: Path) -> Path:
        if Path(file_path).suffix in ['.xls', '.xlsx']:
            return cls.start_excel_changes(doc=file_path)
        elif Path(file_path).suffix == '.csv':
            return cls.create_temp_path(path_to_template_file_and_extension=file_path)

    @classmethod
    def delete_project_file_from_project(cls, project: Project, file_path: Path):
        try:

            if (ProjectFileManager.delete_template_file_from_project(
                    file_path=file_path)):
                for file in project.saved_objects_lists:
                    if file.file_path == file_path:
                        project.saved_objects_lists.remove(file)
                        break
                ProjectFileManager.add_project_files_to_file(project=project)
                return True
            else:
                return False

        except ExcelFileUnavailableError as e:
            message = GlobalTranslate._(e.error_window_message_key)
            title = GlobalTranslate._(e.error_window_title_key)
            NotificationWindow("{0}:\n{1}".format(message,e.file_path),title)

    @classmethod
    def remove_all_project_files(cls, project: Project):
        logging.debug("memory contains %s",
                      project.saved_objects_lists)
        for file in project.saved_objects_lists:
            logging.debug("starting to delete file %s",
                          file.file_path)
            try:
                ProjectFileManager.delete_template_file_from_project(
                    file_path=file.file_path)
            except ExcelFileUnavailableError as e:
                message = GlobalTranslate._(e.error_window_message_key)
                title = GlobalTranslate._(e.error_window_title_key)
                NotificationWindow("{0}:\n{1}".format(message, e.file_path), title)

        project.saved_objects_lists = []
        ProjectFileManager.add_project_files_to_file(project=project)

    @classmethod
    def load_and_validate_document(cls, doc_list):
        error_set: set[dict] = set()
        objects_lists = []
        global_vars.single_project.saved_objects_lists = []

        for doc in doc_list:
            if Path(doc).suffix in ['.xls', '.xlsx']:
                temp_path = InsertDataDomain.start_excel_changes(doc=doc)
            elif Path(doc).suffix == '.csv':
                temp_path = Path(doc)

            try:
                asset = InsertDataDomain.check_document(doc_location=temp_path)
                ProjectFileManager.add_template_file_to_project(Path(doc))
                objects_lists.append(asset)
            except Exception as ex:
                error_set.add({"exception": ex, "path_str": doc})
            else:
                InsertDataDomain.add_template_file_to_project(project=global_vars.single_project,
                                                              filepath=Path(doc),
                                                              state=FileState.OK)

        ProjectFileManager.add_project_files_to_file(global_vars.single_project)

        objects_in_memory = cls.flatten_list(objects_lists)

        global_vars.otl_wizard.main_window.step3_visuals.create_html(objects_in_memory)
        RelationChangeDomain.set_objects(objects_in_memory)

        return error_set, objects_lists

    @classmethod
    def flatten_list(cls, objects_lists):
        objects_in_memory: List[AIMObject] = []
        for objects_list in objects_lists:
            objects_in_memory.extend(objects_list)
        return objects_in_memory