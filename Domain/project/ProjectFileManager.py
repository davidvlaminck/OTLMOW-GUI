import datetime
import json
import logging
import os
import platform
import shutil
import tempfile
import zipfile
from pathlib import Path

from openpyxl.compat import deprecated
from otlmow_converter.OtlmowConverter import OtlmowConverter

from Domain import global_vars
from Domain.network.GitHubDownloader import GitHubDownloader
from Domain.project.ProgramFileStructure import ProgramFileStructure
from Domain.project.Project import Project
from Domain.enums import Language, FileState
from Domain.logger.OTLLogger import OTLLogger
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
    def get_all_otl_wizard_projects(cls) -> [Project]:
        """
        Retrieves all OTL wizard projects from the designated projects directory.
        This class method scans the directory for valid project directories,
        attempts to load each project, and collects them into a list,
        logging any directories that are not valid projects.

        Returns:
            list[Project]: A list of loaded Project instances.

        Raises:
            FileNotFoundError: If a project directory cannot be loaded due to missing files.
        """

        otl_wizard_project_dir = ProgramFileStructure.get_otl_wizard_projects_dir()

        project_dirs = [project_dir for project_dir in otl_wizard_project_dir.iterdir() if project_dir.is_dir()]
        projects = []
        for project_dir in project_dirs:
            try:
                project = Project.load_project(project_dir)
                projects.append(project)
            except FileNotFoundError:
                logging.warning('Project dir %s is not a valid project directory', project_dir)

        global_vars.projects =projects

        return projects


    @classmethod
    def download_fresh_otlmow_model(cls, model_dir_path) -> None:
        """
            what is this doing here?
        """
        ghdl = GitHubDownloader('davidvlaminck/OTLMOW-Model')
        ghdl.download_full_repo(model_dir_path / 'temp')
        shutil.unpack_archive(model_dir_path / 'temp' / 'full_repo_download.zip',
                              model_dir_path / 'temp' / 'downloaded_model')

    @classmethod
    def get_otlmow_model_version(cls, model_dir_path) -> str:
        """
            what is this doing here?
        """
        ghdl = GitHubDownloader('davidvlaminck/OTLMOW-Model')
        ghdl.download_file_to_dir(file_path='otlmow_model/version_info.json',
                                  destination_dir=model_dir_path / 'temp')
        with open(model_dir_path / 'temp' / 'version_info.json') as json_file:
            version_info = json.load(json_file)

        return version_info['model_version']


    @staticmethod
    def create_empty_temporary_map() -> Path:
        tempdir = Path(tempfile.gettempdir()) / 'temp-otlmow'
        logging.debug(f"tempdir {str(tempdir)}")
        if not tempdir.exists():
            os.makedirs(tempdir)
        [f.unlink() for f in Path(tempdir).glob("*") if f.is_file()]
        return tempdir


    @classmethod
    def get_or_create_settings_file(cls) -> None:
        """
            what is this doing here?
        """
        work_dir_path = ProgramFileStructure.get_otl_wizard_work_dir()
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
        """
                    what is this doing here?
                """
        work_dir_path = ProgramFileStructure.get_otl_wizard_work_dir()
        settings_file = work_dir_path / cls.settings_filename
        with open(settings_file) as json_file:
            settings_details = json.load(json_file)
        settings_details['language'] = str(lang.name)
        with open(settings_file, 'w') as f:
            json.dump(settings_details, f)

    @classmethod
    def get_language_from_settings(cls) -> Language:
        """
                    what is this doing here?
                """
        work_dir_path = ProgramFileStructure.get_otl_wizard_work_dir()
        settings_file = work_dir_path / cls.settings_filename
        with open(settings_file) as json_file:
            settings_details = json.load(json_file)
        return Language[settings_details['language']]

    @classmethod
    def create_logging_file(cls) -> Path:
        """
                    what is this doing here?
                """
        work_dir_path = ProgramFileStructure.get_otl_wizard_work_dir() / 'logs'
        if not work_dir_path.exists():
            work_dir_path.mkdir()
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        logging_filepath = work_dir_path / f'logging_{timestamp}.log'
        if not logging_filepath.exists():
            open(Path(logging_filepath), 'w').close()
        return logging_filepath

    @classmethod
    def remove_old_logging_files(cls) -> None:
        """
                    what is this doing here?
                """
        work_dir_path = ProgramFileStructure.get_otl_wizard_work_dir() / 'logs'
        for file in os.listdir(work_dir_path):
            file_name = Path(file).stem
            split_file = file_name.split('_')
            logging.debug(f"split file date {str(split_file[-1])}")
            datetime_obj = datetime.datetime.strptime(split_file[-1], "%Y%m%d%H%M%S")
            if datetime_obj < datetime.datetime.now() - datetime.timedelta(days=7):
                os.remove(work_dir_path / file)

