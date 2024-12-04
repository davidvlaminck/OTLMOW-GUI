import datetime
import json
import logging
import os
import platform
import shutil
import tempfile
import zipfile
from pathlib import Path

from otlmow_converter.OtlmowConverter import OtlmowConverter

from Domain import global_vars
from Domain.GitHubDownloader import GitHubDownloader
from Domain.Project import Project
from Domain.enums import Language, FileState
from Domain.logger.OTLLogger import OTLLogger
from Domain.ProjectFile import ProjectFile
from Exceptions.ExcelFileUnavailableError import ExcelFileUnavailableError
from UnitTests.TestClasses.Classes.ImplementatieElement.AIMObject import AIMObject


class ProjectFileManager:
    """
        Manager to manage OTL projects files on local computer
    """

    settings_filename = 'settings.json'


    @classmethod
    def init(cls):
        settings = cls.get_or_create_settings_file()
        logging_file = cls.create_logging_file()
        cls.remove_old_logging_files()
        OTLLogger.init(logging_file)
        return settings

    @classmethod
    def get_project_from_dir(cls, project_dir_path: Path) -> Project:
        return Project.load_project(project_dir_path)

    @classmethod
    def get_home_path(cls) -> Path:
        return Path.home()

    @classmethod
    def get_otl_wizard_work_dir(cls) -> Path:
        work_dir_path = cls.get_home_path() / 'OTLWizardProjects'
        if not work_dir_path.exists():
            work_dir_path.mkdir()
        return work_dir_path

    @classmethod
    def get_otl_wizard_projects_dir(cls) -> Path:
        projects_dir_path = cls.get_otl_wizard_work_dir() / 'Projects'
        if not projects_dir_path.exists():
            projects_dir_path.mkdir()
        return projects_dir_path

    @classmethod
    def get_otl_wizard_model_dir(cls) -> Path:
        model_dir_path = cls.get_otl_wizard_work_dir() / 'Model'
        if not model_dir_path.exists():
            model_dir_path.mkdir()

            # cls.download_fresh_otlmow_model(model_dir_path)
            # cls.get_otlmow_model_version(model_dir_path)
        return model_dir_path

    @classmethod
    def get_all_otl_wizard_projects(cls) -> [Project]:
        otl_wizard_project_dir = cls.get_otl_wizard_projects_dir()

        project_dirs = [project_dir for project_dir in otl_wizard_project_dir.iterdir() if project_dir.is_dir()]
        projects = []
        for project_dir in project_dirs:
            try:
                project = cls.get_project_from_dir(project_dir)
                projects.append(project)
            except FileNotFoundError:
                logging.warning('Project dir %s is not a valid project directory', project_dir)
        return projects

    @classmethod
    def save_project_to_dir(cls, project: Project) -> None:
        otl_wizard_project_dir = cls.get_otl_wizard_projects_dir()
        project_dir_path = otl_wizard_project_dir / project.project_path.name
        logging.debug("Saving project to %s", project_dir_path)
        project_dir_path.mkdir(exist_ok=True, parents=True)

        last_quick_save_name = None
        if project.last_quick_save:
            last_quick_save_name = str(project.last_quick_save.name)

        project_details_dict = {
            'bestek': project.bestek,
            'eigen_referentie': project.eigen_referentie,
            'laatst_bewerkt': project.laatst_bewerkt.strftime("%Y-%m-%d %H:%M:%S"),
            'subset': project.subset_path.name,
            'subset_operator': project.get_operator_name(),
            'otl_version': project.get_otl_version(),
            'last_quick_save': last_quick_save_name
        }

        with open(project_dir_path / "project_details.json", "w") as project_details_file:
            json.dump(project_details_dict, project_details_file)

        # TODO: It seems the idea here was that validated assets are stored in the project and
        #       and loaded again when you open the project so object_lists don't need to be
        #       validated again? Implement this again later
        #       The problem is that he would overwrite assets.json that now contains a list of
        #       objects_list_files
        # cls.save_validated_assets(project, project_dir_path)

        if project.subset_path.parent.absolute() != project_dir_path.absolute():
            # move subset to project dir
            new_subset_path = project_dir_path / project.subset_path.name
            shutil.copy(project.subset_path, new_subset_path)
        # global_vars.projects = cls.get_all_otl_wizard_projects()

    @classmethod
    def load_validated_assets(cls) -> list[AIMObject]:


        path = global_vars.current_project.get_last_quick_save_path()

        if path:
            return list(OtlmowConverter.from_file_to_objects(path))

        return []



    @classmethod
    def save_validated_assets(cls, project, project_dir_path):
        """
        Saves validated assets of a project to a quick save directory.
        It manages the quick save files by removing old saves and generating a new save file with a unique name.

        the format of the save file is: quick_save_{nbr}-{date}.json:
            nbr:    counts up from 1 everytime a quicksave happens. resets every day.
                    The highest previous number is extracted from the existing quicksave filenames
                    of the current day
            date:   the date on which the quicksave was made in format dd_mm_yy

        All quicksaves that are more than 7 days old are deleted in this function

        Args:
            project: The project containing the assets to be saved.
            project_dir_path: The directory path that the project belongs to

        Returns:
            None

        Raises:
            OSError: If there is an issue creating the quick save directory or saving the file.

        """
        quick_save_dir_path = Path(project_dir_path / "quick_saves")
        save_number = 1
        date_format = "%y%m%d_%H%M%S"
        max_days_stored = 7

        if quick_save_dir_path.exists():
            current_date = datetime.datetime.now()

            cls.remove_too_old_quicksaves(current_date= current_date,
                                          max_days_stored= max_days_stored,
                                          quick_save_dir_path= quick_save_dir_path,
                                          date_format= date_format)
        else:
            os.mkdir(quick_save_dir_path)

        current_date_str =  datetime.datetime.now().strftime(date_format)

        save_path = quick_save_dir_path / f"quick_save-{current_date_str}.json"
        OtlmowConverter.from_objects_to_file(file_path=save_path,
                                             sequence_of_objects=project.assets_in_memory)
        global_vars.current_project.last_quick_save =save_path
        cls.save_project_to_dir(global_vars.current_project)
        project.last_quick_save =save_path
        cls.save_project_to_dir(project)


    @classmethod
    def remove_too_old_quicksaves(cls, current_date, max_days_stored, quick_save_dir_path, date_format):
        files = os.listdir(quick_save_dir_path)
        for filename in files:
            try:
                file_date = datetime.datetime.strptime(filename.split("-")[-1].split(".json")[0],
                                                       date_format)
            except ValueError:
                # if the save file doesn't adhere to standard naming convention it is never deleted
                file_date = current_date

            days_ago = (current_date - file_date).days
            if days_ago > max_days_stored:
                file_to_remove_path = Path(quick_save_dir_path, filename)
                os.remove(file_to_remove_path)

    @classmethod
    def export_project_to_file(cls, project: Project, file_path: Path) -> None:
        with zipfile.ZipFile(file_path, 'w') as project_zip:
            project_zip.write(project.project_path / 'project_details.json', arcname='project_details.json',
                              compresslevel=zipfile.ZIP_DEFLATED)
            project_zip.write(project.assets_path, arcname=project.assets_path.name)
            project_zip.write(project.subset_path, arcname=project.subset_path.name)

            if not project.get_saved_projectfiles():
                project.load_saved_document_filenames()

            for document in project.get_saved_projectfiles():
                file_zip_path = Path('OTL-template-files') / document.file_path.name
                project_zip.write(document.file_path, arcname=file_zip_path)



            last_quick_save_path = project.get_last_quick_save_path()
            last_quick_save_zip_path = Path("quick_saves") / last_quick_save_path.name
            project_zip.write(last_quick_save_path, arcname=last_quick_save_zip_path)

    @classmethod
    def load_project_file(cls, file_path) -> Project:
        with zipfile.ZipFile(file_path) as project_file:

            # TODO: handle if project doesn't contain project_details.json files
            project_details = json.load(project_file.open('project_details.json'))

            project_dir_path = Path(cls.get_otl_wizard_projects_dir() / project_details['eigen_referentie'])
            try:
                project_dir_path.mkdir(exist_ok=False, parents=True)  # TODO: raise error if dir already exists?
            except FileExistsError as ex:
                logging.error("Project dir %s already exists", project_dir_path)
                raise ex

            with zipfile.ZipFile(file_path) as project_file:
                project_file.extractall(path=project_dir_path)

        return cls.get_project_from_dir(project_dir_path)

    @classmethod
    def delete_project_files_by_path(cls, file_path: Path) -> None:
        logging.debug("Deleting project %s", file_path)
        shutil.rmtree(file_path)
        global_vars.projects = cls.get_all_otl_wizard_projects()

    @classmethod
    def load_projects_into_global(cls) -> None:
        global_vars.projects = ProjectFileManager.get_all_otl_wizard_projects()

    @classmethod
    def download_fresh_otlmow_model(cls, model_dir_path) -> None:
        ghdl = GitHubDownloader('davidvlaminck/OTLMOW-Model')
        ghdl.download_full_repo(model_dir_path / 'temp')
        shutil.unpack_archive(model_dir_path / 'temp' / 'full_repo_download.zip',
                              model_dir_path / 'temp' / 'downloaded_model')

    @classmethod
    def get_otlmow_model_version(cls, model_dir_path) -> str:
        ghdl = GitHubDownloader('davidvlaminck/OTLMOW-Model')
        ghdl.download_file(destination_dir=model_dir_path / 'temp', file_path='otlmow_model/version_info.json')
        with open(model_dir_path / 'temp' / 'version_info.json') as json_file:
            version_info = json.load(json_file)

        return version_info['model_version']



    @classmethod
    def delete_template_folder(cls) -> None:
        logging.debug("Started clearing out the whole template folder")
        project = global_vars.current_project
        location_dir = project.project_path / 'OTL-template-files'
        if not location_dir.exists():
            return
        shutil.rmtree(location_dir)
        logging.debug("Finished clearing out the whole template folder")



    @staticmethod
    def create_empty_temporary_map() -> Path:
        tempdir = Path(tempfile.gettempdir()) / 'temp-otlmow'
        logging.debug(f"tempdir {str(tempdir)}")
        if not tempdir.exists():
            os.makedirs(tempdir)
        [f.unlink() for f in Path(tempdir).glob("*") if f.is_file()]
        return tempdir

    @staticmethod
    def correct_project_files_in_memory(project: Project) -> bool:
        logging.debug("Started searching for project files in memory that are OTL conform")
        if project is None:
            logging.debug("No project found")
            return False
        if not project.saved_project_files:
            logging.debug("No project files in memory")
            return False
        return any(
            template.state == FileState.OK for template in project.saved_project_files
        )

    @classmethod
    def get_or_create_settings_file(cls) -> None:

        work_dir_path = cls.get_otl_wizard_work_dir()
        settings_filepath = work_dir_path / 'settings.json'

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        first_run = False
        operating_sys = platform.system()
        language = Language.DUTCH
        if not settings_filepath.exists():
            first_run = True

        with open(settings_filepath, 'w+') as json_file:
            try:
                settings_details = json.load(json_file)
            except:
                settings_details = {}

            if settings_details.__contains__('language'):
                settings_details['language'] = Language[settings_details['language']]
            else:
                settings_details['language'] = str(language.name)


            settings_details['OS']= str(operating_sys)
            settings_details['first_run']= first_run
            settings_details['last_run']= timestamp

            json.dump(settings_details, json_file)

            return settings_details


    @classmethod
    def change_language_on_settings_file(cls, lang) -> None:
        work_dir_path = cls.get_otl_wizard_work_dir()
        settings_file = work_dir_path / cls.settings_filename
        with open(settings_file) as json_file:
            settings_details = json.load(json_file)
        settings_details['language'] = str(lang.name)
        with open(settings_file, 'w') as f:
            json.dump(settings_details, f)

    @classmethod
    def get_language_from_settings(cls) -> Language:
        work_dir_path = cls.get_otl_wizard_work_dir()
        settings_file = work_dir_path / cls.settings_filename
        with open(settings_file) as json_file:
            settings_details = json.load(json_file)
        return Language[settings_details['language']]

    @classmethod
    def create_logging_file(cls) -> Path:
        work_dir_path = cls.get_otl_wizard_work_dir() / 'logs'
        if not work_dir_path.exists():
            work_dir_path.mkdir()
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        logging_filepath = work_dir_path / f'logging_{timestamp}.log'
        if not logging_filepath.exists():
            open(Path(logging_filepath), 'w').close()
        return logging_filepath

    @classmethod
    def remove_old_logging_files(cls) -> None:
        work_dir_path = cls.get_otl_wizard_work_dir() / 'logs'
        for file in os.listdir(work_dir_path):
            file_name = Path(file).stem
            split_file = file_name.split('_')
            logging.debug(f"split file date {str(split_file[-1])}")
            datetime_obj = datetime.datetime.strptime(split_file[-1], "%Y%m%d%H%M%S")
            if datetime_obj < datetime.datetime.now() - datetime.timedelta(days=7):
                os.remove(work_dir_path / file)

