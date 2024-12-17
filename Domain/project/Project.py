import datetime
import json
import logging
import os
import shutil
import zipfile
from pathlib import Path
from typing import Optional, Union, cast, Self

from otlmow_converter.OtlmowConverter import OtlmowConverter
from otlmow_model.OtlmowModel.Classes.ImplementatieElement.AIMObject import AIMObject

from Domain import global_vars
from Domain.database.ModelBuilder import ModelBuilder
from Domain.project.ProjectFile import ProjectFile
from Domain.enums import FileState
from Domain.project.ProgramFileStructure import ProgramFileStructure
from Exceptions.ExcelFileUnavailableError import ExcelFileUnavailableError


class Project:
    """
    Normal Project Structure:
    │   <self.eigen_referentie>                 : folder
    │   │   project_details.json                : json-file
    │   │   saved_documents.json                : json-file
    │   │   <self.subset_path.name>.db                    : sqlite file
    │   ├───project-files                       : folder
    │   │       <saved_project_files[0]>.xlsx   : xlsx,json,geojson,csv file
    │   └───quick_saves                         : folder
    │           quick_save-<date>_<time>.json   : json-file
    """

    project_details_filename = 'project_details.json'
    saved_documents_filename = "saved_documents.json"
    project_files_foldername = 'project_files'
    old_project_files_foldername = 'OTL-template-files' # for legacy compatibility
    quick_saves_foldername =  "quick_saves"

    max_days_quicksave_stored = 7

    def __init__(self, project_path: Path = None, 
                 subset_path: Path = None, 
                 saved_documents_overview_path: Path = None, 
                 eigen_referentie: str = None, 
                 bestek: str = None,
                 laatst_bewerkt: datetime.datetime = None,
                 last_quick_save:Optional[Path] = None, 
                 subset_operator: Optional[Union[str,Path]] = None, 
                 otl_version: Optional[Union[str,Path]] = None):
        
        self.project_path: Path = project_path
        self.subset_path: Path = subset_path
        
        if isinstance(subset_operator,Path):
            subset_operator = subset_operator.stem
        self.subset_operator: Optional[str] = subset_operator
        
        if isinstance(otl_version,Path):
            otl_version = otl_version.stem
        self.otl_version: Optional[str] = otl_version

        if saved_documents_overview_path:
            if ".json" in str(saved_documents_overview_path.absolute()):
                self.saved_documents_overview_path: Path = saved_documents_overview_path
            else:
                self.saved_documents_overview_path: Path = saved_documents_overview_path / self.saved_documents_filename
        elif self.project_path is not None:
            self.saved_documents_overview_path = self.project_path / self.saved_documents_filename
        else:
            self.saved_documents_overview_path = None

        if last_quick_save:
            self.last_quick_save:Path = self.get_quicksaves_dir_path() / last_quick_save.name
        else:
            self.last_quick_save = None

        if self.project_path:
            self.quick_save_dir_path = Path(self.project_path / self.quick_saves_foldername)
        else:
            self.quick_save_dir_path = None

        self.eigen_referentie: str = eigen_referentie
        self.bestek: str = bestek
        self.laatst_bewerkt: datetime.datetime = laatst_bewerkt

        self.assets_in_memory = []

        self.saved_project_files: list[ProjectFile] = []
        self.model_builder = None


    @classmethod
    def load_project(cls, project_path: Path = None)-> Self:
        """
        Loads a project from a specified directory by reading its details from a JSON file.
        It validates the existence of the project directory and the required project details file before extracting and returning the project information.

        Args:
            project_path (Path, optional): The path to the project directory. Defaults to None.

        Returns:
            Project: An instance of the project class initialized with the loaded details.

        Raises:
            FileNotFoundError: If the project directory or the project details file does not exist.
        """

        if project_path and not project_path.exists():
            raise FileNotFoundError(f"Project dir {project_path} does not exist")

        project_details_file = project_path / cls.project_details_filename
        if not project_details_file.exists():
            raise FileNotFoundError(f"Project details file {project_details_file} does not exist")

        with open(project_details_file) as json_file:
            project_details = json.load(json_file)

        if 'last_quick_save' not in project_details or not project_details['last_quick_save']:
            last_quick_save = None
        else:
            last_quick_save = Path(project_path / cls.quick_saves_foldername) / Path(project_details['last_quick_save'])


        if 'subset_operator' not in project_details or not project_details['subset_operator']:
            subset_operator = None
        else:
            subset_operator = project_details['subset_operator']

        if 'otl_version' not in project_details or not project_details['otl_version']:
            otl_version = None
        else:
            otl_version = project_details['otl_version']

        return cls(project_path=project_path,
                   subset_path=project_path / project_details['subset'],
                   saved_documents_overview_path= Path(project_path,  cls.saved_documents_filename),
                   eigen_referentie=project_details['eigen_referentie'],
                   bestek=project_details['bestek'],
                   laatst_bewerkt=datetime.datetime.strptime(project_details['laatst_bewerkt'], "%Y-%m-%d %H:%M:%S"),
                   last_quick_save=last_quick_save,
                   subset_operator=subset_operator,
                   otl_version=otl_version)


    def save_project_to_dir(self) -> None:
        """
        Saves the current project to a designated directory,
        including project details and any associated subset files.
        This function ensures that the project directory is created if it does not exist and
        updates the last modified timestamp if necessary.

        Args:
            self: The instance of the class containing project details.

        Returns:
            None

        Raises:
            OSError: If there is an error creating the directory or writing the project details file.

        Examples:
            project.save_project_to_dir()
        """

        otl_wizard_project_dir = ProgramFileStructure.get_otl_wizard_projects_dir()
        project_dir_path = otl_wizard_project_dir / self.project_path.name
        logging.debug("Saving project to %s", project_dir_path)
        project_dir_path.mkdir(exist_ok=True, parents=True)

        self.save_project_details(project_dir_path=project_dir_path)

        if self.subset_path.parent.absolute() != project_dir_path.absolute():
            # move subset to project dir
            new_subset_path = project_dir_path / self.subset_path.name
            shutil.copy(src=self.subset_path, dst=new_subset_path)

    def save_project_details(self, project_dir_path: Path) -> None:
        """
        Saves the project's details to a specified directory in JSON format.
        This function constructs a dictionary of project attributes and writes it to a file,
        updating the last modified timestamp if necessary.

        Args:
            self: The instance of the class managing the project.
            project_dir_path (Path): The directory path where the project details will be saved.

        Returns:
            None

        Raises:
            OSError: If there is an error writing the project details file.

        Examples:
            project.save_project_details(Path('/path/to/project'))
        """

        last_quick_save_name = None
        if self.last_quick_save:
            last_quick_save_name = str(self.last_quick_save.name)

        if not self.laatst_bewerkt:
            self.laatst_bewerkt = datetime.datetime.now()

        project_details_dict = {
            'bestek': self.bestek,
            'eigen_referentie': self.eigen_referentie,
            'laatst_bewerkt': self.laatst_bewerkt.strftime("%Y-%m-%d %H:%M:%S"),
            'subset': self.subset_path.name,
            'subset_operator': self.get_operator_name(),
            'otl_version': self.get_otl_version(),
            'last_quick_save': last_quick_save_name
        }

        with open(project_dir_path / self.project_details_filename, "w") as project_details_file:
            json.dump(project_details_dict, project_details_file)

    def load_validated_assets(self) -> list[AIMObject]:
        # sourcery skip: use-named-expression
        """
        Loads validated assets from the most recent quick save file.
        If a valid quick save path is found, it converts the file contents into a list of AIMObject
        instances; otherwise, it returns an empty list.

        Args:
            self: The instance of the class managing asset loading.

        Returns:
            list[AIMObject]: A list of validated AIMObject instances loaded from the quick save file, or an empty list if no valid path is found.

        Examples:
            assets = project.load_validated_assets()
        """

        path = self.get_last_quick_save_path()

        if path:
            return cast(typ=list[AIMObject],val=list(OtlmowConverter.from_file_to_objects(path)))

        return []

    def save_validated_assets(self) -> None:
        """
        Saves validated assets the project to the quick save directory.
        It manages the quick save files by removing old saves and generating a new save file with
        a unique name.

        the format of the save file is: quick_save_{date}_{time}.json:
            date:   the date on which the quicksave was made in format yymmdd
            time:   the tie on which the quicksave was made in format HHMMSS

        All quicksaves that are more than set days old (default= 7) are deleted in this function

        Args:

        Returns:
            None

        Raises:
            OSError: If there is an issue creating the quick save directory or saving the file.

        """
        date_format = "%y%m%d_%H%M%S"
        

        if self.quick_save_dir_path.exists():
            current_date = datetime.datetime.now()

            self.remove_too_old_quicksaves(current_date=current_date,
                                          max_days_stored=self.max_days_quicksave_stored,
                                          date_format=date_format)
        else:
            os.mkdir(self.quick_save_dir_path )

        current_date_str = datetime.datetime.now().strftime(date_format)

        save_path = self.quick_save_dir_path  / f"quick_save-{current_date_str}.json"
        OtlmowConverter.from_objects_to_file(file_path=save_path,
                                             sequence_of_objects=self.assets_in_memory)
        self.last_quick_save = save_path

        self.save_project_to_dir()


    def remove_too_old_quicksaves(self, current_date: datetime, max_days_stored: datetime,
                                   date_format: str) -> None:
        """
        Removes quick save files that are older than a specified number of days.
        This function checks the modification dates of the quick save files and deletes those
        that exceed the maximum age defined by the user.

        Files that do not adhere to the standard naming convention are never deleted

        Args:
            self: The instance of the class managing quick saves.
            current_date (datetime): The current date used to compare against quick save file dates.
            max_days_stored (datetime): The maximum number of days to retain quick save files.
            date_format (str): The format used to parse the date from the filename.

        Returns:
            None

        Examples:
            project.remove_too_old_quicksaves(datetime.now(), 30, "%Y-%m-%d")
        """

        files = os.listdir(path=self.quick_save_dir_path )
        for filename in files:
            try:
                file_date = datetime.datetime.strptime(filename.split("-")[-1].split(".json")[0],
                                                       date_format)
            except ValueError:
                # if the save file doesn't adhere to standard naming convention it is never deleted
                file_date = current_date

            days_ago = (current_date - file_date).days
            if days_ago > max_days_stored:
                file_to_remove_path = Path(self.quick_save_dir_path , filename)
                os.remove(file_to_remove_path)


    def export_project_to_file(self, file_path: Path) -> None:
        with zipfile.ZipFile(file=file_path, mode='w') as project_zip:
            project_zip.write(self.project_path / self.project_details_filename,
                              arcname=self.project_details_filename,
                              compresslevel=zipfile.ZIP_DEFLATED)
            if self.saved_documents_overview_path and self.saved_documents_overview_path.exists():
                project_zip.write(self.saved_documents_overview_path,
                                  arcname=self.saved_documents_overview_path.name)
            project_zip.write(self.subset_path, arcname=self.subset_path.name)

            if not self.get_saved_projectfiles():
                self.load_saved_document_filenames()

            for document in self.get_saved_projectfiles():
                file_zip_path = Path() / document.file_path.name
                project_zip.write(document.file_path, arcname=file_zip_path)

            last_quick_save_path = self.get_last_quick_save_path()
            if last_quick_save_path and last_quick_save_path.exists():
                last_quick_save_zip_path = Path(self.quick_saves_foldername) / last_quick_save_path.name
                project_zip.write(last_quick_save_path, arcname=last_quick_save_zip_path)

    @classmethod
    def import_project(cls, file_path: Path) -> Self:
        with zipfile.ZipFile(file=file_path) as project_file:

            # TODO: handle if project doesn't contain project_details.json files
            project_details = json.load(fp=project_file.open(cls.project_details_filename))

            project_dir_path = Path(
                ProgramFileStructure.get_otl_wizard_projects_dir() / project_details[
                    'eigen_referentie'])
            try:
                project_dir_path.mkdir(exist_ok=False, parents=True)
            except FileExistsError as ex:
                # TODO: warning user with dialog window when the project already exists
                logging.error("Project dir %s already exists", project_dir_path)
                raise ex

            project_file.extractall(path=project_dir_path)

        return Project.load_project(project_path=project_dir_path)

    def delete_project_dir_by_path(self) -> None:
        """
            To Project.py without file_path
        """
        logging.debug("Deleting project %s", self.project_path)
        shutil.rmtree(path=self.project_path)
        # ProjectFileManager.load_projects_into_global()


    def are_all_project_files_in_memory_valid(self) -> bool:

        logging.debug("Started searching for project files in memory that are OTL conform")

        if not self.saved_project_files:
            logging.debug("No project files in memory")
            return False
        return any(
            template.state == FileState.OK for template in self.saved_project_files
        )

    def get_subset_db_name(self) -> str:
        """
        Retrieves the name of the subset database associated with the project.
        This function returns the name of the subset path as a string.

        Returns:
            str: The name of the subset database.
        """

        return  str(self.subset_path.name)

    def get_model_builder(self) -> ModelBuilder:
        """
        Loads and initializes the model builder associated with the project if it has not been created yet.
        This function checks if the model builder is already set and creates a new instance using the subset path if necessary.

        Returns:
            ModelBuilder: The model builder instance associated with the project.

        Raises:
            ValueError: If the subset path is not set when attempting to create the model builder.
        """

        if not self.model_builder and self.subset_path:
            self.model_builder = ModelBuilder(self.subset_path)
        return self.model_builder

    def clear_model_builder_from_memory(self) -> None:
        """
        Clears the model builder from memory by setting it to None.
        This function effectively releases the reference to the current model builder, allowing for garbage collection.

        Returns:
            None
        """

        self.model_builder = None

    def get_operator_name(self) -> str:
        """
        Retrieves the name of the subset operator associated with the project.
        If the subset operator is not already set, it fetches the operator name from the model builder and processes it accordingly.

        Returns:
            str: The name of the subset operator.

        Raises:
            ValueError: If the operator name cannot be determined from the model builder.
        """

        if not self.subset_operator:
            subset_operator = self.get_model_builder().get_operator_name()
            if isinstance(subset_operator,Path):
                self.subset_operator = cast(Path,subset_operator).stem
            else:
                self.subset_operator = subset_operator
        return self.subset_operator

    def get_otl_version(self) -> str:
        """
        Retrieves the OTL (Object Type Library) version associated with the project.
        If the OTL version is not already set, it fetches the version from the model builder.

        Returns:
            str: The OTL version.

        Raises:
            ValueError: If the OTL version cannot be determined from the model builder.
        """

        if not self.otl_version:
            self.otl_version = self.get_model_builder().get_otl_version()

        return self.otl_version

    def load_saved_document_filenames(self) -> Self:
        """
        Loads the filenames of saved documents associated with the project from a specified directory.
        This function checks for the existence of a saved documents file, reads its contents, and populates the list of saved project files with their saved states.
        If there are no quicksaves yet then the states are set to FileState.WARNING

        Returns:
            self: The instance of the class, allowing for method chaining.

        Raises:
            FileNotFoundError: If the saved documents file does not exist.
            json.JSONDecodeError: If the saved documents file contains invalid JSON.
        """

        project_dir_path = ProgramFileStructure.get_otl_wizard_projects_dir() / self.project_path.name
        saved_documents_path: Path = project_dir_path / Project.saved_documents_filename
        if saved_documents_path.exists():
            with open(file=saved_documents_path,mode="r") as saved_document:
                saved_documents = json.load(fp=saved_document)
            logging.debug(f"Loaded saved object lists: {str(saved_documents)}")
            self.saved_project_files = []

            location_dir = self.get_project_files_dir_path()

            #copy all files from the old OTL-Template-files folder to the new folder
            if not location_dir.exists():
                location_dir.mkdir()

            old_path = self.get_old_project_files_dir_path()
            if old_path.exists():
                for location, dirs, files in os.walk(old_path):
                    for file in files:
                        old_location = Path(location, file)
                        new_location = Path(location_dir , file)
                        shutil.copyfile(old_location, new_location)
                        os.remove(old_location)
                old_path.rmdir()

            for document in saved_documents:
                # if document was validated but there is no quicksave then set it to warning
                state = FileState(document['state'])
                quick_save_path = self.get_quicksaves_dir_path()
                if (state == FileState.OK and
                    not (quick_save_path.exists() and
                     len(list(os.listdir(path=quick_save_path))))):
                    state = FileState.WARNING

                file = ProjectFile(
                    file_path=location_dir / Path(document['file_path']).name ,
                    state=state)
                self.saved_project_files.append(file)

        return self

    def get_quicksaves_dir_path(self) -> Path:
        """
        Retrieves the path to the quick saves directory for the project.
        If the directory does not exist, it creates it before returning the path.

        Returns:
            Path: The path to the quick saves directory.

        Raises:
            OSError: If the directory cannot be created due to a file system error.
        """

        quick_saves = Path(self.project_path / self.quick_saves_foldername)
        if not quick_saves.exists():
            os.mkdir(Path(self.project_path / self.quick_saves_foldername))
        return quick_saves

    def get_last_quick_save_path(self) -> Optional[Path]:
        # sourcery skip: use-named-expression
        """
        Retrieves the path to the last quick save file for the project.
        It first checks if there is a specific last quick save path and if that exists; if not,
        it looks for the most recent file in the quick saves directory.

        Returns:
            Optional[Path]: The path to the last quick save file, or None if no quick save exists.

        Raises:
            OSError: If there is an issue accessing the quick saves directory.
        """
        path = None
        quick_save_path_dir = self.get_quicksaves_dir_path()
        if self.last_quick_save and self.last_quick_save.exists():
            path = self.last_quick_save
        elif quick_save_path_dir.exists():
            file_list = sorted(os.listdir(quick_save_path_dir), reverse=True)
            if file_list:
                path = Path(quick_save_path_dir, file_list[0])
        return path

    def get_project_files_dir_path(self) -> Path:
        """
        Retrieves the directory path for the project's files. This function constructs and
        returns the full path to the folder designated for storing project files.

        Args:
            self: The instance of the class managing the project.

        Returns:
            Path: The path to the project files directory.

        Examples:
            files_dir = project.get_project_files_dir_path()
        """

        return self.project_path / self.project_files_foldername

    def get_old_project_files_dir_path(self) -> Path:
        """
        Retrieves the directory path for the old project's files. This function constructs and
        returns the full path to the folder designated for storing project files in project made
        with an old version of OTL wizard.

        Args:
            self: The instance of the class managing the project.

        Returns:
            Path: The path to the old project files directory.

        Examples:
            old_files_dir = project.get_old_project_files_dir_path()
        """

        return self.project_path / self.old_project_files_foldername

    def delete_template_folder(self) -> None:

        logging.debug(f"Started clearing out the whole template folder of "
                      f"project: {self.eigen_referentie}")
        new_project_files_folder = self.get_project_files_dir_path()
        old_project_files_folder = self.get_old_project_files_dir_path()

        if old_project_files_folder.exists():
            shutil.rmtree(path=old_project_files_folder)

        if new_project_files_folder.exists():
            shutil.rmtree(path=new_project_files_folder)

        logging.debug("Finished clearing out the whole template folder")

    def save_project_filepaths_to_file(self) -> None:
        """
        Saves the file paths and states of the project's saved files to a JSON file.
        This function constructs a list of saved project file details and writes them to a
        specified file within the project's directory.
        It will overwrite the existing saved_documents.json

        Returns:
            None

        Raises:
            OSError: If there is an issue writing to the file or accessing the project directory.
        """

        otl_wizard_project_dir = ProgramFileStructure.get_otl_wizard_projects_dir()
        object_array = []
        for objects_list in self.saved_project_files:
            objects_list_details = {
                'file_path': str(objects_list.file_path.name),
                'state': objects_list.state.value
            }
            object_array.append(objects_list_details)
        project_dir_path = otl_wizard_project_dir / self.project_path.name
        with open(file=project_dir_path / self.saved_documents_filename, mode="w") as project_details_file:
            json.dump(object_array, project_details_file)

    def is_in_project(self, file_path) -> ProjectFile:
        """
        Checks if a specified file path is present in the project's saved files.
        This function searches through the list of saved project files and returns the matching
        project file if found, or None if no match exists.

        Args:
            file_path (Path): The path of the file to check for in the project's saved files.

        Returns:
            ProjectFile: The matching project file if found, or None if not.

        Raises:
            TypeError: If the provided file_path is not of the expected type.
        """

        matches = [project_file for project_file in self.saved_project_files if
         project_file.file_path == file_path]
        return  matches[0] if matches else None

    def get_saved_projectfiles(self) -> list[ProjectFile]:
        """
        Retrieves the list of saved project files associated with the project.
        This function returns the current state of the saved project files as a list of ProjectFile instances.

        Returns:
            list[ProjectFile]: A list containing the saved project files.
        """

        return self.saved_project_files

    def copy_and_add_project_file(self, file_path: Path | str, state: FileState) -> None:
        """
        Adds a saved project file to the list of saved project files, makes a copy of it and
        updates its state.
        This function converts the file path to a Path object if it is provided as a string,
        constructs the full file path, and appends a new ProjectFile instance to the saved project files.

        Args:
            file_path (Path | str): The path of the file to be saved, which can be a string or a Path object.
            state (FileState): The state of the project file to be saved.

        Returns:
            None

        Raises:
            ValueError: If the provided file_path is invalid or if the state is not a valid FileState.
        """

        if isinstance(file_path,str):
            file_path = Path(file_path)

        location_dir = self.get_project_files_dir_path()
        if not location_dir.exists():
            old_path = self.get_old_project_files_dir_path()
            if old_path.exists():
                location_dir = old_path
            else:
                return

        full_file_path = location_dir / file_path.name
        end_location = self.make_copy_of_added_file(filepath=full_file_path)
        self.saved_project_files.append(ProjectFile(file_path=end_location, state=state))
        self.save_project_filepaths_to_file()


    def make_copy_of_added_file(self, filepath: Path) -> Path:
        """
        Creates a copy of the specified file in the OTL template files directory.
        This function ensures the destination directory exists,
        copies the file if it is not already in the target location,
        and returns the path to the copied file.

        Args:
            filepath (Path): The path of the file to be copied.

        Returns:
            Path: The path to the copied file in the OTL template files directory.

        Raises:
            FileNotFoundError: If the specified file does not exist.
            OSError: If there is an issue creating the directory or copying the file.
        """

        location_dir = self.get_project_files_dir_path()
        if not location_dir.exists():
            old_path = self.get_old_project_files_dir_path()
            if old_path.exists():
                location_dir = old_path
            else:
                location_dir.mkdir()

        doc_name = filepath.name
        end_location = location_dir / doc_name
        if end_location == filepath:
            return end_location
        shutil.copy(src=filepath, dst=end_location)
        logging.debug(f"Created a copy of the template file {filepath.name} in the project folder")
        return end_location


    def remove_all_project_files(self):
        """
        Removes all project files from memory and deletes them from the file system.
        This function iterates through the list of saved project files,
        attempts to delete each one, and handles any errors that occur during the deletion process.

        Creates a notification window to user if the program doesn't have access to file

        empty saved_project_files list is saved to saved_document.json after whole process

        Returns:
            None

        Raises:
            ExcelFileUnavailableError: If a file cannot be deleted due to its unavailability.
        """

        logging.debug("memory contains %s", self.saved_project_files)
        for file in self.saved_project_files:
            logging.debug("starting to delete file %s",file.file_path)
            try:
                self._delete_project_file(file_path=file.file_path)
            except ExcelFileUnavailableError as e:
                # TODO: make a call here to GUI to create this dialogwindow
                global_vars.otl_wizard.main_window.notify_user_of_excel_file_unavailable_error(e)

        self.saved_project_files = []
        self.save_project_filepaths_to_file()


    def remove_project_file(self, file_path) -> bool:
        """
        Removes a specified project file from the list of saved project files and deletes it from
        the file system if it exists.
        This function checks if the file is part of the project, attempts to delete it, and updates
        the saved project files accordingly.

        Args:
            file_path (Path | str): The path of the project file to be removed.

        Returns:
            bool: True if the file was successfully removed, False otherwise.

        Raises:
            ExcelFileUnavailableError: If the file cannot be deleted due to its unavailability.
        """

        project_file = self.is_in_project(file_path=file_path)
        res = False
        if project_file:
            if project_file.file_path.exists():
                try:
                    res =  self._delete_project_file(file_path=project_file.file_path)
                except ExcelFileUnavailableError as e:
                    #TODO: make a call here to GUI to create this dialogwindow
                    global_vars.otl_wizard.main_window.notify_user_of_excel_file_unavailable_error(e)
            else:
                res = True

            if res:
                self.saved_project_files.remove(project_file)
                self.save_project_filepaths_to_file()
        return res

    @staticmethod
    def _delete_project_file(file_path) -> bool:
        """
        Deletes a specified project file from the file system.
        This function attempts to unlink the file at the given path and
        handles some errors that may occur during the deletion process.

        Needs following calls after calling this one
            self.saved_project_files.remove(project_file)
            self.save_project_filepaths_to_file()

        Args:
            file_path (Path | str): The path of the project file to be deleted.

        Returns:
            bool: True if the file was successfully deleted, False if the file was not found.

        Raises:
            ExcelFileUnavailableError: If there is a permission error while attempting to delete the file.
        """

        try:
            logging.debug(f"file path = {str(file_path)}")
            Path(file_path).unlink()
            return True
        except FileNotFoundError as e:
            logging.error(e)
            return False
        except PermissionError as e:
            #TODO: make other errors + dialog windows for cases with non-excel files if necessary
            logging.error(e)
            raise ExcelFileUnavailableError(file_path=file_path, exception=e) from e

    def change_subset(self, new_path: Path) -> None:
        """
        Changes the current subset path for the project and resets related properties.
        This function clears the model builder from memory, updates the subset path,
        ,loads a new model builder and resets subset operator, and OTL version to their initial states.

        Args:
            new_path (Path): The new path to set as the subset for the project.

        Returns:
            None
        """

        self.clear_model_builder_from_memory()
        self.subset_path = new_path
        self.model_builder = self.get_model_builder()
        self.subset_operator = None
        self.otl_version = None
        self.save_project_to_dir()
