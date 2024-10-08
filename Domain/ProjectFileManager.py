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
from GUI.DialogWindows.NotificationWindow import NotificationWindow
from GUI.translation.GlobalTranslate import GlobalTranslate


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

        project_details_dict = {
            'bestek': project.bestek,
            'eigen_referentie': project.eigen_referentie,
            'laatst_bewerkt': project.laatst_bewerkt.strftime("%Y-%m-%d %H:%M:%S"),
            'subset': project.subset_path.name
        }

        with open(project_dir_path / "project_details.json", "w") as project_details_file:
            json.dump(project_details_dict, project_details_file)

        OtlmowConverter().from_objects_to_file(file_path=Path(project_dir_path / "assets.json"),
                                                  sequence_of_objects=project.assets_in_memory)

        if project.subset_path.parent.absolute() != project_dir_path.absolute():
            # move subset to project dir
            new_subset_path = project_dir_path / project.subset_path.name
            shutil.copy(project.subset_path, new_subset_path)
        global_vars.projects = cls.get_all_otl_wizard_projects()

    @classmethod
    def export_project_to_file(cls, project: Project, file_path: Path) -> None:
        with zipfile.ZipFile(file_path, 'w') as project_zip:
            project_zip.write(project.project_path / 'project_details.json', arcname='project_details.json',
                              compresslevel=zipfile.ZIP_DEFLATED)
            project_zip.write(project.assets_path, arcname=project.assets_path.name)
            project_zip.write(project.subset_path, arcname=project.subset_path.name)

    @classmethod
    def add_project_files_to_file(cls, project: Project) -> None:
        otl_wizard_project_dir = cls.get_otl_wizard_projects_dir()
        object_array = []
        for objects_list in project.saved_objects_lists:
            objects_list_details = {
                'file_path': str(objects_list.file_path),
                'state': objects_list.state.value
            }
            object_array.append(objects_list_details)
        project_dir_path = otl_wizard_project_dir / project.project_path.name
        with open(project_dir_path / "assets.json", "w") as project_details_file:
            json.dump(object_array, project_details_file)

    @classmethod
    def get_objects_list_saved_in_project(cls, project: Project) -> Project:
        project_dir_path = cls.get_otl_wizard_projects_dir() / project.project_path.name
        with open(project_dir_path / "assets.json", "r") as project_details_file:
            objects_lists = json.load(project_details_file)
        logging.debug(f"Loaded saved object lists: {str(objects_lists)}")
        objects_lists_array = []
        for objects_list in objects_lists:
            file = ProjectFile(
                file_path=objects_list['file_path'],
                state=FileState.WARNING) # files loaded from memory storage need to be validated
                                         # again
                # state=template['state'])
            objects_lists_array.append(file)
        project.saved_objects_lists = objects_lists_array
        return project

    @classmethod
    def load_project_file(cls, file_path) -> Project:
        project_dir_path = Path(cls.get_otl_wizard_projects_dir() / file_path.stem)
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
    def add_template_file_to_project(cls, filepath: Path) -> Path:
        project = global_vars.single_project
        location_dir = project.project_path / 'OTL-template-files'
        if not location_dir.exists():
            location_dir.mkdir()
        doc_name = filepath.name
        end_location = location_dir / doc_name
        if end_location == filepath:
            return end_location
        shutil.copy(filepath, end_location)
        logging.debug(f"Created a copy of the template file {filepath.name} in the project folder")
        return end_location

    @classmethod
    def delete_template_folder(cls) -> None:
        logging.debug("Started clearing out the whole template folder")
        project = global_vars.single_project
        location_dir = project.project_path / 'OTL-template-files'
        if not location_dir.exists():
            return
        shutil.rmtree(location_dir)
        logging.debug("Finished clearing out the whole template folder")

    @classmethod
    def delete_template_file_from_project(cls, file_path) -> bool:
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
        if not project.saved_objects_lists:
            logging.debug("No project files in memory")
            return False
        return any(
            template.state == FileState.OK for template in project.saved_objects_lists
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
