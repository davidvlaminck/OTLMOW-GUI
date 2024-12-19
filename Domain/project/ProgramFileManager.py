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
from Domain.Settings import Settings
from Domain.network.GitHubDownloader import GitHubDownloader
from Domain.project.ProgramFileStructure import ProgramFileStructure
from Domain.project.Project import Project
from Domain.enums import Language, FileState
from Domain.logger.OTLLogger import OTLLogger
from UnitTests.TestClasses.Classes.ImplementatieElement.AIMObject import AIMObject


class ProgramFileManager:
    """
        Manager to manage OTL projects files on local computer
    """

    @classmethod
    def init(cls):
        settings = Settings.get_or_create_settings_file()

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
    def create_empty_temporary_map(cls) -> Path:
        tempdir = Path(tempfile.gettempdir()) / 'temp-otlmow'
        logging.debug(f"tempdir {str(tempdir)}")
        if not tempdir.exists():
            os.makedirs(tempdir)
        [f.unlink() for f in Path(tempdir).glob("*") if f.is_file()]
        return tempdir







