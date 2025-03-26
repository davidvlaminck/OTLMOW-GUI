from __future__ import annotations

import datetime
import json
import zipfile
from asyncio import sleep
from copy import deepcopy
from datetime import timedelta
from typing import Union
from unittest.mock import mock_open, patch

import pytest
from otlmow_model.OtlmowModel.BaseClasses.RelationInteractor import RelationInteractor
from otlmow_model.OtlmowModel.Classes.ImplementatieElement.RelatieObject import RelatieObject

from Domain.enums import FileState
from Domain.project.ProjectFile import ProjectFile
from Domain.step_domain.HomeDomain import HomeDomain

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

    if project_path.exists():
        shutil.rmtree(project_path)
    shutil.copytree(project_backup_path,project_path)

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
        sleep(0.05) # sleep to give the system time to copy
    yield

    if project_path.exists():
        shutil.rmtree(project_path)


def add_projects_path(projects_path, value):
    if value:
        return projects_path / value
    else:
        return value

@fixture
def mock_otl_wizard_dir(root_directory):
    original_get_otl_wizard_projects_dir = ProgramFileStructure.get_otl_wizard_projects_dir
    ProgramFileStructure.get_otl_wizard_projects_dir = Mock(return_value=root_directory  / "OTLWizardProjects" / "Projects")

    yield
    ProgramFileStructure.get_otl_wizard_projects_dir = original_get_otl_wizard_projects_dir

@pytest.mark.parametrize(
    "eigen_referentie, project_path, subset_path, saved_documents_overview_path, bestek,"
    "laatst_bewerkt, last_quick_save, subset_operator, otl_version,"
    "expected_project_path, expected_subset_operator, expected_otl_version,"
    "expected_saved_documents_overview_path, expected_last_quick_save",
    [
        # Happy path with all parameters provided
        ("ref1", Path("ref1"), Path("ref1"), Path("ref1/saved_documents.json"),
         "bestek1", datetime.datetime(2023, 10, 1),None,"operator1", "version1",
         # expected values
         Path("ref1"), "operator1", "version1", Path("ref1/saved_documents.json"),
         None),

        # Happy path with minimal parameters
        ("ref2", None, None, None, None, None, None, None, None,
        # expected values
         Path('ref2'), None,None, Path('ref2' , 'saved_documents.json'), None),

        # Edge case with subset_operator and otl_version as Path
        ("ref3", None, None, None, None, None, None, Path("/operator/path"), Path("/version/path"),
        # expected values
         Path('ref3'), "path","path", Path('ref3' , 'saved_documents.json'),None),

        # Edge case with saved_documents_overview_path not ending in .json
        ("ref4", None, None, Path("ref4"), None, None, None, None, None,
        # expected values
         Path('ref4'), None, None, Path("ref4/saved_documents.json"), None),



        # Error case with invalid project_path type
        pytest.param("ref5", "invalid_path", None, None, None, None, None, None, None,
                        # expected values
                     None, None, None, None, None, marks=pytest.mark.xfail(raises=TypeError),
                     id="invalid_project_path_type"),

        # Edge case everything except eigen_reference is None
        ("ref6", None, None, None, None, None, None, None, None,
        # expected values
         Path('ref6'), None,None,  Path("ref6/saved_documents.json"), None),

        # last quick save path is given
        ("ref7", None, None, None, None, None,  Path("save.json"), None, None,
        # expected values
        Path('ref7'), None, None, Path("ref7/saved_documents.json"), Path("ref7/quick_saves/save.json")
        ),

        # project_path_given
        ("ref8", Path("project_ref8"), None, None, None, None, None, None, None,
        # expected values
        Path('project_ref8'), None, None, Path("project_ref8/saved_documents.json"), None)
    ],
    ids=[
        "happy_path_all_params",
        "happy_path_minimal_params",
        "edge_case_operator_version_as_path",
        "edge_case_saved_documents_no_json",
        "error_invalid_project_path_type",
        "edge_case_only_eigen_ref",
        "quick_save_path_given",
        "project_path_given"
    ]
)
def test_project_init(mock_otl_wizard_dir, root_directory, eigen_referentie, project_path,
                      subset_path, saved_documents_overview_path,
                      bestek, laatst_bewerkt, last_quick_save, subset_operator, otl_version,
                      expected_project_path, expected_subset_operator, expected_otl_version,
                      expected_saved_documents_overview_path, expected_last_quick_save):
    projects_dir = Path(root_directory,  "OTLWizardProjects","Projects")
    # Act
    # Adding the path to the project folder to all the relative paths
    eigen_referentie = eigen_referentie
    if isinstance(project_path,Path):
        project_path = add_projects_path(projects_dir,project_path)
    subset_path = add_projects_path(projects_dir, subset_path)
    saved_documents_overview_path = add_projects_path(projects_dir,saved_documents_overview_path)
    last_quick_save = add_projects_path(projects_dir,last_quick_save)


    project = Project(eigen_referentie, project_path,subset_path, saved_documents_overview_path,
                      bestek, laatst_bewerkt, last_quick_save, subset_operator, otl_version)

    # also adding that path to the expected values
    expected_last_quick_save= add_projects_path(projects_dir, expected_last_quick_save)
    expected_project_path = add_projects_path(projects_dir, expected_project_path)
    expected_saved_documents_overview_path = add_projects_path(projects_dir,expected_saved_documents_overview_path)

    # Assert
    assert project.project_path == expected_project_path
    assert project.subset_operator == expected_subset_operator
    assert project.otl_version == expected_otl_version
    assert project.saved_documents_overview_path ==  expected_saved_documents_overview_path
    assert project.last_quick_save == expected_last_quick_save

@fixture
def mock_project_dir(root_directory):
    projects_dir = Path(root_directory, "OTLWizardProjects", "Projects")

    # Adding the path to the project folder to all the relative paths
    project_path = add_projects_path(projects_dir, "ref1")
    if project_path.exists():
        shutil.rmtree(project_path)
    os.mkdir(project_path)
    yield
    shutil.rmtree(project_path)

@pytest.mark.parametrize(
    "eigen_referentie, project_path, subset_path, saved_documents_overview_path, bestek,"
    "laatst_bewerkt, last_quick_save, subset_operator, otl_version,"
    "expected_project_path, expected_subset_operator, expected_otl_version,"
    "expected_saved_documents_overview_path, expected_last_quick_save",
    [
        # Happy path with all parameters provided
        ("ref1", Path("ref1"), Path("ref1"), Path("ref1", "saved_documents.json"),
         "bestek1", datetime.datetime(2023, 10, 1),None,"operator1", "version1",
         # expected values
         Path("ref1"), "operator1", "version1", Path("ref1", "saved_documents.json"),
         None),

        # Happy path with minimal parameters
        ("ref1", None, None, None, None, None, None, None, None,
        # expected values
         Path('ref1'), None,None, Path('ref1' , 'saved_documents.json'), None),

        # Edge case with subset_operator and otl_version as Path
        ("ref1", None, None, None, None, None, None, Path("operator", "path"), Path("version", "path"),
        # expected values
         Path('ref1'), "path","path", Path('ref1' , 'saved_documents.json'),None),

        # Edge case with saved_documents_overview_path not ending in .json
        ("ref1", None, None, Path("ref1"), None, None, None, None, None,
        # expected values
         Path('ref1'), None, None, Path("ref1", "saved_documents.json"), None),

        # Edge case everything except eigen_reference is None
        ("ref1", None, None, None, None, None, None, None, None,
        # expected values
         Path('ref1'), None,None,  Path("ref1", "saved_documents.json"), None),

        # quick_save_path_given
        ("ref1", None, None, None, None, None,  Path("save.json"), None, None,
        # expected values
        Path('ref1'), None, None, Path("ref1", "saved_documents.json"), Path("save.json")),

        # project_path_given
        ("ref1", Path("project_ref1"), None, None, None, None, None, None, None,
        # expected values
        Path('project_ref1'), None, None, Path("project_ref1", "saved_documents.json"), None)
    ],
    ids=[
        "happy_path_all_params",
        "happy_path_minimal_params",
        "edge_case_operator_version_as_path",
        "edge_case_saved_documents_no_json",
        "edge_case_only_eigen_ref",
        "quick_save_path_given",
        "project_path_given"
    ]
)
def test_project_init_existing_dir(root_directory,mock_project_dir, eigen_referentie, project_path, subset_path,
                                   saved_documents_overview_path,
                      bestek, laatst_bewerkt, last_quick_save, subset_operator, otl_version,
                      expected_project_path, expected_subset_operator, expected_otl_version,
                      expected_saved_documents_overview_path, expected_last_quick_save):
    projects_dir = Path(root_directory,  "OTLWizardProjects","Projects")
    # Act
    # Adding the path to the project folder to all the relative paths
    eigen_referentie = add_projects_path(projects_dir,eigen_referentie)
    project_path = add_projects_path(projects_dir,project_path)
    subset_path = add_projects_path(projects_dir, subset_path)
    saved_documents_overview_path = add_projects_path(projects_dir,saved_documents_overview_path)
    last_quick_save = add_projects_path(projects_dir,last_quick_save)
    print(last_quick_save)
    project = Project(eigen_referentie, project_path,subset_path, saved_documents_overview_path,
                      bestek, laatst_bewerkt, last_quick_save, subset_operator, otl_version)

    # also adding that path to the expected values
    expected_last_quick_save= add_projects_path(projects_dir/"ref1" / "quick_saves", expected_last_quick_save)
    expected_project_path = add_projects_path(projects_dir, expected_project_path)
    expected_saved_documents_overview_path = add_projects_path(projects_dir,expected_saved_documents_overview_path)

    # Assert
    assert project.project_path == expected_project_path
    assert project.subset_operator == expected_subset_operator
    assert project.otl_version == expected_otl_version
    assert project.saved_documents_overview_path ==  expected_saved_documents_overview_path
    assert project.last_quick_save == expected_last_quick_save


@pytest.mark.parametrize(
    "project_path, project_details, expected",
    [
        # Happy path test case
        pytest.param(
            Path("valid", "project", "path"),
            {
                "subset": "subset_path",
                "eigen_referentie": "ref123",
                "bestek": "bestek123",
                "laatst_bewerkt": "2023-10-01 12:00:00",
                "last_quick_save": "quick_save_path",
                "subset_operator": "operator123",
                "otl_version": "1.0"
            },
            {
                "project_path": Path("valid", "project", "path"),
                "subset_path": Path("valid", "project", "path", "subset_path"),
                "saved_documents_overview_path": Path("valid", "project", "path", "saved_documents.json"),
                "eigen_referentie": "ref123",
                "bestek": "bestek123",
                "laatst_bewerkt": datetime.datetime(2023, 10, 1, 12, 0, 0),
                "last_quick_save": Path("valid", "project", "path", "quick_saves", "quick_save_path"),
                "subset_operator": "operator123",
                "otl_version": "1.0"
            },
            id="happy_path"
        ),
        # Edge case: Missing optional fields
        pytest.param(
            Path("valid", "project", "path"),
            {
                "subset": "subset_path",
                "eigen_referentie": "ref123",
                "bestek": "bestek123",
                "laatst_bewerkt": "2023-10-01 12:00:00"
            },
            {
                "project_path": Path("valid", "project", "path"),
                "subset_path": Path("valid", "project", "path", "subset_path"),
                "saved_documents_overview_path": Path("valid", "project", "path", "saved_documents.json"),
                "eigen_referentie": "ref123",
                "bestek": "bestek123",
                "laatst_bewerkt": datetime.datetime(2023, 10, 1, 12, 0, 0),
                "last_quick_save": None,
                "subset_operator": None,
                "otl_version": None
            },
            id="missing_optional_fields"
        ),
    ]
)
def test_load_project_happy_and_edge_cases(project_path, project_details, expected):
    # Arrange
    project_details_json = json.dumps(project_details)
    with patch("builtins.open", mock_open(read_data=project_details_json)):
        with patch.object(Path, "exists", return_value=True):
            # Act
            project = Project.load_project(project_path)

            # Assert
            assert project.project_path == expected["project_path"]
            assert project.subset_path == expected["subset_path"]
            assert project.saved_documents_overview_path == expected["saved_documents_overview_path"]
            assert project.eigen_referentie == expected["eigen_referentie"]
            assert project.bestek == expected["bestek"]
            assert project.laatst_bewerkt == expected["laatst_bewerkt"]
            assert project.last_quick_save == expected["last_quick_save"]
            assert project.subset_operator == expected["subset_operator"]
            assert project.otl_version == expected["otl_version"]

@pytest.mark.parametrize(
    "project_path, project_path_exists, expected_exception,expected_error_msg, id",
    [
        # Error case: Project directory does not exist
        pytest.param(
            Path("invalid", "project", "path"),
            False,
            FileNotFoundError,
            "Project dir {0} does not exist".format(str(Path("invalid", "project", "path"))),
            "project_directory_not_exist"
        ),
        # Error case: Project details file does not exist
        pytest.param(
            Path("valid", "project", "path"),
            True,
            FileNotFoundError,
            "Project details file {0} does not exist".format(str(Path("valid", "project", "path","project_details.json"))),
            "project_details_file_not_exist"
        ),
    ]
)
def test_load_project_error_cases(project_path, project_path_exists, expected_exception,expected_error_msg, id):
    # Arrange
    with patch.object(Path, "exists", side_effect=[project_path_exists,Path("valid", "project", "path", "project_details.json").exists()]):
        # Act & Assert
        with pytest.raises(expected_exception) as exc_info:
            Project.load_project(project_path)

        assert exc_info.value.args[0] == expected_error_msg




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







@pytest.mark.parametrize("get_and_cleanup_empty_project",
    # "eigen_referentie, project_path, subset_path, saved_documents_overview_path, bestek,"
    # "laatst_bewerkt, last_quick_save, subset_operator, otl_version,"
    # "expected_project_path, expected_subset_operator, expected_otl_version,"
    # "expected_saved_documents_overview_path, expected_last_quick_save",
    [
        # Happy path with all parameters provided
        ( "empty_project", None, None, None, None, None, None, None, None,
        # expected values
         Path("empty_project"), None,None, None, None),

        # space in the eigen ref
        ( "name space", None, None, None, None, None, None, None, None,
        # expected values
         Path("name space"), None,None, None, None),

        # # Happy path with all parameters provided
        # ("ref1", Path("ref1"), Path("ref1"), Path("ref1/saved_documents.json"),
        #  "bestek1", datetime.datetime(2023, 10, 1),None,"operator1", "version1",
        #  # expected values
        #  Path("ref1"), "operator1", "version1", Path("ref1/saved_documents.json"),
        #  None),

        # Happy path with minimal parameters
        ("ref1", None, None, None, None, None, None, None, None,
        # expected values
         Path('ref1'), None,None, Path('ref1' , 'saved_documents.json'), None),

        # Edge case with subset_operator and otl_version as Path
        ("ref1", None, None, None, None, None, None, Path("operator", "path"), Path("version", "path"),
        # expected values
         Path('ref1'), "path","path", Path('ref1' , 'saved_documents.json'),None),

        # Edge case with saved_documents_overview_path not ending in .json
        ("ref1", None, None, Path("ref1"), None, None, None, None, None,
        # expected values
         Path('ref1'), None, None, Path("ref1", "saved_documents.json"), None),

        # Edge case everything except eigen_reference is None
        ("ref1", None, None, None, None, None, None, None, None,
        # expected values
         Path('ref1'), None,None,  Path("ref1", "saved_documents.json"), None),

        # last quick save path is given
        ("ref1", None, None, None, None, None,  Path("save.json"), None, None,
        # expected values
        Path('ref1'), None, None, Path("ref1", "saved_documents.json"), "save.json"),

        # project_path_given
        ("ref1", Path("project_ref1"), None, None, None, None, None, None, None,
        # expected values
        Path('project_ref1'), None, None, Path("project_ref1", "saved_documents.json"), None)
    ],
    ids=[
        "empty_project",
        "space_in_the_eigen_ref",
        # "happy_path_all_params",
        "happy_path_minimal_params",
        "edge_case_operator_version_as_path",
        "edge_case_saved_documents_no_json",
        "edge_case_only_eigen_ref",
        "quick_save_path_given",
        "project_path_given"
    ],indirect=True
)
def test_save_project_to_dir(get_and_cleanup_empty_project):
    project,expected_project_detail_content,param = get_and_cleanup_empty_project
    project.save_project_to_dir()

    expected_project_path = Path(ProgramFileStructure.get_otl_wizard_projects_dir() ,param[9])
    assert expected_project_path.exists()
    assert Path(expected_project_path,Project.project_details_filename).exists()

    with open(expected_project_path/Project.project_details_filename, "r") as project_details_file:
        project_detail_content = json.load(project_details_file)

    if not expected_project_detail_content["laatst_bewerkt"]:
        expected_project_detail_content["laatst_bewerkt"]= project.laatst_bewerkt.strftime("%Y-%m-%d %H:%M:%S")

    assert project_detail_content == expected_project_detail_content

@pytest.mark.parametrize("get_and_cleanup_empty_project",
    # "eigen_referentie, project_path, subset_path, saved_documents_overview_path, bestek,"
    # "laatst_bewerkt, last_quick_save, subset_operator, otl_version,"
    # "expected_project_path, expected_subset_operator, expected_otl_version,"
    # "expected_saved_documents_overview_path, expected_last_quick_save",
    # expected_error, expected_error_value,
    [
        # non_existent_subset
        ("ref1", Path("ref1"), Path("ref1"), Path("ref1", "saved_documents.json"),
         "bestek1", datetime.datetime(2023, 10, 1),None,"operator1", "version1",
         # expected values
         Path("ref1"), "operator1", "version1", Path("ref1", "saved_documents.json"),
         None,FileNotFoundError,'No such file or directory ref1'),


    ],
    ids=[
        "non_existent_subset"

    ],indirect=True
)
def test_save_project_to_dir_with_error(get_and_cleanup_empty_project):
    project, expected_res,param = get_and_cleanup_empty_project
    expected_exception = param[14]
    expected_error_msg = param[15]
    with pytest.raises(expected_exception) as exc_info:
        project.save_project_to_dir()

    assert f"{exc_info.value.strerror} {exc_info.value.filename}" == expected_error_msg



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

@fixture
def setup_quicksave_test_project(root_directory,mock_otl_wizard_dir) -> Project:
    backup_quicksave_test_project_path  = Path(root_directory, "OTLWizardProjects", "Projects_backup", "quicksave_test")
    quicksave_test_project_path = Path(root_directory, "OTLWizardProjects", "Projects", "quicksave_test")

    if quicksave_test_project_path.exists():
        shutil.rmtree(quicksave_test_project_path)

    shutil.copytree(backup_quicksave_test_project_path,
                    quicksave_test_project_path)
    sleep(0.5)  # sleep to give the system time to copy
    yield Project.load_project(quicksave_test_project_path)

    if quicksave_test_project_path.exists():
        shutil.rmtree(quicksave_test_project_path)


@pytest.mark.asyncio
async def test_load_validated_assets(setup_quicksave_test_project):
    loaded_assets_and_relations:list[Union[RelatieObject, RelationInteractor]] = (
        await setup_quicksave_test_project.load_validated_assets())

    print([str(asset) for asset in loaded_assets_and_relations])


    expected_assets_and_relations = ['<Verkeersbordopstelling> object\n'
     '    typeURI : '
     'https://wegenenverkeer.data.vlaanderen.be/ns/installatie#Verkeersbordopstelling\n'
     '    afbeelding :\n'
     '    [0] bestandsnaam : dummy_xEEIhxjFOV\n'
     '    [0] mimeType : '
     'application-vnd.openxmlformats-officedocument.wordprocessingml.document\n'
     '    [0] omschrijving :\n'
     '    [0]     waarde : dummy_ncnHoW\n'
     '    [0] uri : http://TCyQVsJASN.dummy\n'
     '    assetId :\n'
     '        identificator : dummy_hxOTHWe\n'
     '        toegekendDoor : dummy_GfaE\n'
     '    bestekPostNummer :\n'
     '    [0] dummy_ZFsldo\n'
     '    datumOprichtingObject : 2012-02-03\n'
     '    isActief : True\n'
     '    isBotsvriendelijk : False\n'
     '    notitie : dummy_UIKtqsinxn\n'
     '    operationeleStatus : actief\n'
     '    positieTovRijweg : midden\n'
     '    standaardBestekPostNummer :\n'
     '    [0] dummy_ddvuQMNpqH\n'
     '    theoretischeLevensduur :\n'
     '        waarde : 67\n'
     '    toestand : uit-gebruik\n'
     '    wegSegment :\n'
     '    [0] externReferentienummer : dummy_kblEa\n'
     '    [0] externePartij : dummy_Rwa',
     '<Verkeersbordopstelling> object\n'
     '    typeURI : '
     'https://wegenenverkeer.data.vlaanderen.be/ns/installatie#Verkeersbordopstelling\n'
     '    afbeelding :\n'
     '    [0] bestandsnaam : dummy_NsCZgBsVn\n'
     '    [0] mimeType : text-plain\n'
     '    [0] omschrijving :\n'
     '    [0]     waarde : dummy_fU\n'
     '    [0] uri : http://NdYntJxSUtvzl.dummy\n'
     '    assetId :\n'
     '        identificator : dummy_LGG\n'
     '        toegekendDoor : dummy_O\n'
     '    bestekPostNummer :\n'
     '    [0] dummy_qhzW\n'
     '    datumOprichtingObject : 2003-04-26\n'
     '    isActief : True\n'
     '    isBotsvriendelijk : False\n'
     '    notitie : dummy_pHmx\n'
     '    operationeleStatus : actief-met-geplande-verwijdering\n'
     '    positieTovRijweg : midden\n'
     '    standaardBestekPostNummer :\n'
     '    [0] dummy_CWWD\n'
     '    theoretischeLevensduur :\n'
     '        waarde : 39\n'
     '    toestand : uit-gebruik\n'
     '    wegSegment :\n'
     '    [0] externReferentienummer : dummy_URvp\n'
     '    [0] externePartij : dummy_OMtmtTh',
     '<Funderingsmassief> object\n'
     '    typeURI : '
     'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Funderingsmassief\n'
     '    aanzetpeil :\n'
     '        waarde : 57.96\n'
     '    afmetingGrondvlak :\n'
     '        rechthoekig :\n'
     '            breedte :\n'
     '                waarde : 62.93\n'
     '            lengte :\n'
     '                waarde : 48.01\n'
     '    assetId :\n'
     '        identificator : dummy_TyBGmXfXC\n'
     '        toegekendDoor : dummy_Il\n'
     '    bestekPostNummer :\n'
     '    [0] dummy_bzJNOCVhP\n'
     '    datumOprichtingObject : 2017-09-09\n'
     '    funderingshoogte :\n'
     '        waarde : 11.65\n'
     '    hoogte :\n'
     '        waarde : 3.71\n'
     '    isActief : False\n'
     '    isPermanent : False\n'
     '    isPrefab : False\n'
     '    materiaal : inox\n'
     '    notitie : dummy_LUrrpZTJFy\n'
     '    standaardBestekPostNummer :\n'
     '    [0] dummy_aYtzBTGBHQ\n'
     '    theoretischeLevensduur :\n'
     '        waarde : 5\n'
     '    toestand : overgedragen\n'
     '    volume :\n'
     '        waarde : 74.11',
     '<Funderingsmassief> object\n'
     '    typeURI : '
     'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Funderingsmassief\n'
     '    aanzetpeil :\n'
     '        waarde : 26.7\n'
     '    afmetingGrondvlak :\n'
     '        rechthoekig :\n'
     '            breedte :\n'
     '                waarde : 4.78\n'
     '            lengte :\n'
     '                waarde : 18.51\n'
     '    assetId :\n'
     '        identificator : dummy_FNrHuPZCWV\n'
     '        toegekendDoor : dummy_wKUsXpdixr\n'
     '    bestekPostNummer :\n'
     '    [0] dummy_iCdhiGE\n'
     '    datumOprichtingObject : 2001-06-28\n'
     '    funderingshoogte :\n'
     '        waarde : 24.56\n'
     '    hoogte :\n'
     '        waarde : 3.4\n'
     '    isActief : False\n'
     '    isPermanent : True\n'
     '    isPrefab : False\n'
     '    materiaal : staal\n'
     '    notitie : dummy_qBuaNfLvKs\n'
     '    standaardBestekPostNummer :\n'
     '    [0] dummy_FKv\n'
     '    theoretischeLevensduur :\n'
     '        waarde : 7\n'
     '    toestand : in-opbouw\n'
     '    volume :\n'
     '        waarde : 40.2',
     '<Pictogram> object\n'
     '    typeURI : '
     'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Pictogram\n'
     '    assetId :\n'
     '        identificator : dummy_a\n'
     '        toegekendDoor : dummy_PnEQq\n'
     '    bestekPostNummer :\n'
     '    [0] dummy_mp\n'
     '    datumOprichtingObject : 2019-10-02\n'
     '    isActief : True\n'
     '    nalichtingstijd :\n'
     '        waarde : 39\n'
     '    notitie : dummy_ZszahHl\n'
     '    opschrift : dummy_drTTNduz\n'
     '    standaardBestekPostNummer :\n'
     '    [0] dummy_n\n'
     '    symbool : vluchtend-persoon\n'
     '    theoretischeLevensduur :\n'
     '        waarde : 27\n'
     '    toestand : in-opbouw',
     '<Pictogram> object\n'
     '    typeURI : '
     'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Pictogram\n'
     '    assetId :\n'
     '        identificator : dummy_long_identificator_pictogram\n'
     '        toegekendDoor : dummy_Ek\n'
     '    bestekPostNummer :\n'
     '    [0] dummy_AoigeDNpf\n'
     '    datumOprichtingObject : 2004-01-03\n'
     '    isActief : True\n'
     '    nalichtingstijd :\n'
     '        waarde : 4\n'
     '    notitie : dummy_Jp\n'
     '    opschrift : dummy_zZJ\n'
     '    standaardBestekPostNummer :\n'
     '    [0] dummy_yMDK\n'
     '    symbool : nummer-veiligheidsnis\n'
     '    theoretischeLevensduur :\n'
     '        waarde : 39\n'
     '    toestand : gepland',
     '<Verkeersbordsteun> object\n'
     '    typeURI : '
     'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Verkeersbordsteun\n'
     '    assetId :\n'
     '        identificator : dummy_vbeo\n'
     '        toegekendDoor : dummy_JNihuWw\n'
     '    bestekPostNummer :\n'
     '    [0] dummy_NratsxlNcl\n'
     '    breedte :\n'
     '        waarde : 68.82\n'
     '    datumOprichtingObject : 2000-03-26\n'
     '    diameter :\n'
     '        waarde : 24.2\n'
     '    fabricagevoorschrift : dummy_aeESM\n'
     '    isActief : True\n'
     '    lengte :\n'
     '        waarde : 51.45\n'
     '    lengteBovengronds :\n'
     '        waarde : 32.48\n'
     '    lengteOndergronds :\n'
     '        waarde : 19.36\n'
     '    naam : dummy_J\n'
     '    notitie : dummy_xZIw\n'
     '    operationeleStatus : tijdelijk-actief\n'
     '    standaardBestekPostNummer :\n'
     '    [0] dummy_aXoooLO\n'
     '    theoretischeLevensduur :\n'
     '        waarde : 41\n'
     '    toestand : overgedragen\n'
     '    type : botsvriendelijke-steun-type-100NE2\n'
     '    wanddikte :\n'
     '        waarde : 32.08',
     '<Verkeersbordsteun> object\n'
     '    typeURI : '
     'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Verkeersbordsteun\n'
     '    assetId :\n'
     '        identificator : dummy_TjwXqP\n'
     '        toegekendDoor : dummy_afJZZphX\n'
     '    bestekPostNummer :\n'
     '    [0] dummy_pKywpsiAoi\n'
     '    breedte :\n'
     '        waarde : 62.5\n'
     '    datumOprichtingObject : 2011-04-22\n'
     '    diameter :\n'
     '        waarde : 19.94\n'
     '    fabricagevoorschrift : dummy_Xyl\n'
     '    isActief : False\n'
     '    lengte :\n'
     '        waarde : 65.42\n'
     '    lengteBovengronds :\n'
     '        waarde : 75.44\n'
     '    lengteOndergronds :\n'
     '        waarde : 30.04\n'
     '    naam : dummy_s\n'
     '    notitie : dummy_lPDNDUFkW\n'
     '    operationeleStatus : actief-met-tijdelijke-wijziging\n'
     '    standaardBestekPostNummer :\n'
     '    [0] dummy_Z\n'
     '    theoretischeLevensduur :\n'
     '        waarde : 74\n'
     '    toestand : in-opbouw\n'
     '    type : botsvriendelijke-steun-type-100NE2\n'
     '    wanddikte :\n'
     '        waarde : 20.8',
     '<Bewegingssensor> object\n'
     '    typeURI : '
     'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Bewegingssensor\n'
     '    assetId :\n'
     '        identificator : dummy_Q\n'
     '        toegekendDoor : OTL_wizard_2',
     '<BetonnenHeipaal> object\n'
     '    typeURI : '
     'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#BetonnenHeipaal\n'
     '    assetId :\n'
     '        identificator : dummy_bcjseEAj\n'
     '        toegekendDoor : OTL_wizard_2',
     '<Bevestiging> object\n'
     '    typeURI : '
     'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Bevestiging\n'
     '    assetId :\n'
     '        identificator : dummy_bevestiging_2\n'
     '        toegekendDoor : dummy_zQp\n'
     '    bron :\n'
     '    bronAssetId :\n'
     '        identificator : dummy_Q\n'
     '        toegekendDoor : dummy_okopD\n'
     '    doel :\n'
     '    doelAssetId :\n'
     '        identificator : dummy_bcjseEAj\n'
     '        toegekendDoor : dummy_dY\n'
     '    isActief : True',
     '<HoortBij> object\n'
     '    typeURI : '
     'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#HoortBij\n'
     '    assetId :\n'
     '        identificator : dummy_hoort_bij\n'
     '        toegekendDoor : dummy_LxexRM\n'
     '    bron :\n'
     '    bronAssetId :\n'
     '        identificator : dummy_vbeo\n'
     '        toegekendDoor : dummy_Ouee\n'
     '    doel :\n'
     '    doelAssetId :\n'
     '        identificator : dummy_LGG\n'
     '        toegekendDoor : dummy_ZT\n'
     '    isActief : True',
     '<Bevestiging> object\n'
     '    typeURI : '
     'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Bevestiging\n'
     '    assetId :\n'
     '        identificator : dummy_bevestiging_1\n'
     '        toegekendDoor : dummy_zQp\n'
     '    bron :\n'
     '    bronAssetId :\n'
     '        identificator : dummy_a\n'
     '        toegekendDoor : dummy_okopD\n'
     '    doel :\n'
     '    doelAssetId :\n'
     '        identificator : dummy_TyBGmXfXC\n'
     '        toegekendDoor : dummy_dY\n'
     '    isActief : False',
     '<LigtOp> object\n'
     '    typeURI : https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#LigtOp\n'
     '    assetId :\n'
     '        identificator : dummy_ligt_op\n'
     '        toegekendDoor : dummy_LxexRM\n'
     '    bron :\n'
     '    bronAssetId :\n'
     '        identificator : dummy_FNrHuPZCWV\n'
     '        toegekendDoor : dummy_Ouee\n'
     '    doel :\n'
     '    doelAssetId :\n'
     '        identificator : dummy_TyBGmXfXC\n'
     '        toegekendDoor : dummy_ZT\n'
     '    isActief : False']
    assert [str(asset) for asset in loaded_assets_and_relations] == expected_assets_and_relations

@fixture
def mock_get_last_quick_save_path_to_return_empty():
    original_get_last_quick_save_path = Project.get_last_quick_save_path
    Project.get_last_quick_save_path = Mock(return_value=[])
    yield
    Project.get_last_quick_save_path = original_get_last_quick_save_path


@pytest.mark.asyncio
async def test_load_validated_assets_with_empty_path(setup_quicksave_test_project,
                                                mock_get_last_quick_save_path_to_return_empty):

    loaded_assets_and_relations:list[Union[RelatieObject, RelationInteractor]] = (
        await setup_quicksave_test_project.load_validated_assets())

    assert loaded_assets_and_relations == []


@pytest.mark.parametrize("get_and_cleanup_empty_project",
    # "eigen_referentie, project_path, subset_path, saved_documents_overview_path, bestek,"
    # "laatst_bewerkt, last_quick_save, subset_operator, otl_version,"
    # "expected_project_path, expected_subset_operator, expected_otl_version,"
    # "expected_saved_documents_overview_path, expected_last_quick_save",
    [
        # Happy path with all parameters provided
        ( "empty_project", None, None, None, None, None, None, None, None,
        # expected values
         Path("empty_project"), None,None, None, None),
    ],
    ids=[
        "empty_project",
    ],indirect=True
)
@pytest.mark.asyncio
async def test_save_validated_assets_from_scratch(get_and_cleanup_empty_project: Project):
    """
    testing to see if we can make the quicksave directory in an empty project

    @param get_and_cleanup_empty_project:
    @return:
    """
    project, expected_res,param = get_and_cleanup_empty_project
    project.assets_in_memory = []

    if project.quick_save_dir_path and project.quick_save_dir_path.exists():
            shutil.rmtree(project.quick_save_dir_path)

    #to create the project folder we need to save it first
    project.save_project_to_dir()

    assert not project.quick_save_dir_path.exists()

    await project.save_validated_assets()

    # check that the quicksave directory exists now
    assert project.quick_save_dir_path.exists()


@pytest.mark.parametrize("get_and_cleanup_empty_project",
    # "eigen_referentie, project_path, subset_path, saved_documents_overview_path, bestek,"
    # "laatst_bewerkt, last_quick_save, subset_operator, otl_version,"
    # "expected_project_path, expected_subset_operator, expected_otl_version,"
    # "expected_saved_documents_overview_path, expected_last_quick_save",
    [
        # Happy path with all parameters provided
        ( "empty_project", None, None, None, None, None, None, None, None,
        # expected values
         Path("empty_project"), None,None, None, None),
    ],
    ids=[
        "empty_project",
    ],indirect=True
)
@pytest.mark.asyncio
async def test_save_validated_assets_delete_old_files(get_and_cleanup_empty_project: Project):
    """
    testing situations:
    1. when there is a file in the quicksave directory that doesn't follow the naming convention
    2. when there is a file that is more then 7 days old
    3. a file that is not older than 7 days

    @param get_and_cleanup_empty_project:
    @return:
    """
    project, expected_res,param = get_and_cleanup_empty_project

    # to create the project folder we need to save it first
    project.save_project_to_dir()

    #make files
    # a file that doesn't follow the standard naming convention, needs to stay6
    strange_name_save_path = project.get_quicksaves_dir_path()/ "strange_name.json"
    strange_name_f = open(strange_name_save_path, mode="x")
    strange_name_f.close()
    # a file that is younger than 7 days, needs to stay
    young_date_str = (datetime.datetime.now() - timedelta(days=5)).strftime(Project.quicksave_date_format)
    young_save_path = project.quick_save_dir_path / f"quick_save-{young_date_str}.json"
    young_save_f = open(young_save_path,mode="x")
    young_save_f.close()
    # a file that is older than 7 days, needs to be deleted
    old_date_str = (datetime.datetime.now() - timedelta(days=8)).strftime(
        Project.quicksave_date_format)
    old_save_path = project.quick_save_dir_path / f"quick_save-{old_date_str}.json"
    old_save_f = open(old_save_path,mode="x")
    old_save_f.close()

    # before saving validated assets there should be 3 files
    quick_save_files = os.listdir(project.get_quicksaves_dir_path())
    assert len(quick_save_files) == 3

    await project.save_validated_assets(asynchronous=False)

    # quicksave folder should contain
    # 1. strange_name_f
    # 2. young_save_f
    # 3. new_saved_save_f
    # only old_save_f is deleted
    quick_save_files =  sorted(os.listdir(project.get_quicksaves_dir_path()))
    assert len(quick_save_files) == 3

    expected_quick_save_files = sorted([f"quick_save-{young_date_str}.json", project.get_last_quick_save_path().name, 'strange_name.json'])
    assert quick_save_files == expected_quick_save_files
@fixture
async def setup_preloaded_assets_in_memory(setup_quicksave_test_project) -> Project:

    setup_quicksave_test_project.assets_in_memory = await setup_quicksave_test_project.load_validated_assets()
    yield setup_quicksave_test_project
    setup_quicksave_test_project.assets_in_memory = []


@pytest.mark.asyncio
async def test_save_validated_assets(setup_preloaded_assets_in_memory: Project):

    expected_assets =  deepcopy(setup_preloaded_assets_in_memory.assets_in_memory)
    old_quicksave = deepcopy(setup_preloaded_assets_in_memory.last_quick_save)

    await setup_preloaded_assets_in_memory.save_validated_assets(asynchronous=False)

    # we expect there to be a new last_quick_save
    assert setup_preloaded_assets_in_memory.last_quick_save != old_quicksave

    new_loaded_assets = setup_preloaded_assets_in_memory.load_validated_assets()

    assert new_loaded_assets == expected_assets

def list_files_scandir(path='.'):
    with os.scandir(path) as entries:
        for entry in entries:
            if entry.is_file():
                print(entry.path)
            elif entry.is_dir():
                list_files_scandir(entry.path)

def test_export_project_with_other_files(root_directory, setup_quicksave_test_project,cleanup_after_creating_a_file_to_delete, mock_otl_wizard_dir):
    quicksave_test_project_export_path = Path(root_directory, "OTLWizardProjects", "TestFiles", "export_test.otlw")

    cleanup_after_creating_a_file_to_delete.append(quicksave_test_project_export_path)

    project = setup_quicksave_test_project
    print("In folder:")
    list_files_scandir(project.project_path)

    project.export_project_to_file(quicksave_test_project_export_path)

    # check the file content of the otlw file (zip format)
    assert quicksave_test_project_export_path.exists()
    expected_list_of_files = ['project_details.json',
                              'project_files/simpel_vergelijking_template5.xlsx',
                              'quick_saves/quick_save-250103_170930.json',
                              'saved_documents.json',
                              'simpele_vergelijkings_subset2.db']

    with zipfile.ZipFile(quicksave_test_project_export_path) as project_zip:
        list_of_files = sorted(project_zip.namelist())
    print("In zip:")
    print(list_of_files)
    assert list_of_files == expected_list_of_files

@fixture
def setup_exported_project(root_directory, setup_quicksave_test_project,cleanup_after_creating_a_file_to_delete):
    quicksave_test_project_export_path = Path(root_directory,
                                              "OTLWizardProjects/TestFiles/export_test.otlw")

    cleanup_after_creating_a_file_to_delete.append(quicksave_test_project_export_path)

    project = setup_quicksave_test_project

    project.export_project_to_file(quicksave_test_project_export_path)
    project.delete_project_dir_by_path()
    HomeDomain.reload_projects()


    yield quicksave_test_project_export_path

def test_imported_project_with_other_files(root_directory,mock_otl_wizard_dir, setup_exported_project):
    exported_project_path = setup_exported_project
    backup_quicksave_test_project_path = Path(root_directory,
                                              "OTLWizardProjects/Projects_backup/quicksave_test")

    imported_project = Project.import_project(exported_project_path)
    imported_project.load_saved_document_filenames()
    expected_project = Project.load_project(backup_quicksave_test_project_path)
    expected_project.load_saved_document_filenames()

    assert imported_project == expected_project

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

@pytest.fixture
def mock_project(mock_otl_wizard_dir):
    project = Project(eigen_referentie="test_project")
    project.saved_project_files = []
    project.save_project_to_dir()

    yield project

    if project.project_path and project.project_path.exists():
        shutil.rmtree(project.project_path)

@pytest.mark.parametrize("saved_documents_content, expected_states, test_id", [
    ([], [], "empty_saved_documents"),
    ([{"file_path": "file1.txt", "state": "ok"}], [FileState.WARNING], "no_quicksave_warning"),
    ([{"file_path": "file1.txt", "state": "ok"}, {"file_path": "file2.txt", "state": "warning"}], [FileState.WARNING, FileState.WARNING], "mixed_states_no_quicksave"),
    ([{"file_path": "file1.txt", "state": "ok"}], [FileState.OK], "quicksave_exists"),
], ids=["empty_saved_documents",
        "no_quicksave_warning",
        "mixed_states_no_quicksave",
        "quicksave_exists"])
def test_load_saved_document_filenames(mock_project, mock_otl_wizard_dir, saved_documents_content, expected_states, test_id):
    # Arrange
    saved_documents_path = ProgramFileStructure.get_otl_wizard_projects_dir() / mock_project.project_path.name / Project.saved_documents_filename
    quicksave_dir_path = mock_project.get_quicksaves_dir_path()
    os.makedirs(quicksave_dir_path, exist_ok=True)
    with open(saved_documents_path, 'w') as f:
        json.dump(saved_documents_content, f)
    if expected_states and expected_states[0] == FileState.OK:
        with open(quicksave_dir_path / "quicksave.txt", 'w') as f:
            f.write("quicksave content")
    # Act
    result = mock_project.load_saved_document_filenames()

    # Assert
    assert result == mock_project
    assert len(mock_project.saved_project_files) == len(expected_states)
    for file, expected_state in zip(mock_project.saved_project_files, expected_states):
        assert file.state == expected_state


def test_load_saved_document_filenames_old_project_structure(mock_project, mock_otl_wizard_dir):
    """
    Test the loading of saved document filenames for a project with an old directory structure.

    This function verifies that the correct file states are assigned and that files are moved
    from the old project structure to the new one.

    @param mock_project:
    @param mock_otl_wizard_dir:
    @return:
    """
    saved_documents_content =  [{"file_path": "file1.txt", "state": "ok"}]
    expected_states = [FileState.WARNING]
    test_id = "old_project_structure_test"

    # Arrange
    saved_documents_path = ProgramFileStructure.get_otl_wizard_projects_dir() / mock_project.project_path.name / Project.saved_documents_filename
    quicksave_dir_path = mock_project.get_quicksaves_dir_path()
    os.makedirs(quicksave_dir_path, exist_ok=True)
    with open(saved_documents_path, 'w') as f:
        json.dump(saved_documents_content, f)

    #create the file in the save_document_content in the old OTL-templates directory
    os.mkdir(mock_project.get_old_project_files_dir_path())
    with open(mock_project.get_old_project_files_dir_path() / saved_documents_content[0]["file_path"], 'w') as f:
        f.write("file to be moved")

    if expected_states and expected_states[0] == FileState.OK:
        with open(quicksave_dir_path / "quicksave.txt", 'w') as f:
            f.write("quicksave content")
    # Act
    result = mock_project.load_saved_document_filenames()

    # Assert
    assert result == mock_project
    assert len(mock_project.saved_project_files) == len(expected_states)
    for file, expected_state in zip(mock_project.saved_project_files, expected_states):
        assert file.state == expected_state

    expected_file = ProjectFile(
        file_path=mock_project.get_project_files_dir_path() / Path(saved_documents_content[0]["file_path"]).name,
        state=FileState.OK)
    assert len(mock_project.saved_project_files) == 1
    assert mock_project.saved_project_files[0].file_path == expected_file.file_path
    assert expected_file.file_path.exists()

@pytest.mark.parametrize("caught_exception, test_id, saved_documents_content", [
    (FileNotFoundError, "no_file",""),
    (json.JSONDecodeError, "invalid_json","invalid json"),
    (json.JSONDecodeError, "no_json_content",""),
], ids=["no_file",
        "invalid_json",
        "no_json_content"])
def test_load_saved_document_filenames_edge_cases(mock_project : Project, mock_otl_wizard_dir,
                                                  caught_exception, test_id, saved_documents_content):
    """
    test Project.load_saved_document_filenames with edge cases that are handled

    @param mock_project: mock project
    @param mock_otl_wizard_dir: mocks the ProgramFileStructure.get_otl_wizard_projects_dir() function
    @param caught_exception: these exceptions should NOT happen
    @param test_id:
    @return:
    """
    # Arrange
    saved_documents_path = ProgramFileStructure.get_otl_wizard_projects_dir() / mock_project.project_path.name / Project.saved_documents_filename
    if isinstance(caught_exception, FileNotFoundError):
        # Ensure the file does not exist
        if saved_documents_path.exists():
            os.remove(saved_documents_path)
    else:
        # Create an invalid JSON file
        with open(saved_documents_path, 'w+') as f:
            f.write(saved_documents_content)

    # Act & Assert
    mock_project.load_saved_document_filenames()

    assert mock_project.saved_project_files == []

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
        cleanup_after_creating_a_file_to_delete,create_mock_project_project_1,mock_otl_wizard_dir):
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