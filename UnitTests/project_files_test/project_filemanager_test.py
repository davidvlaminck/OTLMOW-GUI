import datetime
import os
import shutil
import zipfile
from pathlib import Path

import pytest

from Domain.Project import Project
from Domain.ProjectFileManager import ProjectFileManager

PARENT_OF_THIS_FILE = Path(__file__).parent


@pytest.fixture
def mock_get_otl_wizard_projects_dir(mocked_dir='mock_otlwizard_dir/Projects'):
    # This fixture will mock the get_otl_wizard_projects_dir function to return a directory in the UnitTests directory
    # and defaults to 'mock_otlwizard_dir' / 'Projects'
    orig_get_otl_wizard_projects_dir = ProjectFileManager.get_otl_wizard_projects_dir
    ProjectFileManager.get_otl_wizard_projects_dir = lambda: Path(PARENT_OF_THIS_FILE / mocked_dir)
    yield
    ProjectFileManager.get_otl_wizard_projects_dir = orig_get_otl_wizard_projects_dir


def test_get_project_from_dir_given_project_dir_location():
    project_dir_path = PARENT_OF_THIS_FILE / 'mock_otlwizard_dir' / 'Projects' / 'project_1'

    project = ProjectFileManager.get_project_from_dir(project_dir_path)

    assert project.project_path == Path(PARENT_OF_THIS_FILE / 'mock_otlwizard_dir' / 'Projects' / 'project_1')
    assert project.subset_path == Path(
        PARENT_OF_THIS_FILE / 'mock_otlwizard_dir' / 'Projects' / 'project_1' / 'OTL_AllCasesTestClass.db')
    assert project.assets_path == Path(PARENT_OF_THIS_FILE / 'mock_otlwizard_dir' / 'Projects' / 'project_1' / 'assets.json')
    assert project.eigen_referentie == "eigen referentie"
    assert project.bestek == "bestek"
    assert project.laatst_bewerkt == datetime.datetime(2023, 11, 1)


def test_get_project_from_dir_project_dir_missing():
    project_dir_path = PARENT_OF_THIS_FILE / 'mock_otlwizard_dir' / 'Projects' / 'project_missing'

    with pytest.raises(FileNotFoundError):
        ProjectFileManager.get_project_from_dir(project_dir_path)


def test_get_project_from_dir_details_missing():
    project_dir_path = PARENT_OF_THIS_FILE / 'mock_otlwizard_dir' / 'Projects' / 'project_details_missing'
    project_dir_path.mkdir(exist_ok=True, parents=True)

    with pytest.raises(FileNotFoundError):
        ProjectFileManager.get_project_from_dir(project_dir_path)

    shutil.rmtree(project_dir_path)


def test_save_project_given_details(mock_get_otl_wizard_projects_dir):
    project = Project(
        project_path=Path(PARENT_OF_THIS_FILE / 'mock_otlwizard_dir' / 'Projects' / 'project_2'),
        subset_path=Path(PARENT_OF_THIS_FILE / 'mock_otlwizard_dir' / 'Projects' / 'project_1' / 'OTL_AllCasesTestClass.db'),
        assets_path=Path(PARENT_OF_THIS_FILE / 'mock_otlwizard_dir' / 'Projects' / 'project_2' / 'assets.json'),
        eigen_referentie="eigen referentie",
        bestek="bestek",
        laatst_bewerkt=datetime.datetime(2023, 11, 1))

    ProjectFileManager.save_project_to_dir(project)

    project_dir_path = PARENT_OF_THIS_FILE / 'mock_otlwizard_dir' / 'Projects' / 'project_2'
    assert project_dir_path.exists()
    assert (project_dir_path / 'project_details.json').exists()
    assert (project_dir_path / 'OTL_AllCasesTestClass.db').exists()
    assert (project_dir_path / 'assets.json').exists()

    generated_project = ProjectFileManager.get_project_from_dir(project_dir_path)
    assert generated_project.eigen_referentie == "eigen referentie"
    assert generated_project.bestek == "bestek"
    assert generated_project.laatst_bewerkt == datetime.datetime(2023, 11, 1)

    shutil.rmtree(project_dir_path)


# KAPUTT
def test_get_all_otl_wizard_projects(caplog, mock_get_otl_wizard_projects_dir):
    projects = ProjectFileManager.get_all_otl_wizard_projects()
    assert len(projects) == 1
    assert projects[0].project_path == Path(PARENT_OF_THIS_FILE / 'mock_otlwizard_dir' / 'Projects' / 'project_1')
    assert len(caplog.records) == 1


def test_get_all_otl_wizard_projects_wrong_directory(mock_get_otl_wizard_projects_dir):
    orig_get_otl_wizard_projects_dir = ProjectFileManager.get_otl_wizard_projects_dir
    ProjectFileManager.get_otl_wizard_projects_dir = lambda: Path(PARENT_OF_THIS_FILE / 'mock_otlwizard_dir' / 'Projects' / 'bad_dir')

    projects = ProjectFileManager.get_all_otl_wizard_projects()
    assert projects == []

    ProjectFileManager.get_otl_wizard_projects_dir = orig_get_otl_wizard_projects_dir


def test_get_otl_wizard_projects_dir():
    home_dir = os.path.expanduser('~')
    otl_wizard_dir_using_os = Path(os.path.join(home_dir, 'OTLWizardProjects/Projects'))

    otl_wizard_projects_dir = ProjectFileManager.get_otl_wizard_projects_dir()

    assert otl_wizard_projects_dir == otl_wizard_dir_using_os


def test_export_project_to_file(mock_get_otl_wizard_projects_dir):
    project = Project(
        project_path=Path(PARENT_OF_THIS_FILE / 'mock_otlwizard_dir' / 'Projects' / 'project_1'),
        subset_path=Path(PARENT_OF_THIS_FILE / 'mock_otlwizard_dir' / 'Projects' / 'project_1' / 'OTL_AllCasesTestClass.db'),
        assets_path=Path(PARENT_OF_THIS_FILE / 'mock_otlwizard_dir' / 'Projects' / 'project_1' / 'assets.json'),
        eigen_referentie="eigen referentie",
        bestek="bestek",
        laatst_bewerkt=datetime.datetime(2023, 11, 1))
    file_path = Path(PARENT_OF_THIS_FILE / 'mock_otlwizard_dir' / 'Projects' / 'project_1.otlw')

    ProjectFileManager.export_project_to_file(project=project, file_path=file_path)

    assert file_path.exists()

    with zipfile.ZipFile(file_path) as project_zip:
        list_of_files = sorted(project_zip.namelist())
    assert list_of_files == ['OTL_AllCasesTestClass.db', 'assets.json', 'project_details.json']

    os.remove(file_path)


def test_load_project_file(mock_get_otl_wizard_projects_dir):
    project = Project(
        project_path=Path(PARENT_OF_THIS_FILE / 'mock_otlwizard_dir' / 'Projects' / 'project_1'),
        subset_path=Path(PARENT_OF_THIS_FILE / 'mock_otlwizard_dir' / 'Projects' / 'project_1' / 'OTL_AllCasesTestClass.db'),
        assets_path=Path(PARENT_OF_THIS_FILE / 'mock_otlwizard_dir' / 'Projects' / 'project_1' / 'assets.json'),
        eigen_referentie="eigen referentie",
        bestek="bestek",
        laatst_bewerkt=datetime.datetime(2023, 11, 1))
    file_path = Path(PARENT_OF_THIS_FILE / 'mock_otlwizard_dir' / 'Projects' / 'project_extract_and_load.otlw')

    ProjectFileManager.export_project_to_file(project=project, file_path=file_path)

    assert file_path.exists()

    project_loaded = ProjectFileManager.load_project_file(file_path=file_path)
    assert project_loaded.project_path == Path(
        PARENT_OF_THIS_FILE / 'mock_otlwizard_dir' / 'Projects' / 'project_extract_and_load')
    assert project_loaded.subset_path == Path(
        PARENT_OF_THIS_FILE / 'mock_otlwizard_dir' / 'Projects' / 'project_extract_and_load' / 'OTL_AllCasesTestClass.db')
    assert project_loaded.assets_path == Path(
        PARENT_OF_THIS_FILE / 'mock_otlwizard_dir' / 'Projects' / 'project_extract_and_load' / 'assets.json')
    assert project_loaded.eigen_referentie == project.eigen_referentie
    assert project_loaded.bestek == project.bestek
    assert project_loaded.laatst_bewerkt == project.laatst_bewerkt

    os.remove(file_path)
    shutil.rmtree(Path(PARENT_OF_THIS_FILE / 'mock_otlwizard_dir' / 'Projects' / 'project_extract_and_load'))
