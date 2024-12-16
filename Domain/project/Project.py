import datetime
import json
import logging
import os
import shutil
from pathlib import Path
from typing import Optional, Union, cast

from Domain.database.ModelBuilder import ModelBuilder
from Domain.project.ProjectFile import ProjectFile
from Domain.enums import FileState
from Domain.project.ProgramFileStructure import ProgramFileStructure
from Exceptions.ExcelFileUnavailableError import ExcelFileUnavailableError
from GUI.dialog_windows.NotificationWindow import NotificationWindow
from GUI.translation.GlobalTranslate import GlobalTranslate


class Project:
    saved_documents_filename = "saved_documents.json"

    def __init__(self, project_path: Path = None, subset_path: Path = None, assets_path: Path = None,
                 eigen_referentie: str = None, bestek: str = None, laatst_bewerkt: datetime.datetime = None,
                 last_quick_save:Optional[Path] = None, subset_operator: Optional[Union[str,Path]] = None,otl_version: Optional[Union[str,Path]] = None):
        self.project_path: Path = project_path
        self.subset_path: Path = subset_path
        if isinstance(subset_operator,Path):
            subset_operator = subset_operator.stem
        self.subset_operator: Optional[str] = subset_operator
        if isinstance(otl_version,Path):
            otl_version = otl_version.stem
        self.otl_version: Optional[str] = otl_version

        if assets_path:
            if ".json" in str(assets_path.absolute()):
                self.assets_path: Path = assets_path
            else:
                self.assets_path: Path = assets_path / self.saved_documents_filename
        elif self.project_path is not None:
            self.assets_path = self.project_path / self.saved_documents_filename
        else:
            self.assets_path = None

        if last_quick_save:
            self.last_quick_save:Path = self.get_quicksaves_dir_path() / last_quick_save.name
        else:
            self.last_quick_save = None

        self.eigen_referentie: str = eigen_referentie
        self.bestek: str = bestek
        self.laatst_bewerkt: datetime.datetime = laatst_bewerkt

        self.assets_in_memory = []

        self.saved_project_files: list[ProjectFile] = []
        self.model_builder = None


    @classmethod
    def load_project(cls, project_path: Path = None):
        if not project_path.exists():
            raise FileNotFoundError(f"Project dir {project_path} does not exist")

        project_details_file = project_path / 'project_details.json'
        if not project_details_file.exists():
            raise FileNotFoundError(f"Project details file {project_details_file} does not exist")

        with open(project_details_file) as json_file:
            project_details = json.load(json_file)

        if 'last_quick_save' not in project_details or not project_details['last_quick_save']:
            last_quick_save = None
        else:
            last_quick_save = Path(project_path / "quick_saves") / Path(project_details['last_quick_save'])


        if 'subset_operator' not in project_details or not project_details['subset_operator']:
            subset_operator = None
        else:
            subset_operator = project_details['subset_operator']

        if 'otl_version' not in project_details or not project_details['otl_version']:
            otl_version = None
        else:
            otl_version = project_details['otl_version']

        return cls(project_path,
                   project_path / project_details['subset'],
                   project_path,
                   project_details['eigen_referentie'],
                   project_details['bestek'],
                   datetime.datetime.strptime(project_details['laatst_bewerkt'], "%Y-%m-%d %H:%M:%S"),
                   last_quick_save,
                   subset_operator=subset_operator,
                   otl_version=otl_version)

    def get_subset_db_name(self):
        return  str(self.subset_path.name)

    def load_model_builder(self) -> ModelBuilder:
        if not self.model_builder and self.subset_path:
            self.model_builder = ModelBuilder(self.subset_path)
        return self.model_builder

    def clear_model_builder_from_memory(self) -> None:
        self.model_builder = None

    def get_operator_name(self):
        if not self.subset_operator:
            subset_operator = self.load_model_builder().get_operator_name()
            if isinstance(subset_operator,Path):
                self.subset_operator = cast(Path,subset_operator).stem()
            else:
                self.subset_operator = subset_operator
        return self.subset_operator

    def get_otl_version(self):
        if not self.otl_version:
            self.otl_version = self.load_model_builder().get_otl_version()

        return self.otl_version

    def load_saved_document_filenames(self):

        project_dir_path = ProgramFileStructure.get_otl_wizard_projects_dir() / self.project_path.name
        saved_documents_path: Path = project_dir_path / Project.saved_documents_filename
        if saved_documents_path.exists():
            with open(saved_documents_path, "r") as saved_document:
                saved_documents = json.load(saved_document)
            logging.debug(f"Loaded saved object lists: {str(saved_documents)}")
            self.saved_project_files = []
            for document in saved_documents:

                # if document was validated but there is no quicksave then set it to warning
                state = FileState(document['state'])
                quick_save_path = self.get_quicksaves_dir_path()
                if (state == FileState.OK and
                    not (quick_save_path.exists() and
                     len(list(os.listdir(quick_save_path))))):
                    state = FileState.WARNING

                file = ProjectFile(
                    file_path= self.get_OTL_template_files_dir_path() / Path(document['file_path']).name ,
                    state=state)
                self.saved_project_files.append(file)

        return self

    def get_quicksaves_dir_path(self):
        quick_saves = Path(self.project_path / "quick_saves")
        if not quick_saves.exists():
            os.mkdir(Path(self.project_path / "quick_saves"))
        return quick_saves

    def get_last_quick_save_path(self) -> Optional[Path]:
        path = None
        quick_save_path_dir = self.get_quicksaves_dir_path()
        if self.last_quick_save and self.last_quick_save.exists():
            path = self.last_quick_save
        elif quick_save_path_dir.exists():
            file_list = sorted(os.listdir(quick_save_path_dir), reverse=True)
            if file_list:
                path = Path(quick_save_path_dir, file_list[0])
        return path

    def save_project_filepaths_to_file(self) -> None:

        otl_wizard_project_dir = ProgramFileStructure.get_otl_wizard_projects_dir()
        object_array = []
        for objects_list in self.saved_project_files:
            objects_list_details = {
                'file_path': str(objects_list.file_path.name),
                'state': objects_list.state.value
            }
            object_array.append(objects_list_details)
        project_dir_path = otl_wizard_project_dir / self.project_path.name
        with open(project_dir_path / self.saved_documents_filename, "w") as project_details_file:
            json.dump(object_array, project_details_file)

    def is_in_project(self, file_path) -> ProjectFile:
        matches = [project_file for project_file in self.saved_project_files if
         project_file.file_path == file_path]
        return  matches[0] if matches else None

    def get_saved_projectfiles(self):
        return self.saved_project_files

    def add_saved_project_file(self, file_path: Path | str, state: FileState):
        if isinstance(file_path,str):
            file_path = Path(file_path)

        full_file_path = self.get_OTL_template_files_dir_path() / file_path.name
        self.saved_project_files.append(ProjectFile(file_path=full_file_path, state=state))
        self.save_project_filepaths_to_file()


    def make_copy_of_added_file(self, filepath: Path) -> Path:

        location_dir = self.get_OTL_template_files_dir_path()
        if not location_dir.exists():
            location_dir.mkdir()
        doc_name = filepath.name
        end_location = location_dir / doc_name
        if end_location == filepath:
            return end_location
        shutil.copy(filepath, end_location)
        logging.debug(f"Created a copy of the template file {filepath.name} in the project folder")
        return end_location

    def get_OTL_template_files_dir_path(self):
        return self.project_path / 'OTL-template-files'

    def remove_all_project_files(self):
        logging.debug("memory contains %s",
                      self.saved_project_files)
        for file in self.saved_project_files:
            logging.debug("starting to delete file %s",
                          file.file_path)
            try:
                self._delete_project_file(file_path=file.file_path)
            except ExcelFileUnavailableError as e:
                message = GlobalTranslate._(e.error_window_message_key)
                title = GlobalTranslate._(e.error_window_title_key)
                NotificationWindow("{0}:\n{1}".format(message, e.file_path), title)

        self.saved_project_files = []
        self.save_project_filepaths_to_file()


    def remove_project_file(self, file_path) -> bool:
        project_file = self.is_in_project(file_path)
        res = False
        if project_file:
            if project_file.file_path.exists():
                res =  self._delete_project_file(project_file.file_path)
            else:
                res = True

            if res:
                self.saved_project_files.remove(project_file)
                self.save_project_filepaths_to_file()
        return res

    def _delete_project_file(self, file_path) -> bool:
        try:
            logging.debug(f"file path = {str(file_path)}")
            Path(file_path).unlink()
            return True
        except FileNotFoundError as e:
            logging.error(e)
            return False
        except PermissionError as e:
            logging.error(e)
            raise ExcelFileUnavailableError(file_path=file_path, exception=e)

    def change_subset(self, new_path: Path):
        self.clear_model_builder_from_memory()
        self.subset_path = new_path
        self.model_builder = self.load_model_builder()
        self.subset_operator = None
        self.otl_version = None
