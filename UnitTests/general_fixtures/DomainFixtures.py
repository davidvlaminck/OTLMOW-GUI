import os
import shutil
from collections import namedtuple
from pathlib import Path
from unittest.mock import Mock, AsyncMock

from _pytest.fixtures import fixture

from Domain import global_vars
from Domain.logger.OTLLogger import OTLLogger
from Domain.ProgramFileStructure import ProgramFileStructure
from Domain.step_domain.InsertDataDomain import InsertDataDomain
from Domain.project.Project import Project
from Domain.step_domain.RelationChangeDomain import RelationChangeDomain

OTLLogger.logger = Mock()
global_vars.test_mode=True

@fixture
def cleanup_after_creating_a_file_to_delete():
    to_delete = []
    yield to_delete
    for item in to_delete:
        if os.path.exists(item):
            os.remove(item)

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
def mock_save_validated_assets_function() -> None:
    original_save_validated_assets = Project.save_validated_assets
    Project.save_validated_assets = AsyncMock()
    yield
    Project.save_validated_assets = original_save_validated_assets


@fixture
def setup_test_project(root_directory: Path, mock_step3_visuals,mock_get_otl_wizard_projects_dir,mock_save_validated_assets_function) -> None:
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

    global_vars.current_project = Project( eigen_referentie="test", project_path=project_file_path,
                                          subset_path=Path(test_subset_file_path))
    original_get_otl_wizard_projects_dir = ProgramFileStructure.get_otl_wizard_projects_dir
    ProgramFileStructure.get_otl_wizard_projects_dir = Mock(
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
    ProgramFileStructure.get_otl_wizard_projects_dir = original_get_otl_wizard_projects_dir



@fixture
def mock_load_validated_assets() -> None:
    original_load_validated_assets = Project.load_validated_assets_async

    Project.load_validated_assets_async = AsyncMock(return_value=RelationChangeDomain.get_quicksave_instances())
    yield
    Project.load_validated_assets_async = original_load_validated_assets

@fixture
def setup_simpel_vergelijking_template5(root_directory):
    test_object_lists_file_path: list[str] = [
        str(root_directory / "demo_projects" / "simpel_vergelijkings_project" /
            "simpel_vergelijking_template5.xlsx")]

    for path_str in test_object_lists_file_path:
        if os.path.exists(path_str):
            os.remove(path_str)

        backup_path = root_directory / "demo_projects" / "simpel_vergelijkings_project_backup_files" / Path(path_str).name
        shutil.copy(backup_path, path_str)

    yield test_object_lists_file_path

    for path_str in test_object_lists_file_path:
        if os.path.exists(path_str):
            os.remove(path_str)

@fixture
def setup_simpel_vergelijking_template2(root_directory):
    test_object_lists_file_path: list[str] = [
        str(root_directory / "demo_projects" / "simpel_vergelijkings_project" /
            "simpel_vergelijking_template2.xlsx")]

    for path_str in test_object_lists_file_path:
        if os.path.exists(path_str):
            os.remove(path_str)

        backup_path = root_directory / "demo_projects" / "simpel_vergelijkings_project_backup_files" / Path(
            path_str).name
        shutil.copy(backup_path, path_str)

    yield test_object_lists_file_path

    for path_str in test_object_lists_file_path:
        if os.path.exists(path_str):
            os.remove(path_str)

@fixture
def setup_simpel_vergelijking_template4(root_directory):
    test_object_lists_file_path: list[str] = [
        str(root_directory / "demo_projects" / "simpel_vergelijkings_project" /
            "simpel_vergelijking_template4.xlsx")]

    for path_str in test_object_lists_file_path:
        if os.path.exists(path_str):
            os.remove(path_str)

        backup_path = root_directory / "demo_projects" / "simpel_vergelijkings_project_backup_files" / Path(
            path_str).name
        shutil.copy(backup_path, path_str)

    yield test_object_lists_file_path

    for path_str in test_object_lists_file_path:
        if os.path.exists(path_str):
            os.remove(path_str)
@fixture
def mock_otl_wizard_dir_no_param(root_directory):
    original_get_otl_wizard_projects_dir = ProgramFileStructure.get_otl_wizard_projects_dir
    ProgramFileStructure.get_otl_wizard_projects_dir = Mock(return_value=root_directory  / "OTLWizardProjects" / "Projects")

    yield
    ProgramFileStructure.get_otl_wizard_projects_dir = original_get_otl_wizard_projects_dir

@fixture
def get_and_cleanup_empty_project_no_param(mock_otl_wizard_dir_no_param):
    RequestTuple = namedtuple('requestTuple', ['param'])
    request = RequestTuple(("empty_project", None, None, None, None, None, None, None, None))
    eigen_referentie = request.param[0]
    project_path = request.param[1]
    subset_path= request.param[2]
    saved_documents_overview_path= request.param[3]
    bestek= request.param[4]
    laatst_bewerkt= request.param[5]
    last_quick_save= request.param[6]
    subset_operator= request.param[7]
    otl_version= request.param[8]
    print()

    # remove remnants from failed or aborted tests if necessary
    project_path_rm = ProgramFileStructure.get_otl_wizard_projects_dir() / eigen_referentie
    if project_path_rm.exists():
        shutil.rmtree(project_path_rm)

    yield Project(eigen_referentie=eigen_referentie, project_path= project_path,
                  subset_path=subset_path,
                  saved_documents_overview_path=saved_documents_overview_path,bestek=bestek,
                  laatst_bewerkt=laatst_bewerkt, subset_operator=subset_operator,
                  otl_version=otl_version,
                  last_quick_save=last_quick_save)

    if project_path_rm.exists():
        shutil.rmtree(project_path_rm)

@fixture
def mock_otl_wizard_dir(root_directory):
    original_get_otl_wizard_projects_dir = ProgramFileStructure.get_otl_wizard_projects_dir
    ProgramFileStructure.get_otl_wizard_projects_dir = Mock(return_value=root_directory  / "OTLWizardProjects" / "Projects")

    yield
    ProgramFileStructure.get_otl_wizard_projects_dir = original_get_otl_wizard_projects_dir

@fixture
def get_and_cleanup_empty_project(mock_otl_wizard_dir,request):
    eigen_referentie = request.param[0]
    project_path = request.param[1]
    subset_path= request.param[2]
    saved_documents_overview_path= request.param[3]
    bestek= request.param[4]
    laatst_bewerkt= request.param[5]
    last_quick_save= request.param[6]
    subset_operator= request.param[7]
    otl_version= request.param[8]
    expected_project_path= request.param[9]
    expected_subset_operator= request.param[10]
    expected_otl_version= request.param[11]
    expected_saved_documents_overview_path= request.param[12]
    expected_last_quick_save= request.param[13]
    print()

    # remove remnants from failed or aborted tests if necessary
    project_path_rm = ProgramFileStructure.get_otl_wizard_projects_dir() / eigen_referentie
    if project_path_rm.exists():
        shutil.rmtree(project_path_rm)
    if expected_project_path:
        project_path2_rm = ProgramFileStructure.get_otl_wizard_projects_dir() / expected_project_path
        if project_path2_rm.exists():
            shutil.rmtree(project_path2_rm)

    yield (Project(eigen_referentie=eigen_referentie, project_path= project_path,
                  subset_path=subset_path,
                  saved_documents_overview_path=saved_documents_overview_path,bestek=bestek,
                  laatst_bewerkt=laatst_bewerkt, subset_operator=subset_operator,
                  otl_version=otl_version,
                  last_quick_save=last_quick_save),
           {'bestek':bestek,
            'eigen_referentie': eigen_referentie,
            'laatst_bewerkt' : laatst_bewerkt,
            'subset': subset_path,
            'subset_operator':expected_subset_operator,
            'otl_version': expected_otl_version,
            'last_quick_save':expected_last_quick_save},
            request.param)

    # eigen_referentie = "empty_project"
    # yield Project(eigen_referentie=eigen_referentie,last_quick_save=Path("last_quick_save") )
    project_path = ProgramFileStructure.get_otl_wizard_projects_dir() / eigen_referentie
    if project_path.exists():
        shutil.rmtree(project_path)
    if expected_project_path:
        project_path2 = ProgramFileStructure.get_otl_wizard_projects_dir() / expected_project_path
        if project_path2.exists():
            shutil.rmtree(project_path2)