import os
from pathlib import Path
from unittest.mock import Mock

from _pytest.fixtures import fixture
from pytestqt.plugin import qtbot
from pytestqt.qtbot import QtBot

from Domain import global_vars
from Domain.InsertDataDomain import InsertDataDomain
from Domain.Project import Project
from Domain.ProjectFileManager import ProjectFileManager
from Domain.RelationChangeDomain import RelationChangeDomain
from Domain.enums import FileState
from GUI.Screens.DataVisualisationScreen import DataVisualisationScreen
from GUI.Screens.InsertDataScreen import InsertDataScreen
from GUI.Screens.RelationChangeScreen import RelationChangeScreen

from UnitTests.general_fixtures.GUIFixtures import *
from UnitTests.general_fixtures.DomainFixtures import *

#################################################
# FULL TESTS                                    #
#################################################
#######################################################
# InsertDataDomain.load_and_validate_document         #
#######################################################


@fixture
def mock_screen(qtbot: QtBot, create_translations) -> InsertDataScreen:
    relation_change_screen = InsertDataScreen(GlobalTranslate.instance.get_all())
    relation_change_screen.fill_class_list = Mock()
    InsertDataDomain.get_screen = Mock(return_value=relation_change_screen)
    return relation_change_screen

@fixture
def mock_rel_screen(qtbot: QtBot, create_translations) -> RelationChangeScreen:
    relation_change_screen = RelationChangeScreen(GlobalTranslate.instance.get_all())
    relation_change_screen.fill_class_list = Mock()
    RelationChangeDomain.get_screen = Mock(return_value=relation_change_screen)
    return relation_change_screen

@fixture
def mock_step3_visuals() -> None:
    step3_visuals = Mock(step3_visuals=DataVisualisationScreen)
    main_window =  Mock(step3_visuals=step3_visuals)
    global_vars.otl_wizard = Mock(main_window=main_window)

def test_load_and_validate_document_good_path(mock_screen: InsertDataScreen,
                                              root_directory: Path,
                                              setup_test_project,
                                              mock_rel_screen: RelationChangeScreen,
                                              mock_step3_visuals) -> None:

    test_object_lists_file_path: list[str] = ["{0}\\demo_projects\\simpel_vergelijkings_project\\simpel_vergelijking_template2.xlsx".format(str(root_directory))]

    InsertDataDomain.add_files_to_backend_list(test_object_lists_file_path)

    assert(len(InsertDataDomain.documents) == 1)
    assert(list(InsertDataDomain.documents.keys())[0] == test_object_lists_file_path[0])
    assert(list(InsertDataDomain.documents.values())[0] == FileState.WARNING)

    error_set, objects_lists = InsertDataDomain.load_and_validate_documents()

    assert(len(error_set) == 0)
    assert(len(objects_lists) == 1)
    assert(len(objects_lists[0]) == 8)
    assert (list(InsertDataDomain.documents.values())[0] == FileState.OK)