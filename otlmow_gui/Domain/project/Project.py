from __future__ import annotations

import datetime
import json
import os
import shutil
import zipfile
from collections import defaultdict
from pathlib import Path
from typing import Optional, Union, cast

from otlmow_model.OtlmowModel.BaseClasses.RelationInteractor import RelationInteractor
from otlmow_model.OtlmowModel.Classes.ImplementatieElement.AIMObject import AIMObject
from otlmow_model.OtlmowModel.Classes.ImplementatieElement.RelatieObject import RelatieObject
from otlmow_visuals.PyVisWrapper import PyVisWrapper

from otlmow_gui.Domain import global_vars
from otlmow_gui.Domain.util.Helpers import Helpers
from otlmow_gui.Domain.database.ModelBuilder import ModelBuilder
from otlmow_gui.Domain.logger.OTLLogger import OTLLogger
from otlmow_gui.Domain.project.ProjectFile import ProjectFile
from otlmow_gui.Domain.enums import FileState
from otlmow_gui.Domain.ProgramFileStructure import ProgramFileStructure
from otlmow_gui.Domain.util.VisualisationStateTracker import VisualisationStateTracker
from otlmow_gui.Exceptions.ExcelFileUnavailableError import ExcelFileUnavailableError
from otlmow_gui.GUI.dialog_windows.LoadingImageWindow import add_loading_screen
from otlmow_gui.GUI.dialog_windows.NotificationWindow import NotificationWindow
from otlmow_gui.GUI.dialog_windows.ProjectExistsError import ProjectExistsError
from otlmow_gui.GUI.dialog_windows.YesOrNoNotificationWindow import YesOrNoNotificationWindow
from otlmow_gui.GUI.translation.GlobalTranslate import GlobalTranslate
from otlmow_gui.exception_handler.ExceptionHandlers import create_task_reraise_exception


class Project:
    """
    Normal Project Structure:
    │   <self.eigen_referentie>                 : folder
    │   │   project_details.json                : json-file
    │   │   saved_documents.json                : json-file
    │   │   <self.subset_path_name>.db          : sqlite file
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
    visualisation_foldername = "visuals"
    visualisation_filename = "graph_visualisation.html"
    visualisation_python_support_data_filename = "visuals_python_support_data.json"

    max_days_quicksave_stored = 7
    quicksave_date_format = "%y%m%d_%H%M%S"

    def __init__(self, eigen_referentie: str, project_path: Path = None, subset_path: Path = None,
                 saved_documents_overview_path: Path = None, bestek: str = None,
                 laatst_bewerkt: datetime.datetime = None, last_quick_save: Optional[Path] = None,
                 subset_operator: Optional[Union[str, Path]] = None,
                 otl_version: Optional[Union[str, Path]] = None):

        self.project_path: Path = project_path
        if not self.project_path:
            self.project_path = Path(
                ProgramFileStructure.get_otl_wizard_projects_dir() / eigen_referentie)

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
        else:
            self.saved_documents_overview_path = self.project_path / self.saved_documents_filename

        self.quick_save_dir_path = Path(self.project_path / self.quick_saves_foldername)

        if last_quick_save:
            self.last_quick_save:Path = self.get_quicksaves_dir_path() / last_quick_save.name
        else:
            self.last_quick_save = None

        self.eigen_referentie: str = eigen_referentie
        self.bestek: str = bestek
        self.laatst_bewerkt: datetime.datetime = laatst_bewerkt

        self.assets_in_memory:list[Union[RelatieObject, RelationInteractor]] = []

        self.saved_project_files: list[ProjectFile] = []
        self.model_builder = None
        #status tracking if the visualisation is uptodate with changes in relations and OTL-assets
        self.visualisation_uptodate: VisualisationStateTracker = VisualisationStateTracker()
        self.graph_saved_status: bool = True # status tracking if graph changes are written to html

    @classmethod
    def load_project(cls, project_path: Path = None):
        """
        Loads a project from a specified directory by reading its details from a JSON file.

        It validates the existence of the project directory and the required project details file
        before extracting and returning the project information.

        :param project_path: The path to the project directory. Defaults to None.
        :type project_path: Path, optional

        :return: An instance of the project class initialized with the loaded details.
        :rtype: Project

        :raises FileNotFoundError:  If the project directory or the project details file does not
                                    exist.
        """
        OTLLogger.logger.info(f"loading project details: {project_path.name}",extra={"timing_ref":f"details_{project_path.name}"})
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
            last_quick_save = (Path(project_path / cls.quick_saves_foldername) /
                               Path(project_details['last_quick_save']))


        if 'subset_operator' not in project_details or not project_details['subset_operator']:
            subset_operator = None
        else:
            subset_operator = project_details['subset_operator']

        if 'otl_version' not in project_details or not project_details['otl_version']:
            otl_version = None
        else:
            otl_version = project_details['otl_version']

        OTLLogger.logger.info(f"loading project details: {project_path.name}"
                              ,extra={"timing_ref":f"details_{project_path.name}"})
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
        Saves the current project to a designated directory, including project details and any
        associated subset files.

        This function ensures that the project directory is created if it does not exist and
        updates the last modified timestamp if necessary.

        :param self: The instance of the class containing project details.

        :return: None

        :raises OSError:    If there is an error creating the directory or writing the project
                            details file.

        :example:
            project.save_project_to_dir()
        """

        project_dir_path = self.get_project_local_path()

        OTLLogger.logger.debug("Saving project to %s", project_dir_path)
        project_dir_path.mkdir(exist_ok=True, parents=True)
        self.save_project_details(project_dir_path=project_dir_path)

        if self.subset_path and self.subset_path.parent.absolute() != project_dir_path.absolute():
            # move subset to project dir
            new_subset_path = project_dir_path / self.subset_path.name
            shutil.copy(src=self.subset_path, dst=new_subset_path)

    def get_project_local_path(self) -> Path:
        otl_wizard_project_dir = ProgramFileStructure.get_otl_wizard_projects_dir()
        return otl_wizard_project_dir / self.project_path.name

    def get_current_visuals_folder_path(self) -> Path:
        visuals_folder = self.get_project_local_path() / self.visualisation_foldername

        if not visuals_folder.exists():
            os.makedirs(visuals_folder, exist_ok=True)

        return visuals_folder

    def get_current_visuals_html_path(self) -> Path:
        return self.get_current_visuals_folder_path() / self.visualisation_filename

    def get_visualisation_python_support_data_path(self) -> Path:
        visuals_uptodate_state_path = self.get_current_visuals_folder_path() / self.visualisation_python_support_data_filename

        if not visuals_uptodate_state_path.exists():
            with open(visuals_uptodate_state_path,"w") as file:
                json.dump({"visuals_uptodate":False},file)

        return visuals_uptodate_state_path

    def load_visualisation_python_support_data(self,vis_wrap: Optional[PyVisWrapper] = None) -> None:
        file_path = self.get_visualisation_python_support_data_path()

        with open(file_path, "r") as file:
            json_data = json.load(file)

            self.visualisation_uptodate.set_clear_all(not json_data["visuals_uptodate"])
            if vis_wrap and "collection_support_data" in json_data.keys():
                vis_wrap.special_edges = json_data["collection_support_data"]["vis_wrap.special_edges"]
                vis_wrap.asset_id_to_display_name_dict = json_data["collection_support_data"][
                    "vis_wrap.asset_id_to_display_name_dict"]
                vis_wrap.relation_id_to_collection_id = defaultdict(list,json_data["collection_support_data"][
                    "vis_wrap.relation_id_to_collection_id"])
                vis_wrap.collection_id_to_list_of_relation_ids = defaultdict(list,json_data["collection_support_data"][
                    "vis_wrap.collection_id_to_list_of_relation_ids"])
                vis_wrap.collection_relation_count_threshold = json_data["collection_support_data"][
                    "vis_wrap.collection_relation_count_threshold"]

    def save_visualisation_python_support_data(self,vis_wrap: Optional[PyVisWrapper] = None) -> None:
        file_path = self.get_visualisation_python_support_data_path()

        if file_path.exists():
            # load file first to preserve previously saved data
            with open(file_path, "r") as file:
                json_data = json.load(file)
        else:
            json_data = {}


        json_data["visuals_uptodate"] = not self.visualisation_uptodate.get_clear_all()
        if vis_wrap:
            if "collection_support_data" not in json_data.keys():
                json_data["collection_support_data"] = {}

            json_data["collection_support_data"]["vis_wrap.special_edges"] = vis_wrap.special_edges
            json_data["collection_support_data"]["vis_wrap.asset_id_to_display_name_dict"] = vis_wrap.asset_id_to_display_name_dict
            json_data["collection_support_data"]["vis_wrap.relation_id_to_collection_id"] = vis_wrap.relation_id_to_collection_id
            json_data["collection_support_data"]["vis_wrap.collection_id_to_list_of_relation_ids"] = vis_wrap.collection_id_to_list_of_relation_ids
            json_data["collection_support_data"]["vis_wrap.collection_relation_count_threshold"] = vis_wrap.collection_relation_count_threshold
            # json_data["visualisation_option"] =

        with open(file_path, "w") as file:
            json.dump(json_data ,file)

    def save_project_details(self, project_dir_path: Path) -> None:
        """
        Saves the project's details to a specified directory in JSON format.

        This function constructs a dictionary of project attributes and writes it to a file, updating the last modified timestamp if necessary.

        :param self: The instance of the class managing the project.
        :param project_dir_path: The directory path where the project details will be saved.
        :type project_dir_path: Path

        :return: None

        :raises OSError: If there is an error writing the project details file.

        :example:
            project.save_project_details(Path('/path/to/project'))
        """

        last_quick_save_name = None
        if self.last_quick_save:
            last_quick_save_name = str(self.last_quick_save.name)

        if not self.laatst_bewerkt:
            self.laatst_bewerkt = datetime.datetime.now()

        subset_name = None
        if self.subset_path:
            subset_name = self.subset_path.name

        project_details_dict = {
            'bestek': self.bestek,
            'eigen_referentie': self.eigen_referentie,
            'laatst_bewerkt': self.laatst_bewerkt.strftime("%Y-%m-%d %H:%M:%S"),
            'subset': subset_name,
            'subset_operator': self.get_operator_name(),
            'otl_version': self.get_otl_version(),
            'last_quick_save': last_quick_save_name
        }

        with open(project_dir_path / self.project_details_filename, "w") as project_details_file:
            json.dump(project_details_dict, project_details_file)

    @add_loading_screen
    async def load_validated_assets_async(self) -> list[Union[RelatieObject, RelationInteractor]]:
        # sourcery skip: assign-if-exp, reintroduce-else, use-named-expression
        """
        Loads validated assets from the most recent quick save file.

        If a valid quick save path is found, it converts the file contents into a list of AIMObject
        instances; otherwise, it returns an empty list.

        :param self: The instance of the class managing asset loading.

        :return:    A list of validated AIMObject instances loaded from the quick save file, or an
                    empty list if no valid path is found.
        :rtype: list[AIMObject]

        :example:
            assets = project.load_validated_assets()
        """

        path = self.get_last_quick_save_path()

        if path:
            timing_ref = f"load_assets_{path.stem}"
            OTLLogger.logger.debug(
                f"Execute Project.load_validated_assets({path.name}) for project "
                f"{self.eigen_referentie}",
                extra={"timing_ref": timing_ref})

            # noinspection PyTypeChecker
            saved_objects, exceptions_group = await Helpers.converter_from_file_to_object_async(
                path,
                allow_non_otl_conform_attributes=True)

            object_count = len(saved_objects)
            OTLLogger.logger.debug(
                f"Execute Project.load_validated_assets({path.name}) for project"
                f" {self.eigen_referentie} ({object_count} objects)",
                extra={"timing_ref":  timing_ref})

            return saved_objects
        return []


    def load_validated_assets(self) -> list[Union[RelatieObject, RelationInteractor]]:
        # sourcery skip: assign-if-exp, reintroduce-else, use-named-expression
        """
        Loads validated assets from the most recent quick save file.

        If a valid quick save path is found, it converts the file contents into a list of AIMObject
        instances; otherwise, it returns an empty list.

        :param self: The instance of the class managing asset loading.

        :return:    A list of validated AIMObject instances loaded from the quick save file, or an
                    empty list if no valid path is found.
        :rtype: list[AIMObject]

        :example:
            assets = project.load_validated_assets()
        """

        path = self.get_last_quick_save_path()

        if path:
            timing_ref = f"load_assets_{path.stem}"
            OTLLogger.logger.debug(
                f"Execute Project.load_validated_assets({path.name}) for project "
                f"{self.eigen_referentie}",
                extra={"timing_ref": timing_ref})

            # noinspection PyTypeChecker
            saved_objects, exceptions_group = Helpers.converter_from_file_to_object(
                path)

            object_count = len(saved_objects)
            OTLLogger.logger.debug(
                f"Execute Project.load_validated_assets({path.name}) for project"
                f" {self.eigen_referentie} ({object_count} objects)",
                extra={"timing_ref": timing_ref})

            return saved_objects
        return []

    async def save_validated_assets(self, asynchronous=True) -> None:
        """
        Saves validated assets to the project quick save directory.

        It manages the quick save files by removing old saves and generating a new save file with a unique name.

        The format of the save file is: quick_save_{date}_{time}.json:
            date:   the date on which the quicksave was made in format yymmdd
            time:   the time on which the quicksave was made in format HHMMSS

        All quicksaves that are more than set days old (default= 7) are deleted in this function.

        :param self: The instance of the class managing quick saves.

        :return: None

        :raises OSError: If there is an issue creating the quick save directory or saving the file.
        @param asynchronous: do the save asynchronous or not
        """

        if self.quick_save_dir_path.exists():
            current_date = datetime.datetime.now()

            self.remove_too_old_quicksaves(current_date=current_date,
                                          max_days_stored=Project.max_days_quicksave_stored,
                                          date_format=Project.quicksave_date_format)
        else:
            os.mkdir(self.quick_save_dir_path )

        current_date_str = datetime.datetime.now().strftime(Project.quicksave_date_format)

        save_path = self.quick_save_dir_path  / f"quick_save-{current_date_str}.json"
        if asynchronous:
            try:
                create_task_reraise_exception(self.make_quick_save_async(save_path=save_path))
            except DeprecationWarning:
                # should only go here if you are testing
                self.make_quick_save(save_path=save_path)
        else:
            self.make_quick_save(save_path=save_path)


    async def make_quick_save_async(self, save_path: Path) -> None:
        object_count = len(self.assets_in_memory)
        OTLLogger.logger.debug(f"Execute Project.make_quick_save({save_path.name}) for project {self.eigen_referentie} ({object_count} objects)", extra={
            "timing_ref": f"make_quick_save_{save_path.stem}"})

        await Helpers.from_objects_to_file_async(save_path,self.assets_in_memory)
        self.last_quick_save = save_path
        self.save_project_to_dir()
        OTLLogger.logger.debug(
            f"Execute Project.make_quick_save({save_path.name}) for project {self.eigen_referentie} ({object_count} objects)",
            extra={
                "timing_ref": f"make_quick_save_{save_path.stem}"})



    def make_quick_save(self, save_path: Path) -> None:
        object_count = len(self.assets_in_memory)
        OTLLogger.logger.debug(f"Execute Project.make_quick_save({save_path.name}) for project {self.eigen_referentie} ({object_count} objects)", extra={
            "timing_ref": f"make_quick_save_{save_path.stem}"})

        Helpers.from_objects_to_file(save_path,self.assets_in_memory)
        self.last_quick_save = save_path
        self.save_project_to_dir()
        OTLLogger.logger.debug(
            f"Execute Project.make_quick_save({save_path.name}) for project {self.eigen_referentie} ({object_count} objects)",
            extra={
                "timing_ref": f"make_quick_save_{save_path.stem}"})



    def remove_too_old_quicksaves(self, current_date: datetime, max_days_stored: datetime,
                                   date_format: str) -> None:
        """
        Removes quick save files that are older than a specified number of days.

        This function checks the modification dates of the quick save files and deletes those that exceed the maximum age defined by the user.

        Files that do not adhere to the standard naming convention are never deleted.

        :param self: The instance of the class managing quick saves.
        :param current_date: The current date used to compare against quick save file dates.
        :type current_date: datetime
        :param max_days_stored: The maximum number of days to retain quick save files.
        :type max_days_stored: datetime
        :param date_format: The format used to parse the date from the filename.
        :type date_format: str

        :return: None

        :example:
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
        """
        Exports the project data to a specified file in OTLW format which is a custom ZIP format.

        This method creates a ZIP file containing the project's details,
        including the project details file, saved documents overview, subset path, and any saved
        project files. It also includes the last quick save file if it exists, ensuring that all
        relevant project information is packaged together.

        :param file_path: The path where the OTLW file will be saved.
        :type file_path: Path

        :return: None

        :raises FileNotFoundError: If any of the files to be included in the ZIP do not exist.
        """

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

            # tell the user there are files missing
            missing_project_files = self.check_if_project_files_exist()
            if len(missing_project_files):
                message = GlobalTranslate._(
                    "There are files missing that belong to this project:\n")
                for project_file in missing_project_files:
                    filename = project_file.file_path.name
                    message += f"   -{filename}\n"

                message += GlobalTranslate._("Do you still want to export?")
                msgbox = YesOrNoNotificationWindow(message=message, title=GlobalTranslate._("Missing project files"))
                answer = msgbox.exec()

                if answer == 65536:
                    return

            for document in self.get_saved_projectfiles():
                if document.file_path.exists():
                    file_zip_path = Path(self.project_files_foldername) / document.file_path.name
                    project_zip.write(document.file_path, arcname=file_zip_path)

            last_quick_save_path = self.get_last_quick_save_path()
            if last_quick_save_path and last_quick_save_path.exists():
                last_quick_save_zip_path = Path(self.quick_saves_foldername) / last_quick_save_path.name
                project_zip.write(last_quick_save_path, arcname=last_quick_save_zip_path)

            visualisation_html_path = self.get_current_visuals_html_path()
            if visualisation_html_path and visualisation_html_path.exists():
                visualisation_html_zip_path = Path(
                    self.visualisation_foldername) / visualisation_html_path.name
                project_zip.write(visualisation_html_path, arcname=visualisation_html_zip_path)

            visualisation_uptodate_json_path = self.get_visualisation_python_support_data_path()
            if visualisation_uptodate_json_path and visualisation_uptodate_json_path.exists():
                visualisation_uptodate_json_zip_path = Path(
                    self.visualisation_foldername) / visualisation_uptodate_json_path.name
                project_zip.write(visualisation_uptodate_json_path, arcname=visualisation_uptodate_json_zip_path)

    @classmethod
    def import_project(cls, file_path: Path):
        """
        Imports a project from a specified OTLW file which is a custom ZIP format.

        This class method extracts project details from a ZIP file and creates a new project directory based on the extracted information. It handles the creation of the project directory and raises an error if the directory already exists.

        :param file_path: The path to the OTLW file containing the project data.
        :type file_path: Path

        :return: An instance of the Project class initialized with the imported project details.
        :rtype: Self

        :raises FileExistsError: If the project directory already exists.
        """

        with zipfile.ZipFile(file=file_path) as project_file:

            # TODO: handle if project doesn't contain project_details.json files
            project_details = json.load(fp=project_file.open(cls.project_details_filename))

            project_dir_path = Path(
                ProgramFileStructure.get_otl_wizard_projects_dir() / project_details[
                    'eigen_referentie'])
            try:
                project_dir_path.mkdir(exist_ok=False, parents=True)
            except FileExistsError as ex:
                OTLLogger.logger.error("Project dir %s already exists", project_dir_path)
                raise ProjectExistsError(eigen_referentie=project_details['eigen_referentie'])

            project_file.extractall(path=project_dir_path)

        return Project.load_project(project_path=project_dir_path)

    def delete_project_dir_by_path(self) -> None:
        """
        Deletes the project directory specified by the project's path.

        This method removes the entire directory associated with the project, including all its contents. It logs the deletion action for debugging purposes.

        :return: None
        """

        OTLLogger.logger.debug("Deleting project %s", self.project_path)
        shutil.rmtree(path=self.project_path)



    def are_all_project_files_in_memory_valid(self) -> bool:
        """
        Checks if all project files currently in memory are valid.

        This method evaluates the state of saved project files to determine if at least one file
        meets the required validity criteria. It logs the process and returns a boolean indicating
        whether any project files are valid.

        :return: True if at least one project file is valid; otherwise, False.
        :rtype: bool
        """

        # OTLLogger.logger.debug("Started searching for project files in memory that are OTL conform")

        if not self.saved_project_files:
            OTLLogger.logger.debug("No project files in memory")
            return False
        return all(
            template.state == FileState.OK for template in self.saved_project_files
        )

    def get_subset_db_name(self) -> str:
        """
        Retrieves the name of the subset database associated with the project.

        This function returns the name of the subset path as a string.

        :return: The name of the subset database.
        :rtype: str
        """

        return  str(self.subset_path.name)

    def get_model_builder(self) -> ModelBuilder:
        """
        Loads and initializes the model builder associated with the project if it has not been
        created yet.

        This function checks if the model builder is already set and creates a new instance using
        the subset path if necessary.

        :return: The model builder instance associated with the project.
        :rtype: ModelBuilder

        :raises ValueError: If the subset path is not set when attempting to create the model
                            builder.
        """


        if not self.model_builder and self.subset_path:
            self.model_builder = ModelBuilder(self.subset_path)
        return self.model_builder

    def clear_model_builder_from_memory(self) -> None:
        """
        Clears the model builder from memory by setting it to None.

        This function effectively releases the reference to the current model builder, allowing for garbage collection.

        :return: None
        """

        self.model_builder = None

    def get_operator_name(self) -> str:
        """
        Retrieves the name of the subset operator associated with the project.

        If the subset operator is not already set, it fetches the operator name from the model builder and processes it accordingly.

        :return: The name of the subset operator.
        :rtype: str

        :raises ValueError: If the operator name cannot be determined from the model builder.
        """

        if self.subset_path and not self.subset_operator:
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

        :return: The OTL version.
        :rtype: str

        :raises ValueError: If the OTL version cannot be determined from the model builder.
        """

        if self.subset_path and not self.otl_version:
            self.otl_version = self.get_model_builder().get_otl_version()


        return self.otl_version

    def load_saved_document_filenames(self):
        """
        Loads the filenames of saved documents associated with the project from a specified directory.

        This function checks for the existence of a saved documents file, reads its contents, and populates the list of saved project files with their saved states. If there are no quicksaves yet then the states are set to FileState.WARNING.

        :return: The instance of the class, allowing for method chaining.
        :rtype: self

        :raises FileNotFoundError: If the saved documents file does not exist.
        :raises json.JSONDecodeError: If the saved documents file contains invalid JSON.
        """

        project_dir_path = ProgramFileStructure.get_otl_wizard_projects_dir() / self.project_path.name
        saved_documents_path: Path = project_dir_path / Project.saved_documents_filename



        if saved_documents_path.exists():

            OTLLogger.logger.debug(
                f"Loading saved documents: {self.project_path.name}/{Project.saved_documents_filename}",
                extra={"timing_ref": f"load_quicksave_{self.project_path.name}"})

            with open(file=saved_documents_path,mode="r") as saved_document:
                try:
                    saved_documents = json.load(fp=saved_document)
                except json.decoder.JSONDecodeError as e:
                    # happens when the saved_documents.json file is empty
                    OTLLogger.logger.warning(e)
                    saved_documents = []
            saved_documents_str = str(saved_documents)

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
                document_file_path = location_dir / Path(document['file_path']).name

                if (state == FileState.OK and
                    not (quick_save_path.exists() and
                     len(list(os.listdir(path=quick_save_path))))):
                    state = FileState.WARNING

                file = ProjectFile(
                    file_path=location_dir / Path(document['file_path']).name ,
                    state=state)
                self.saved_project_files.append(file)

            OTLLogger.logger.debug(
                f"Loading saved documents: {self.project_path.name}/{Project.saved_documents_filename}",
                extra={"timing_ref": f"load_quicksave_{self.project_path.name}"})
        return self

    def check_if_project_files_exist(self) -> list[ProjectFile]:
        missing_project_files = []
        for project_file in self.get_saved_projectfiles():
            if not project_file.file_path.exists():
                OTLLogger.logger.info(f'project "{self.eigen_referentie}" is missing file: {project_file.file_path}')
                missing_project_files.append(project_file)
                project_file.state = FileState.ERROR


        return missing_project_files

    def get_quicksaves_dir_path(self) -> Path:
        """
        Retrieves the path to the quick saves directory for the project.

        If the directory does not exist, it creates it before returning the path.

        :return: The path to the quick saves directory.
        :rtype: Path

        :raises OSError: If the directory cannot be created due to a file system error.
        """

        quick_saves = Path(self.project_path / self.quick_saves_foldername)
        if not quick_saves.exists() and self.project_path.exists():
            os.mkdir(Path(self.project_path / self.quick_saves_foldername))
        return quick_saves

    def get_last_quick_save_path(self) -> Optional[Path]:
        # sourcery skip: use-named-expression
        """
        Retrieves the path to the last quick save file for the project.

        It first checks if there is a specific last quick save path and if that exists; if not, it looks for the most recent file in the quick saves directory.

        :return: The path to the last quick save file, or None if no quick save exists.
        :rtype: Optional[Path]

        :raises OSError: If there is an issue accessing the quick saves directory.
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
        Retrieves the directory path for the project's files.

        This function constructs and returns the full path to the folder designated for storing project files.

        :param self: The instance of the class managing the project.

        :return: The path to the project files directory.
        :rtype: Path

        :example:
            files_dir = project.get_project_files_dir_path()
        """

        return self.project_path / self.project_files_foldername

    def get_old_project_files_dir_path(self) -> Path:
        """
        Retrieves the directory path for the old project's files.

        This function constructs and returns the full path to the folder designated for storing project files in projects made with an old version of OTL wizard.

        :param self: The instance of the class managing the project.

        :return: The path to the old project files directory.
        :rtype: Path

        :example:
            old_files_dir = project.get_old_project_files_dir_path()
        """

        return self.project_path / self.old_project_files_foldername

    def delete_template_folder(self) -> None:
        """
        Deletes the template folders associated with the project.

        This method removes both the old and new project files directories, effectively clearing
        out all template files. It logs the start and completion of the deletion process for
        debugging purposes.

        :return: None
        """

        OTLLogger.logger.debug(f"Started clearing out the whole template folder of "
                      f"project: {self.eigen_referentie}")
        new_project_files_folder = self.get_project_files_dir_path()
        old_project_files_folder = self.get_old_project_files_dir_path()

        if old_project_files_folder.exists():
            shutil.rmtree(path=old_project_files_folder)

        if new_project_files_folder.exists():
            shutil.rmtree(path=new_project_files_folder)

        OTLLogger.logger.debug("Finished clearing out the whole template folder")

    def save_project_filepaths_to_file(self) -> None:
        """
        Saves the file paths and states of the project's saved files to a JSON file.

        This function constructs a list of saved project file details and writes them to a specified file within the project's directory. It will overwrite the existing saved_documents.json.

        :return: None

        :raises OSError: If there is an issue writing to the file or accessing the project directory.
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
        with open(file=project_dir_path / self.saved_documents_filename, mode="w+") as project_details_file:
            json.dump(object_array, project_details_file)

    def is_in_project(self, file_path) -> ProjectFile:
        """
        Checks if a specified file path is present in the project's saved files.

        This function searches through the list of saved project files and returns the matching project file if found, or None if no match exists.

        :param file_path: The path of the file to check for in the project's saved files.
        :type file_path: Path

        :return: The matching project file if found, or None if not.
        :rtype: ProjectFile

        :raises TypeError: If the provided file_path is not of the expected type.
        """

        matches = [project_file for project_file in self.saved_project_files if
         project_file.file_path == file_path]
        return  matches[0] if matches else None

    def get_saved_projectfiles(self) -> list[ProjectFile]:
        """
        Retrieves the list of saved project files associated with the project.

        This function returns the current state of the saved project files as a list of ProjectFile instances.

        :return: A list containing the saved project files.
        :rtype: list[ProjectFile]
        """

        return self.saved_project_files

    def copy_and_add_project_file(self, file_path: Path | str, state: FileState) -> None:
        """
        Adds a saved project file to the list of saved project files, makes a copy of it, and
        updates its state.

        This function converts the file path to a Path object if it is provided as a string,
        constructs the full file path, and appends a new ProjectFile instance to the saved project
        files.

        :param file_path: The path of the file to be saved, which can be a string or a Path object.
        :type file_path: Path | str
        :param state: The state of the project file to be saved.
        :type state: FileState

        :return: None

        :raises ValueError: If the provided file_path is invalid or if the state is not a valid
                            FileState.
        """


        if isinstance(file_path,str):
            file_path = Path(file_path)

        if self.has_duplicate_filename(filename=file_path.name,
                                       project_files_list=self.saved_project_files):
            return

        end_location = self.make_copy_of_added_file(filepath=file_path)
        self.saved_project_files.append(ProjectFile(file_path=end_location, state=state))
        self.save_project_filepaths_to_file()

    def has_duplicate_filename(self, filename: str, project_files_list: list[ProjectFile]) -> bool:
        file_names_in_project = [project_file.file_path.name for project_file in
                                 project_files_list]
        has_duplicate = False
        if filename in file_names_in_project:
            message = GlobalTranslate._("Can't insert duplicate filename {0}")

            msgbox = NotificationWindow(message=message.format(filename),
                                        title=GlobalTranslate._("Duplicate filename"))
            msgbox.exec()
            has_duplicate = True
        return has_duplicate

    def make_copy_of_added_file(self, filepath: Path) -> Path:
        """
        Creates a copy of the specified file in the OTL template files directory.

        This function ensures the destination directory exists, copies the file if it is not
        already in the target location, and returns the path to the copied file.

        :param filepath: The path of the file to be copied.
        :type filepath: Path

        :return: The path to the copied file in the OTL template files directory.
        :rtype: Path

        :raises FileNotFoundError: If the specified file does not exist.
        :raises OSError: If there is an issue creating the directory or copying the file.
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
        OTLLogger.logger.debug(f"Created a copy of the template file {filepath.name} in the project folder")
        return end_location


    def remove_all_project_files(self):
        """
        Removes all project files from memory and deletes them from the file system.

        This function iterates through the list of saved project files, attempts to delete each one, and handles any errors that occur during the deletion process. It creates a notification window to the user if the program doesn't have access to the file, and an empty saved_project_files list is saved to saved_document.json after the whole process.

        :return: None

        :raises ExcelFileUnavailableError: If a file cannot be deleted due to its unavailability.
        """

        OTLLogger.logger.debug("memory contains %s", self.saved_project_files)
        for file in self.saved_project_files:
            OTLLogger.logger.debug("starting to delete file %s",file.file_path)
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

        This function checks if the file is part of the project, attempts to delete it, and
        updates the saved project files accordingly.

        :param file_path: The path of the project file to be removed.
        :type file_path: Path | str

        :return: True if the file was successfully removed, False otherwise.

        :raises ExcelFileUnavailableError: If the file cannot be deleted due to its unavailability.
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

        This function attempts to unlink the file at the given path and handles some errors that may occur during the deletion process. Needs following calls after calling this one: self.saved_project_files.remove(project_file) and self.save_project_filepaths_to_file().

        :param file_path: The path of the project file to be deleted.
        :type file_path: Path | str

        :return: True if the file was successfully deleted, False if the file was not found.

        :raises ExcelFileUnavailableError: If there is a permission error while attempting to delete the file.
        """

        try:
            file_path_str = str(file_path)
            OTLLogger.logger.debug(f"file path = {file_path_str}")
            Path(file_path).unlink()
            return True
        except FileNotFoundError as e:
            OTLLogger.logger.error(e)
            return False
        except PermissionError as e:
            #TODO: make other errors + dialog windows for cases with non-excel files if necessary
            OTLLogger.logger.error(e)
            raise ExcelFileUnavailableError(file_path=file_path, exception=e) from e

    def change_subset(self, new_path: Path) -> None:
        """
        Changes the current subset path for the project and resets related properties.

        This function clears the model builder from memory, updates the subset path, loads a new model builder, and resets the subset operator and OTL version to their initial states.

        :param new_path: The new path to set as the subset for the project.
        :type new_path: Path

        :return: None
        """

        self.clear_model_builder_from_memory()
        self.subset_path = new_path
        self.model_builder = self.get_model_builder()
        self.subset_operator = None
        self.otl_version = None
        self.update_last_alter_time()
        self.save_project_to_dir()

    def update_information(self, new_eigen_ref:str, new_bestek:str, new_subset_path: Path):
        """
        Updates the project information with new details.

        This method modifies the project's eigen reference,
        bestek, and subset path, ensuring that the project reflects the latest information.
        It also updates the last altered time to track when the changes were made.

        :param new_eigen_ref: The new eigen reference for the project.
        :type new_eigen_ref: str
        :param new_bestek: The new bestek for the project.
        :type new_bestek: str
        :param new_subset_path: The new path for the project's subset.
        :type new_subset_path: Path

        :return: None
        """
        # check if there is a difference avoid unnecessary renaming of folders
        if new_eigen_ref != self.eigen_referentie:
            # include the new_subset_path so it can be changed to the new folder name if it is the old subset
            new_subset_path = self.update_eigen_referentie(new_eigen_ref,new_subset_path)
        self.bestek = new_bestek
        self.change_subset(new_subset_path)
        self.update_last_alter_time()


    def update_eigen_referentie(self,new_eigen_ref:str, new_subset_path:Path=None ) -> Path:
        new_project_path = Path(ProgramFileStructure.get_otl_wizard_projects_dir() / new_eigen_ref)
        try:
            if new_project_path.exists():
                raise FileExistsError
            shutil.move(self.project_path, new_project_path)
        except FileExistsError as ex:
            OTLLogger.logger.error("Project dir %s already exists", new_project_path)
            raise ProjectExistsError(eigen_referentie=new_eigen_ref)
        except PermissionError as ex:
            OTLLogger.logger.error("No permission to rename ", self.project_path)
            raise ex

        # try:
        #     shutil.copytree(self.project_path, new_project_path)
        # except FileExistsError as ex:
        #     OTLLogger.logger.error("Project dir %s already exists", new_project_path)
        #     raise ProjectExistsError(eigen_referentie=new_eigen_ref)

        # delete the original path
        # self.delete_project_dir_by_path()

        # change the new subset path otherwise change the old one
        if not new_subset_path:
            new_subset_path = self.subset_path
        elif new_subset_path == self.subset_path:
            new_subset_path = new_project_path / self.subset_path.name


        # make sure the current data is correctly renamed before updating the projects attributes
        self.eigen_referentie = new_eigen_ref
        self.project_path = new_project_path

        return new_subset_path


    def update_last_alter_time(self):
        """
        Updates the last altered time of the project.

        This method sets the last altered timestamp to the current date and time, allowing for tracking of when the project was last modified.

        :return: None
        """

        time_of_alter = datetime.datetime.now().date()
        self.laatst_bewerkt = time_of_alter


    def __eq__(self, __value):
        if not __value:
            return False

        return (self.eigen_referentie == __value.eigen_referentie and
                Helpers.equal_paths(path1=self.subset_path,path2=__value.subset_path) and
                self.subset_operator == __value.subset_operator and
                self.otl_version == __value.otl_version and
                self.bestek == __value.bestek and
                self.laatst_bewerkt == __value.laatst_bewerkt and
                self.saved_project_files == __value.saved_project_files)

    def set_saved_graph_status(self,new_status:bool) -> None:
        self.graph_saved_status = new_status

    def get_saved_graph_status(self) -> bool:
        return self.graph_saved_status
