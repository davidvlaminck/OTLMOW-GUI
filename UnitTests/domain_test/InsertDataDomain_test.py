import os
from pathlib import Path
from unittest.mock import Mock

from _pytest.fixtures import fixture
from pytestqt.plugin import qtbot

from Domain import global_vars
from Domain.InsertDataDomain import InsertDataDomain
from Domain.Project import Project
from Domain.ProjectFileManager import ProjectFileManager
from Domain.RelationChangeDomain import RelationChangeDomain
from Domain.enums import FileState
from GUI.Screens.DataVisualisationScreen import DataVisualisationScreen
from GUI.Screens.InsertDataScreen import InsertDataScreen
from GUI.Screens.RelationChangeScreen import RelationChangeScreen
from GUI.translation.GlobalTranslate import GlobalTranslate
from OTLWizard import OTLWizard


#################################################
# FULL TESTS                                    #
#################################################
#######################################################
# InsertDataDomain.load_and_validate_document         #
#######################################################
@fixture
def create_translations():
    lang_dir = Path(Path(__file__).absolute()).parent.parent.parent / 'locale/'
    setting={"language": "DUTCH"}
    GlobalTranslate(settings=setting,lang_dir=str(lang_dir))

@fixture
def mock_screen(qtbot, create_translations):
    relation_change_screen = InsertDataScreen(GlobalTranslate.instance.get_all())
    relation_change_screen.fill_class_list = Mock()
    InsertDataDomain.get_screen = Mock(return_value=relation_change_screen)
    return relation_change_screen

@fixture
def root_directory():
    path = Path(os.getcwd())

    while str(path).split("\\").__reversed__().__next__() != 'OTLMOW-GUI':
        path = path.parent

    return path

@fixture
def setup_test_project(root_directory):
    test_subset_file_path:Path = Path("{0}\\demo_projects\\simpel_vergelijkings_project\\simpele_vergelijkings_subset.db".format(
        str(root_directory)))
    project_file_path: Path = Path("{0}\\demo_projects\\simpel_vergelijkings_project\\wizardProject".format(
        str(root_directory)))
    global_vars.current_project = Project(project_path=project_file_path,
                                          subset_path=Path(test_subset_file_path))

@fixture
def mock_project_path(root_directory):
    ProjectFileManager.get_otl_wizard_projects_dir = Mock(return_value=root_directory / "demo_projects" /"simpel_vergelijkings_project")

@fixture
def mock_rel_screen(qtbot, create_translations):
    relation_change_screen = RelationChangeScreen(GlobalTranslate.instance.get_all())
    relation_change_screen.fill_class_list = Mock()
    RelationChangeDomain.get_screen = Mock(return_value=relation_change_screen)
    return relation_change_screen

@fixture
def mock_step3_visuals():
    step3_visuals = Mock(step3_visuals=DataVisualisationScreen)
    main_window =  Mock(step3_visuals=step3_visuals)
    global_vars.otl_wizard = Mock(main_window=main_window)

def test_load_and_validate_document_good_path(mock_screen, root_directory, setup_test_project,
                                              mock_project_path,mock_rel_screen,mock_step3_visuals):

    test_object_lists_file_path: list[str] = ["{0}\\demo_projects\\simpel_vergelijkings_project\\simpel_vergelijking_template2.xlsx".format(str(root_directory))]

    InsertDataDomain.add_files_to_backend_list(test_object_lists_file_path)

    assert(len(InsertDataDomain.documents) == 1)
    assert(list(InsertDataDomain.documents.keys())[0] == test_object_lists_file_path[0])
    assert(list(InsertDataDomain.documents.values())[0] == FileState.WARNING)

    error_set, objects_lists = InsertDataDomain.load_and_validate_documents()

    assert(len(error_set) == 0)
    assert(len(objects_lists) == 1)
    assert (len(objects_lists[0]) == 8)