from pathlib import Path
from unittest.mock import Mock

from _pytest.fixtures import fixture

from Domain import global_vars
from Domain.project.ProgramFileStructure import ProgramFileStructure
from Domain.step_domain.InsertDataDomain import InsertDataDomain
from Domain.project.Project import Project
from Domain.project.ProjectFileManager import ProjectFileManager
from Domain.step_domain.RelationChangeDomain import RelationChangeDomain


@fixture
def mock_project_home_path(root_directory):
    original_home_path = ProgramFileStructure.get_home_path
    ProgramFileStructure.get_home_path = Mock(return_value=root_directory)
    yield
    ProgramFileStructure.get_home_path = original_home_path

@fixture
def mock_get_otl_wizard_projects_dir(root_directory):
    original_get_otl_wizard_projects_dir = ProgramFileStructure.get_otl_wizard_projects_dir
    ProgramFileStructure.get_otl_wizard_projects_dir= Mock(return_value=root_directory / "demo_projects"
                                                                        /  "simpel_vergelijkings_project")
    yield
    ProgramFileStructure.get_otl_wizard_projects_dir = original_get_otl_wizard_projects_dir

@fixture
def setup_test_project(root_directory: Path, mock_step3_visuals,mock_get_otl_wizard_projects_dir) -> None:
    """Set up a test project environment for unit testing.

       This fixture initializes a test project by setting the current project and mocking the
       method that retrieves the directory for wizard projects. It ensures that tests have a
       consistent and controlled environment to work with, allowing for reliable and repeatable
       test outcomes.

        simpele_vergelijkings_subset.db contains the following classes:
        1. Verkeersbordopstelling
        2. Funderingsmassief
        3. Pictogram
        4. Verkeersbordsteun
        5. Bevestiging
        6. HoortBij
        7. LigtOp
        Not all attributes of each class are required

       Args:
           root_directory (Path): The root directory where the demo projects are located.

       Returns:
           None
       """



    test_subset_file_path: Path = (root_directory / "demo_projects"
                                   /  "simpel_vergelijkings_project"
                                   / "simpele_vergelijkings_subset2.db")
    project_file_path: Path = (root_directory / "demo_projects"  /  "simpel_vergelijkings_project"
                               / "wizardProject")

    global_vars.current_project = Project(project_path=project_file_path,
                                          subset_path=Path(test_subset_file_path))
    original_get_otl_wizard_projects_dir = ProjectFileManager.get_otl_wizard_projects_dir
    ProjectFileManager.get_otl_wizard_projects_dir = Mock(
        return_value=root_directory / "demo_projects" / "simpel_vergelijkings_project")

    local_mock_InsertDataDomain_get_screen = InsertDataDomain.get_screen
    InsertDataDomain.get_screen = Mock()
    InsertDataDomain.init_static()
    InsertDataDomain.get_screen = local_mock_InsertDataDomain_get_screen

    local_mock_RelationChangeDomain_get_screen = RelationChangeDomain.get_screen
    RelationChangeDomain.get_screen = Mock()
    RelationChangeDomain.init_static(global_vars.current_project)
    RelationChangeDomain.get_screen = local_mock_RelationChangeDomain_get_screen


    yield
    ProjectFileManager.get_otl_wizard_projects_dir = original_get_otl_wizard_projects_dir

@fixture
def mock_save_validated_assets_function() -> None:
    original_save_validated_assets =  ProjectFileManager.save_validated_assets
    ProjectFileManager.save_validated_assets  = Mock()
    yield
    ProjectFileManager.save_validated_assets = original_save_validated_assets

@fixture
def mock_load_validated_assets() -> None:
    original_load_validated_assets = ProjectFileManager.load_validated_assets

    ProjectFileManager.load_validated_assets = Mock(return_value=RelationChangeDomain.get_quicksave_instances())
    yield
    ProjectFileManager.load_validated_assets = original_load_validated_assets
