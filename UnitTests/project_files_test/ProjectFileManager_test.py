import datetime
import os
import shutil
import tempfile
import zipfile
from pathlib import Path

import pytest
from _pytest.fixtures import fixture

from Domain import global_vars
from Domain.project.ProgramFileStructure import ProgramFileStructure
from Domain.project.Project import Project
from Domain.project.ProgramFileManager import ProgramFileManager
from Domain.enums import FileState
from Domain.project.ProjectFile import ProjectFile
from Exceptions.ExcelFileUnavailableError import ExcelFileUnavailableError

from UnitTests.general_fixtures.GUIFixtures import *
from UnitTests.general_fixtures.DomainFixtures import *

PARENT_OF_THIS_FILE = Path(__file__).parent


@pytest.fixture
def root_directory():
    # This fixture will mock the get_home_path function to make home path a directory in the UnitTests directory
    # and defaults to 'project_files_test' in UnitTests

    yield Path(PARENT_OF_THIS_FILE)



@pytest.fixture
def mock_get_home_path_with_empty_directory():
    empty_dir = Path(PARENT_OF_THIS_FILE) / 'empty_dir'
    empty_dir.mkdir()

    orig_get_home_path = ProgramFileStructure.get_home_path
    ProgramFileStructure.get_home_path = lambda: empty_dir

    yield

    ProgramFileStructure.get_home_path = orig_get_home_path
    shutil.rmtree(empty_dir)





def test_get_all_otl_wizard_projects(caplog, mock_project_home_path):
    projects = ProgramFileManager.get_all_otl_wizard_projects()
    assert len(projects) == 1
    assert projects[0].project_path == Path(PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_1')
    assert len(caplog.records) == 1


def test_create_otl_wizard_model_dir(mock_get_home_path_with_empty_directory):
    path = ProgramFileStructure.get_otl_wizard_model_dir()
    assert path == Path(PARENT_OF_THIS_FILE / 'empty_dir' / 'OTLWizardProjects' / 'Model')


def test_get_all_otl_wizard_projects_empty_directory(mock_get_home_path_with_empty_directory):
    projects = ProgramFileManager.get_all_otl_wizard_projects()
    assert projects == []


def test_get_otl_wizard_projects_dir():
    home_dir = os.path.expanduser('~')
    otl_wizard_dir_using_os = Path(os.path.join(home_dir, 'OTLWizardProjects/Projects'))

    otl_wizard_projects_dir = ProgramFileStructure.get_otl_wizard_projects_dir()

    assert otl_wizard_projects_dir == otl_wizard_dir_using_os


def test_create_empty_temporary_map_creates_map_in_correct_location():
    temp_loc = Path(tempfile.gettempdir()) / 'temp-otlmow'
    temp_loc.rmdir()
    tempdir = ProgramFileManager.create_empty_temporary_map()
    Path(tempfile.gettempdir()) / 'temp-otlmow'
    assert tempdir == Path(tempfile.gettempdir()) / 'temp-otlmow'


def test_create_empty_temporary_map_contains_no_files():
    tempdir = ProgramFileManager.create_empty_temporary_map()
    assert not os.listdir(tempdir)



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
        ProgramFileManager.delete_template_file_from_project(test_file_path)

        assert e.value.file_path ==  test_file_path