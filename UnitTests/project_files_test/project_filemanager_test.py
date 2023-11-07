import datetime
import os
import re
import shutil
from pathlib import Path
from sys import platform

import pytest

from Domain.Project import Project
from Domain.ProjectFileManager import ProjectFileManager

ROOT_DIR = Path(__file__).parent


def test_get_project_from_dir_given_project_dir_location():
    project_dir_path = ROOT_DIR / 'mock_otlwizard_project_dir' / 'project_1'

    project = ProjectFileManager.get_project_from_dir(project_dir_path)

    assert project.project_path == Path(ROOT_DIR / 'mock_otlwizard_project_dir' / 'project_1')
    assert project.subset_path == Path(ROOT_DIR / 'mock_otlwizard_project_dir' / 'project_1' / 'OTL_AllCasesTestClass.db')
    assert project.assets_path == Path(ROOT_DIR / 'mock_otlwizard_project_dir' / 'project_1' / 'assets.json')
    assert project.eigen_referentie == "eigen referentie"
    assert project.bestek == "bestek"
    assert project.laatst_bewerkt == datetime.datetime(2023, 11, 1)


def test_get_project_from_dir_project_dir_missing():
    project_dir_path = ROOT_DIR / 'mock_otlwizard_project_dir' / 'project_missing'

    with pytest.raises(FileNotFoundError):
        ProjectFileManager.get_project_from_dir(project_dir_path)


def test_get_project_from_dir_details_missing():
    project_dir_path = ROOT_DIR / 'mock_otlwizard_project_dir' / 'project_details_missing'
    project_dir_path.mkdir(exist_ok=True, parents=True)

    with pytest.raises(FileNotFoundError):
        ProjectFileManager.get_project_from_dir(project_dir_path)

    shutil.rmtree(project_dir_path)


def test_save_project_given_details():
    project = Project()

    project.project_path = Path(ROOT_DIR / 'mock_otlwizard_project_dir' / 'project_2')
    project.subset_path = Path(ROOT_DIR / 'mock_otlwizard_project_dir' / 'project_1' / 'OTL_AllCasesTestClass.db')
    project.assets_path = Path(ROOT_DIR / 'mock_otlwizard_project_dir' / 'project_2' / 'assets.json')
    project.eigen_referentie = "eigen referentie"
    project.bestek = "bestek"
    project.laatst_bewerkt = datetime.datetime(2023, 11, 1)

    orig_get_otl_wizard_projects_dir = ProjectFileManager.get_otl_wizard_projects_dir

    ProjectFileManager.get_otl_wizard_projects_dir = lambda: Path(ROOT_DIR / 'mock_otlwizard_project_dir')
    ProjectFileManager.save_project_to_dir(project)

    project_dir_path = ROOT_DIR / 'mock_otlwizard_project_dir' / 'project_2'
    assert project_dir_path.exists()
    assert (project_dir_path / 'project_details.json').exists()
    assert (project_dir_path / 'OTL_AllCasesTestClass.db').exists()
    assert (project_dir_path / 'assets.json').exists()

    generated_project = ProjectFileManager.get_project_from_dir(project_dir_path)
    assert generated_project.eigen_referentie == "eigen referentie"
    assert generated_project.bestek == "bestek"
    assert generated_project.laatst_bewerkt == datetime.datetime(2023, 11, 1)

    shutil.rmtree(project_dir_path)

    ProjectFileManager.get_otl_wizard_projects_dir = orig_get_otl_wizard_projects_dir


def test_get_all_otl_wizard_projects(caplog):
    orig_get_otl_wizard_projects_dir = ProjectFileManager.get_otl_wizard_projects_dir

    ProjectFileManager.get_otl_wizard_projects_dir = lambda: Path(ROOT_DIR / 'mock_otlwizard_project_dir')

    projects = ProjectFileManager.get_all_otl_wizard_projects()
    assert len(projects) == 1
    assert projects[0].project_path == Path(ROOT_DIR / 'mock_otlwizard_project_dir' / 'project_1')
    assert len(caplog.records) == 1

    ProjectFileManager.get_otl_wizard_projects_dir = orig_get_otl_wizard_projects_dir


def test_get_all_otl_wizard_projects_wrong_directory():
    orig_get_otl_wizard_projects_dir = ProjectFileManager.get_otl_wizard_projects_dir

    ProjectFileManager.get_otl_wizard_projects_dir = lambda: Path(ROOT_DIR / 'wrong_dir')
    projects = ProjectFileManager.get_all_otl_wizard_projects()
    assert projects == []

    ProjectFileManager.get_otl_wizard_projects_dir = orig_get_otl_wizard_projects_dir


def test_get_otl_wizard_projects_dir():
    home_dir = os.path.expanduser('~')
    otl_wizard_dir_using_os = Path(os.path.join(home_dir, 'OTLWizardProjects'))

    otl_wizard_projects_dir = ProjectFileManager.get_otl_wizard_projects_dir()

    assert otl_wizard_projects_dir == otl_wizard_dir_using_os

