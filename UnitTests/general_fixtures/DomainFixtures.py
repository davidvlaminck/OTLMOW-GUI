from pathlib import Path
from unittest.mock import Mock

from _pytest.fixtures import fixture

from Domain import global_vars
from Domain.Project import Project
from Domain.ProjectFileManager import ProjectFileManager


@fixture
def root_directory() -> Path:
    return Path(__file__).parent.parent.parent

@fixture
def setup_test_project(root_directory: Path) -> None:
    test_subset_file_path:Path = Path("{0}\\demo_projects\\simpel_vergelijkings_project\\simpele_vergelijkings_subset.db".format(
        str(root_directory)))
    project_file_path: Path = Path("{0}\\demo_projects\\simpel_vergelijkings_project\\wizardProject".format(
        str(root_directory)))
    global_vars.current_project = Project(project_path=project_file_path,
                                          subset_path=Path(test_subset_file_path))
    original_get_otl_wizard_projects_dir = ProjectFileManager.get_otl_wizard_projects_dir
    ProjectFileManager.get_otl_wizard_projects_dir = Mock(
        return_value=root_directory / "demo_projects" / "simpel_vergelijkings_project")
    yield
    ProjectFileManager.get_otl_wizard_projects_dir = original_get_otl_wizard_projects_dir