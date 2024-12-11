import datetime
import os
import shutil
import tempfile
import zipfile
from pathlib import Path

import pytest
from _pytest.fixtures import fixture

from Domain import global_vars
from Domain.Project import Project
from Domain.ProjectFileManager import ProjectFileManager
from Domain.enums import FileState
from Domain.ProjectFile import ProjectFile
from Exceptions.ExcelFileUnavailableError import ExcelFileUnavailableError

PARENT_OF_THIS_FILE = Path(__file__).parent

@fixture
def create_mock_project_project_1():
    project_path = Path(PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_1')
    project = Project(
        project_path=project_path,
        subset_path=Path(
            PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_1' /
            'OTL_AllCasesTestClass_no_double_kard.db'),
        assets_path=Path(
            PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_1' / 'saved_documents.json'),
        eigen_referentie="eigen referentie",
        bestek="bestek",
        laatst_bewerkt=datetime.datetime(2023, 11, 1))

    # ProjectFileManager.save_project_to_dir(project)
    yield project
    # if project_path.exists():
    #     shutil.rmtree(project_path)

@fixture
def create_mock_project_project_2():
    project_path = Path(PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_2')
    project = Project(
        project_path=project_path,
        subset_path=Path(
            PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_1' /
            'OTL_AllCasesTestClass_no_double_kard.db'),
        assets_path=Path(
            PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_2' / 'saved_documents.json'),
        eigen_referentie="eigen referentie",
        bestek="bestek",
        laatst_bewerkt=datetime.datetime(2023, 11, 1))

    ProjectFileManager.save_project_to_dir(project)
    yield project
    if project_path.exists():
        shutil.rmtree(project_path)

@fixture
def create_mock_project_project_3():
    project_path = Path(PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_2')
    project = Project(
        project_path=project_path,
        subset_path=Path(
            PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_1' /
            'OTL_AllCasesTestClass_no_double_kard.db'),
        assets_path=Path(
            PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_2' / 'saved_documents.json'),
        eigen_referentie="eigen referentie",
        bestek="bestek",
        laatst_bewerkt=datetime.datetime(2023, 11, 1))

    # ProjectFileManager.save_project_to_dir(project)
    yield project
    # if project_path.exists():
    #     shutil.rmtree(project_path)

@fixture
def create_mock_project_project_4():
    project_path = Path(ProjectFileManager.get_otl_wizard_projects_dir() / 'project_4')
    project = Project(
        project_path=project_path ,
        subset_path=Path(PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_1' /
                         'OTL_AllCasesTestClass_no_double_kard.db'),
        assets_path=Path(
            PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_1' / 'saved_documents.json'),
        eigen_referentie="eigen referentie",
        bestek="bestek",
        laatst_bewerkt=datetime.datetime(2023, 11, 1))
    ProjectFileManager.save_project_to_dir(project)
    yield project
    if project_path.exists():
        shutil.rmtree(project_path)

@fixture
def create_mock_project_eigen_referentie():
    project_path = Path(PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_2')
    project = Project(
        project_path=project_path,
        subset_path=Path(
            PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_1' /
            'OTL_AllCasesTestClass_no_double_kard.db'),
        assets_path=Path(
            PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_2' / 'saved_documents.json'),
        eigen_referentie="eigen referentie",
        bestek="bestek",
        laatst_bewerkt=datetime.datetime(2023, 11, 1))

    ProjectFileManager.save_project_to_dir(project)
    yield project
    if project_path.exists():
        shutil.rmtree(project_path)

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


def test_get_project_from_dir_given_project_dir_location(create_mock_project_project_1):
    project_dir_path = PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_1'

    project = ProjectFileManager.get_project_from_dir(project_dir_path)

    assert project.project_path == Path(PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_1')
    assert project.subset_path == Path(
        PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_1' /
        'OTL_AllCasesTestClass_no_double_kard.db')
    assert project.assets_path == Path(
        PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_1' / 'saved_documents.json')
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


def test_save_project_given_details(mock_get_home_path,create_mock_project_eigen_referentie):


    project_dir_path = PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_2'
    assert project_dir_path.exists()
    assert (project_dir_path / 'project_details.json').exists()
    assert (project_dir_path / 'OTL_AllCasesTestClass_no_double_kard.db').exists()
    # assert (project_dir_path / 'saved_documents.json').exists() #is not supposed to be created

    generated_project = ProjectFileManager.get_project_from_dir(project_dir_path)
    assert generated_project.eigen_referentie == "eigen referentie"
    assert generated_project.bestek == "bestek"
    assert generated_project.laatst_bewerkt == datetime.datetime(2023, 11, 1)

    shutil.rmtree(project_dir_path)


def test_get_all_otl_wizard_projects(caplog, mock_get_home_path):
    projects = ProjectFileManager.get_all_otl_wizard_projects()
    assert len(projects) == 1
    assert projects[1].project_path == Path(PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_1')
    assert len(caplog.records) == 2


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


def test_export_project_to_file(mock_get_home_path,create_mock_project_project_1):
    project = create_mock_project_project_1
    file_path = Path(PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_1.otlw')

    ProjectFileManager.export_project_to_file(project=project, file_path=file_path)

    assert file_path.exists()

    with zipfile.ZipFile(file_path) as project_zip:
        list_of_files = sorted(project_zip.namelist())
    assert list_of_files == ['OTL_AllCasesTestClass_no_double_kard.db', 'project_details.json']

    os.remove(file_path)


def test_load_project_file(mock_get_home_path,create_mock_project_project_1):
    project = create_mock_project_project_1
    file_path = Path(PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_extract_and_load.otlw')

    ProjectFileManager.export_project_to_file(project=project, file_path=file_path)

    assert file_path.exists()

    project_loaded = ProjectFileManager.load_project_file(file_path=file_path)
    assert project_loaded.project_path == Path(
        PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_extract_and_load')
    assert project_loaded.subset_path == Path(
        PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_extract_and_load' /
        'OTL_AllCasesTestClass_no_double_kard.db')
    assert project_loaded.assets_path == Path(
        PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_extract_and_load' / 'saved_documents.json')
    assert project_loaded.eigen_referentie == project.eigen_referentie
    assert project_loaded.bestek == project.bestek
    assert project_loaded.laatst_bewerkt == project.laatst_bewerkt

    os.remove(file_path)
    shutil.rmtree(Path(PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_extract_and_load'))


def test_delete_project_removes_correct_project(create_mock_project_project_4):
    project = create_mock_project_project_4
    assert project.project_path.exists()
    ProjectFileManager.delete_project_files_by_path(project.project_path)
    assert not project.project_path.exists()


def test_add_template_file_generates_folder(create_mock_project_project_4):
    project = create_mock_project_project_4()
    global_vars.current_project = project
    assert project.project_path.exists()
    ProjectFileManager.make_copy_of_added_file(Path(
        PARENT_OF_THIS_FILE) / 'OTLWizardProjects' / 'TestFiles' / 'should_pass_implementatieelement_Derdenobject.csv')
    assert (project.project_path / 'OTL-template-files').exists()
    ProjectFileManager.delete_project_files_by_path(project.project_path)
    global_vars.current_project = None


def test_remove_template_folder_removes_folder(create_mock_project_project_4):
    project = create_mock_project_project_4
    global_vars.current_project = project
    assert project.project_path.exists()
    ProjectFileManager.make_copy_of_added_file(Path(
        PARENT_OF_THIS_FILE) / 'OTLWizardProjects' / 'TestFiles' / 'should_pass_implementatieelement_Derdenobject.csv')
    assert (project.project_path / 'OTL-template-files').exists()
    ProjectFileManager.delete_template_folder()
    assert not (project.project_path / 'OTL-template-files').exists()
    ProjectFileManager.delete_project_files_by_path(project.project_path)
    global_vars.current_project = None


def test_correct_project_files_in_memory_returns_false_if_none_given_as_param():
    assert not ProjectFileManager.correct_project_files_in_memory(None)


def test_correct_project_files_in_memory_returns_false_if_project_has_no_templates_in_memory(create_mock_project_project_4):
    project = create_mock_project_project_4
    assert not ProjectFileManager.correct_project_files_in_memory(project)


def test_correct_project_files_in_memory_returns_true_if_ok_files_in_memory(create_mock_project_project_4):
    project = create_mock_project_project_4
    project_file = ProjectFile(file_path=Path(
        PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'TestFiles' / 'should_pass_implementatieelement_Derdenobject.csv'),
        state=FileState.OK)
    project.saved_project_files.append(project_file)
    assert ProjectFileManager.correct_project_files_in_memory(project) is True


def test_correct_project_files_in_memory_returns_false_if_no_ok_files_in_memory(create_mock_project_project_4):
    project = create_mock_project_project_4
    project_file = ProjectFile(file_path=Path(
        PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'TestFiles' / 'should_pass_implementatieelement_Derdenobject.csv'),
        state=FileState.ERROR)
    project.saved_project_files.append(project_file)
    assert ProjectFileManager.correct_project_files_in_memory(project) is False


def test_create_empty_temporary_map_creates_map_in_correct_location():
    temp_loc = Path(tempfile.gettempdir()) / 'temp-otlmow'
    temp_loc.rmdir()
    tempdir = ProjectFileManager.create_empty_temporary_map()
    Path(tempfile.gettempdir()) / 'temp-otlmow'
    assert tempdir == Path(tempfile.gettempdir()) / 'temp-otlmow'


def test_create_empty_temporary_map_contains_no_files():
    tempdir = ProjectFileManager.create_empty_temporary_map()
    assert not os.listdir(tempdir)

@fixture
def cleanup_after_creating_a_file_to_delete():
    to_delete = []
    yield to_delete
    for item in to_delete:
        if os.path.exists(item):
            os.remove(item)

"""
Test the deletion of a template file from a project. This function verifies 
that a specified file is successfully removed from the project directory.

It creates a temporary file, adds its path to a cleanup list, and then calls 
the method responsible for deleting the file. After the deletion, it asserts 
that the file no longer exists.

Args:
    cleanupAfterCreatingAFileToDelete (list):   A list that tracks files to be 
                                                deleted after the test 
                                                completes.

Returns:
    None
"""

def test_delete_template_file_from_project(
        cleanup_after_creating_a_file_to_delete):
    testFilePath = Path(PARENT_OF_THIS_FILE.parent / 'project_files_test' /
                        'OTLWizardProjects' / 'Projects' / 'project_1' /
                        'testFileToRemove.txt')

    with open(testFilePath , 'w+') as fp:
        fp.write("This is a textfile not a sqllite file")

    # add path to testfile to the to_delete list so it gets deleted
    # after the test is done this fixture will continue running from the yield
    cleanup_after_creating_a_file_to_delete.append(testFilePath)

    assert ProjectFileManager.delete_template_file_from_project(testFilePath)

    assert not os.path.exists(testFilePath)


def test_delete_non_existent_file_from_project(
        cleanup_after_creating_a_file_to_delete):
    fakeTestFilePath = Path(PARENT_OF_THIS_FILE.parent / 'project_files_test' /
                            'OTLWizardProjects' / 'Projects' / 'project_1' /
                            'fakeTestFileToRemove.txt')

    assert not ProjectFileManager.delete_template_file_from_project(
        fakeTestFilePath)

@pytest.mark.skip
def test_delete_occupied_template_file_from_project(
                                            cleanup_after_creating_a_file_to_delete):
    test_file_path = Path(PARENT_OF_THIS_FILE.parent / 'project_files_test' /
                        'OTLWizardProjects' / 'Projects' / 'project_1' /
                        'testFileToRemove.txt')

    # add path to testfile to the to_delete list so it gets deleted
    # after the test is done this fixture will continue running from the yield
    cleanup_after_creating_a_file_to_delete.append(test_file_path)

    with open(test_file_path, 'w+') as fp:
        fp.write("This is a textfile not a sqllite file")

    #TODO: figure out why this doesn't work on github pipeline
    with pytest.raises(ExcelFileUnavailableError) as e:
        ProjectFileManager.delete_template_file_from_project(test_file_path)

        assert e.value.file_path ==  test_file_path