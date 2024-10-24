from pathlib import Path
from unittest.mock import Mock

from _pytest.fixtures import fixture

from Domain import global_vars
from Domain.InsertDataDomain import InsertDataDomain
from Domain.Project import Project
from Domain.ProjectFileManager import ProjectFileManager
from Domain.RelationChangeDomain import RelationChangeDomain


@fixture
def setup_test_project(root_directory: Path) -> None:
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

    InsertDataDomain.init_static()
    RelationChangeDomain.init_static(global_vars.current_project)

    yield
    ProjectFileManager.get_otl_wizard_projects_dir = original_get_otl_wizard_projects_dir