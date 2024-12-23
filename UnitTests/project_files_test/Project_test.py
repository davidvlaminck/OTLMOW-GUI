import datetime
import os
import shutil
import zipfile
from pathlib import Path

import pytest
from _pytest.fixtures import fixture

from Domain import global_vars
from Domain.enums import FileState
from Domain.project.ProgramFileStructure import ProgramFileStructure
from Domain.project.Project import Project
from Domain.project.ProjectFile import ProjectFile

from UnitTests.general_fixtures.GUIFixtures import *
from UnitTests.general_fixtures.DomainFixtures import *

PARENT_OF_THIS_FILE = Path(__file__).parent

@pytest.fixture
def root_directory():
    # This fixture will mock the get_home_path function to make home path a directory in the UnitTests directory
    # and defaults to 'project_files_test' in UnitTests

    yield Path(PARENT_OF_THIS_FILE)


@fixture
def create_mock_project_project_1():
    project_path = Path(PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_1')
    project_backup_path = Path(PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects_backup' / project_path.name)
    # project = Project(
    #     project_path=project_path,
    #     subset_path=Path(
    #         PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_1' /
    #         'OTL_AllCasesTestClass_no_double_kard.db'),
    #     assets_path=Path(
    #         PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_1' / 'saved_documents.json'),
    #     eigen_referentie="project_1",
    #     bestek="bestek",
    #     laatst_bewerkt=datetime.datetime(2023, 11, 1))
    # project.save_project_to_dir()

    project = Project.load_project(project_path)

    yield project
    if project_path.exists():
        shutil.rmtree(project_path)
    shutil.copytree(project_backup_path,project_path)

@fixture
def create_mock_project_project_2():
    project_path = Path(PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_2')
    project = Project(eigen_referentie="eigen referentie", project_path=project_path,
                      subset_path=Path(
                          PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_1' /
                          'OTL_AllCasesTestClass_no_double_kard.db'),
                      saved_documents_overview_path=Path(
                          PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_2' / 'saved_documents.json'),
                      bestek="bestek", laatst_bewerkt=datetime.datetime(2023, 11, 1))

    project.save_project_to_dir()
    yield project
    if project_path.exists():
        shutil.rmtree(project_path)

@fixture
def create_mock_project_project_3():
    project_path = Path(PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_2')
    project_backup_path = Path(
        PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects_backup' / project_path.name)

    project = Project(eigen_referentie="eigen referentie", project_path=project_path,
                      subset_path=Path(
                          PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_1' /
                          'OTL_AllCasesTestClass_no_double_kard.db'),
                      saved_documents_overview_path=Path(
                          PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_2' / 'saved_documents.json'),
                      bestek="bestek", laatst_bewerkt=datetime.datetime(2023, 11, 1))

    project.save_project_to_dir()
    yield project
    if project_path.exists():
        shutil.rmtree(project_path)
    shutil.copytree(project_backup_path,project_path)


@fixture
def create_mock_project_project_4():
    project_path = Path(ProgramFileStructure.get_otl_wizard_projects_dir() / 'project_4')
    project = Project(eigen_referentie="eigen referentie", project_path=project_path,
                      subset_path=Path(
                          PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_1' /
                          'OTL_AllCasesTestClass_no_double_kard.db'),
                      saved_documents_overview_path=Path(
                          PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_1' / 'saved_documents.json'),
                      bestek="bestek", laatst_bewerkt=datetime.datetime(2023, 11, 1))
    project.save_project_to_dir()
    yield project
    if project_path.exists():
        shutil.rmtree(project_path)

@fixture
def create_mock_project_eigen_referentie():
    project_path = Path(PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'eigen referentie')
    project_backup_path = Path(
        PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects_backup' / project_path.name)

    if not project_path.exists():
        shutil.copytree(project_backup_path,project_path)

    yield

    if project_path.exists():
        shutil.rmtree(project_path)


def test_get_project_from_dir_given_project_dir_location(create_mock_project_project_1: Project):
    project_dir_path = PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_1'

    project = Project.load_project(project_dir_path)

    assert project.project_path == Path(PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_1')
    assert project.subset_path == Path(
        PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_1' /
        'OTL_AllCasesTestClass_no_double_kard.db')
    assert project.saved_documents_overview_path == Path(
        PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_1' / 'saved_documents.json')
    assert project.eigen_referentie == "project_1"
    assert project.bestek == "bestek"
    assert project.laatst_bewerkt == datetime.datetime(2023, 11, 1)


def test_get_project_from_dir_project_dir_missing():
    project_dir_path = PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_missing'

    with pytest.raises(FileNotFoundError):
        Project.load_project(project_dir_path)


def test_get_project_from_dir_details_missing():
    project_dir_path = PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_details_missing'
    project_dir_path.mkdir(exist_ok=True, parents=True)

    with pytest.raises(FileNotFoundError):
        Project.load_project(project_dir_path)

    shutil.rmtree(project_dir_path)


def test_save_project_given_details(mock_project_home_path,create_mock_project_eigen_referentie):


    project_dir_path = PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'eigen referentie'
    assert project_dir_path.exists()
    assert (project_dir_path / 'project_details.json').exists()
    assert (project_dir_path / 'OTL_AllCasesTestClass_no_double_kard.db').exists()
    # assert (project_dir_path / 'saved_documents.json').exists() #is not supposed to be created

    generated_project = Project.load_project(project_dir_path)
    assert generated_project.eigen_referentie == "eigen referentie"
    assert generated_project.bestek == "bestek"
    assert generated_project.laatst_bewerkt == datetime.datetime(2023, 11, 1)

    shutil.rmtree(project_dir_path)

def test_export_project_to_file(mock_project_home_path,create_mock_project_project_1: Project):
    project = create_mock_project_project_1
    file_path = Path(PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_1.otlw')

    project.export_project_to_file(file_path=file_path)

    assert file_path.exists()

    with zipfile.ZipFile(file_path) as project_zip:
        list_of_files = sorted(project_zip.namelist())
    assert list_of_files == ['OTL_AllCasesTestClass_no_double_kard.db', 'project_details.json']

    os.remove(file_path)


def test_import_project(mock_project_home_path, create_mock_project_project_1: Project, cleanup_after_creating_a_file_to_delete):
    project = create_mock_project_project_1
    file_path = Path(PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_extract_and_load.otlw')

    cleanup_after_creating_a_file_to_delete.append(file_path)

    project.export_project_to_file(file_path=file_path)
    # project directory is deleted but the data is kept in memory
    project.delete_project_dir_by_path()
    assert file_path.exists()

    project_loaded = Project.import_project(file_path=file_path)
    assert project_loaded.project_path == Path(
        PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_1')
    assert project_loaded.subset_path == Path(
        PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_1' /
        'OTL_AllCasesTestClass_no_double_kard.db')
    assert project_loaded.saved_documents_overview_path == Path(
        PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_1' / 'saved_documents.json')
    assert project_loaded.eigen_referentie == project.eigen_referentie
    assert project_loaded.bestek == project.bestek
    assert project_loaded.laatst_bewerkt == project.laatst_bewerkt


def test_delete_project_removes_correct_project(create_mock_project_project_4: Project):
    project = create_mock_project_project_4
    assert project.project_path.exists()
    project.delete_project_dir_by_path()
    assert not project.project_path.exists()


def test_add_template_file_generates_folder(create_mock_project_project_4: Project):
    project = create_mock_project_project_4

    assert project.project_path.exists()
    project.make_copy_of_added_file(Path(
        PARENT_OF_THIS_FILE) / 'OTLWizardProjects' / 'TestFiles' / 'should_pass_implementatieelement_Derdenobject.csv')

    location_dir = project.get_project_files_dir_path()
    if not location_dir.exists():
        old_path = project.get_old_project_files_dir_path()
        if old_path.exists():
            location_dir = old_path
        else:
            location_dir.mkdir()

    assert location_dir.exists()
    project.delete_project_dir_by_path()

def test_delete_template_file_from_project(
        cleanup_after_creating_a_file_to_delete,create_mock_project_project_1):
    project = create_mock_project_project_1

    testFilePath = Path(PARENT_OF_THIS_FILE.parent / 'project_files_test' /
                        'OTLWizardProjects' / 'Projects' / 'project_1' /
                        'testFileToRemove.txt')

    project.saved_project_files.append(ProjectFile(testFilePath,FileState.ERROR))

    with open(testFilePath , 'w+') as fp:
        fp.write("This is a textfile not a sqllite file")

    # add path to testfile to the to_delete list so it gets deleted
    # after the test is done this fixture will continue running from the yield
    cleanup_after_creating_a_file_to_delete.append(testFilePath)

    assert project.remove_project_file(testFilePath)

    assert not os.path.exists(testFilePath)


def test_delete_non_existent_file_from_project(
        cleanup_after_creating_a_file_to_delete,create_mock_project_project_1):
    project = create_mock_project_project_1
    fakeTestFilePath = Path(PARENT_OF_THIS_FILE.parent / 'project_files_test' /
                            'OTLWizardProjects' / 'Projects' / 'project_1' /
                            'fakeTestFileToRemove.txt')

    assert not project.remove_project_file(
        fakeTestFilePath)



def test_remove_template_folder_removes_folder(create_mock_project_project_4: Project):
    project = create_mock_project_project_4

    assert project.project_path.exists()
    project.make_copy_of_added_file(Path(
        PARENT_OF_THIS_FILE) / 'OTLWizardProjects' / 'TestFiles' / 'should_pass_implementatieelement_Derdenobject.csv')

    location_dir = project.get_project_files_dir_path()
    if not location_dir.exists():
        old_path = project.get_old_project_files_dir_path()
        if old_path.exists():
            location_dir = old_path
        else:
            location_dir.mkdir()

    assert location_dir.exists()
    project.delete_template_folder()
    assert not location_dir.exists()
    project.delete_project_dir_by_path()


def test_correct_project_files_in_memory_returns_false_if_project_has_no_templates_in_memory(create_mock_project_project_4):
    project = create_mock_project_project_4
    assert not project.are_all_project_files_in_memory_valid()


def test_correct_project_files_in_memory_returns_true_if_ok_files_in_memory(create_mock_project_project_4):
    project = create_mock_project_project_4
    project_file = ProjectFile(file_path=Path(
        PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'TestFiles' / 'should_pass_implementatieelement_Derdenobject.csv'),
        state=FileState.OK)
    project.saved_project_files.append(project_file)
    assert project.are_all_project_files_in_memory_valid()


def test_correct_project_files_in_memory_returns_false_if_no_ok_files_in_memory(create_mock_project_project_4: Project):
    project = create_mock_project_project_4
    project_file = ProjectFile(file_path=Path(
        PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'TestFiles' / 'should_pass_implementatieelement_Derdenobject.csv'),
        state=FileState.ERROR)
    project.saved_project_files.append(project_file)
    assert project.are_all_project_files_in_memory_valid() is False