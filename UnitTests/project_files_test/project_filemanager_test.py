import datetime
import os
import shutil
import zipfile
from pathlib import Path

import pytest

from Domain import GitHubDownloader, global_vars
from Domain.Project import Project
from Domain.ProjectFileManager import ProjectFileManager

PARENT_OF_THIS_FILE = Path(__file__).parent


@pytest.fixture
def mock_get_home_path(mocked_dir=Path(PARENT_OF_THIS_FILE)):
    # This fixture will mock the get_home_path function to make home path a directory in the UnitTests directory
    # and defaults to 'project_files_test' in UnitTests
    orig_get_home_path = ProjectFileManager.get_home_path
    ProjectFileManager.get_home_path = lambda: mocked_dir
    yield
    ProjectFileManager.get_home_path = orig_get_home_path


@pytest.fixture
def mock_get_home_path_with_empty_directory(mock_get_home_path):
    empty_dir = Path(PARENT_OF_THIS_FILE) / 'empty_dir'
    empty_dir.mkdir()

    orig_get_home_path = ProjectFileManager.get_home_path
    ProjectFileManager.get_home_path = lambda: empty_dir

    yield

    ProjectFileManager.get_home_path = orig_get_home_path
    shutil.rmtree(empty_dir)


def test_get_project_from_dir_given_project_dir_location():
    project_dir_path = PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_1'

    project = ProjectFileManager.get_project_from_dir(project_dir_path)

    assert project.project_path == Path(PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_1')
    assert project.subset_path == Path(
        PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_1' / 'OTL_AllCasesTestClass.db')
    assert project.assets_path == Path(
        PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_1' / 'assets.json')
    assert project.eigen_referentie == "eigen referentie"
    assert project.bestek == "bestek"
    assert project.laatst_bewerkt == datetime.datetime(2023, 11, 1)


def test_get_project_from_dir_project_dir_missing():
    project_dir_path = PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_missing'

    with pytest.raises(FileNotFoundError):
        ProjectFileManager.get_project_from_dir(project_dir_path)


def test_get_project_from_dir_details_missing():
    project_dir_path = PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_details_missing'
    project_dir_path.mkdir(exist_ok=True, parents=True)

    with pytest.raises(FileNotFoundError):
        ProjectFileManager.get_project_from_dir(project_dir_path)

    shutil.rmtree(project_dir_path)


def test_save_project_given_details(mock_get_home_path):
    project = Project(
        project_path=Path(PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_2'),
        subset_path=Path(
            PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_1' / 'OTL_AllCasesTestClass.db'),
        assets_path=Path(PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_2' / 'assets.json'),
        eigen_referentie="eigen referentie",
        bestek="bestek",
        laatst_bewerkt=datetime.datetime(2023, 11, 1))

    ProjectFileManager.save_project_to_dir(project)

    project_dir_path = PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_2'
    assert project_dir_path.exists()
    assert (project_dir_path / 'project_details.json').exists()
    assert (project_dir_path / 'OTL_AllCasesTestClass.db').exists()
    assert (project_dir_path / 'assets.json').exists()

    generated_project = ProjectFileManager.get_project_from_dir(project_dir_path)
    assert generated_project.eigen_referentie == "eigen referentie"
    assert generated_project.bestek == "bestek"
    assert generated_project.laatst_bewerkt == datetime.datetime(2023, 11, 1)

    shutil.rmtree(project_dir_path)


def test_get_all_otl_wizard_projects(caplog, mock_get_home_path):
    projects = ProjectFileManager.get_all_otl_wizard_projects()
    assert len(projects) == 1
    assert projects[0].project_path == Path(PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_1')
    assert len(caplog.records) == 1


def test_create_otl_wizard_model_dir(mock_get_home_path_with_empty_directory):
    path = ProjectFileManager.get_otl_wizard_model_dir()
    assert path == Path(PARENT_OF_THIS_FILE / 'empty_dir' / 'OTLWizardProjects' / 'Model')


def test_get_all_otl_wizard_projects_empty_directory(mock_get_home_path_with_empty_directory):
    projects = ProjectFileManager.get_all_otl_wizard_projects()
    assert projects == []


def test_get_otl_wizard_projects_dir():
    home_dir = os.path.expanduser('~')
    otl_wizard_dir_using_os = Path(os.path.join(home_dir, 'OTLWizardProjects/Projects'))

    otl_wizard_projects_dir = ProjectFileManager.get_otl_wizard_projects_dir()

    assert otl_wizard_projects_dir == otl_wizard_dir_using_os


def test_export_project_to_file(mock_get_home_path):
    project = Project(
        project_path=Path(PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_1'),
        subset_path=Path(
            PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_1' / 'OTL_AllCasesTestClass.db'),
        assets_path=Path(PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_1' / 'assets.json'),
        eigen_referentie="eigen referentie",
        bestek="bestek",
        laatst_bewerkt=datetime.datetime(2023, 11, 1))
    file_path = Path(PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_1.otlw')

    ProjectFileManager.export_project_to_file(project=project, file_path=file_path)

    assert file_path.exists()

    with zipfile.ZipFile(file_path) as project_zip:
        list_of_files = sorted(project_zip.namelist())
    assert list_of_files == ['OTL_AllCasesTestClass.db', 'assets.json', 'project_details.json']

    os.remove(file_path)


def test_load_project_file(mock_get_home_path):
    project = Project(
        project_path=Path(PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_1'),
        subset_path=Path(
            PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_1' / 'OTL_AllCasesTestClass.db'),
        assets_path=Path(PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_1' / 'assets.json'),
        eigen_referentie="eigen referentie",
        bestek="bestek",
        laatst_bewerkt=datetime.datetime(2023, 11, 1))
    file_path = Path(PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_extract_and_load.otlw')

    ProjectFileManager.export_project_to_file(project=project, file_path=file_path)

    assert file_path.exists()

    project_loaded = ProjectFileManager.load_project_file(file_path=file_path)
    assert project_loaded.project_path == Path(
        PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_extract_and_load')
    assert project_loaded.subset_path == Path(
        PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_extract_and_load' / 'OTL_AllCasesTestClass.db')
    assert project_loaded.assets_path == Path(
        PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_extract_and_load' / 'assets.json')
    assert project_loaded.eigen_referentie == project.eigen_referentie
    assert project_loaded.bestek == project.bestek
    assert project_loaded.laatst_bewerkt == project.laatst_bewerkt

    os.remove(file_path)
    shutil.rmtree(Path(PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_extract_and_load'))


def test_delete_project_removes_correct_project():
    project = Project(
        project_path=Path(ProjectFileManager.get_otl_wizard_projects_dir() / 'project_4'),
        subset_path=Path(
            PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_1' / 'OTL_AllCasesTestClass.db'),
        assets_path=Path(PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_1' / 'assets.json'),
        eigen_referentie="eigen referentie",
        bestek="bestek",
        laatst_bewerkt=datetime.datetime(2023, 11, 1))
    ProjectFileManager.save_project_to_dir(project)
    assert project.project_path.exists()
    ProjectFileManager.delete_project_files_by_path(project.project_path)
    assert not project.project_path.exists()


def test_add_template_file_generates_folder():
    project = Project(
        project_path=Path(ProjectFileManager.get_otl_wizard_projects_dir() / 'project_4'),
        subset_path=Path(
            PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_1' / 'OTL_AllCasesTestClass.db'),
        assets_path=Path(PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_1' / 'assets.json'),
        eigen_referentie="eigen referentie",
        bestek="bestek",
        laatst_bewerkt=datetime.datetime(2023, 11, 1))
    ProjectFileManager.save_project_to_dir(project)
    global_vars.single_project = project
    assert project.project_path.exists()
    ProjectFileManager.add_template_file_to_project(Path(
        PARENT_OF_THIS_FILE) / 'OTLWizardProjects' / 'TestFiles' / 'should_pass_implementatieelement_Derdenobject.csv')
    assert (project.project_path / 'OTL-template-files').exists()
    ProjectFileManager.delete_project_files_by_path(project.project_path)
    global_vars.single_project = None


def test_remove_template_folder_removes_folder():
    project = Project(
        project_path=Path(ProjectFileManager.get_otl_wizard_projects_dir() / 'project_4'),
        subset_path=Path(
            PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_1' / 'OTL_AllCasesTestClass.db'),
        assets_path=Path(PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_1' / 'assets.json'),
        eigen_referentie="eigen referentie",
        bestek="bestek",
        laatst_bewerkt=datetime.datetime(2023, 11, 1))
    ProjectFileManager.save_project_to_dir(project)
    global_vars.single_project = project
    assert project.project_path.exists()
    ProjectFileManager.add_template_file_to_project(Path(
        PARENT_OF_THIS_FILE) / 'OTLWizardProjects' / 'TestFiles' / 'should_pass_implementatieelement_Derdenobject.csv')
    assert (project.project_path / 'OTL-template-files').exists()
    ProjectFileManager.delete_template_folder()
    assert not (project.project_path / 'OTL-template-files').exists()
    ProjectFileManager.delete_project_files_by_path(project.project_path)
    global_vars.single_project = None
