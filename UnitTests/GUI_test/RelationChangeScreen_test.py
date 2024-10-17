from pathlib import Path
from unittest.mock import Mock

import pytest
from _pytest.fixtures import fixture
from pytestqt.plugin import qtbot
from pytestqt.qtbot import QtBot

from Domain import global_vars
from Domain.InsertDataDomain import InsertDataDomain
from Domain.Project import Project
from Domain.RelationChangeDomain import RelationChangeDomain
from Domain.enums import Language
from GUI.Screens.DataVisualisationScreen import DataVisualisationScreen
from GUI.Screens.InsertDataScreen import InsertDataScreen
from GUI.Screens.RelationChangeScreen import RelationChangeScreen
from GUI.Screens.Screen import Screen
from GUI.translation.GlobalTranslate import GlobalTranslate
from UnitTests.TestClasses.Classes.Onderdeel.AllCasesTestClass import AllCasesTestClass

from UnitTests.general_fixtures.GUIFixtures import *
from UnitTests.general_fixtures.DomainFixtures import *

#################################################
# FULL TESTS                                    #
#################################################
#######################################################
# RelationChangeScreen.fill_possible_relations_list   #
#######################################################
@fixture
def root_directory() -> Path:
    return Path(__file__).parent.parent.parent


@fixture
def mock_screen(qtbot: QtBot, create_translations) -> InsertDataScreen:
    insert_data_screen = InsertDataScreen(GlobalTranslate.instance.get_all())
    InsertDataDomain.get_screen = Mock(return_value=insert_data_screen)
    return insert_data_screen

@fixture
def mock_rel_screen(qtbot: QtBot, create_translations) -> RelationChangeScreen:
    relation_change_screen = RelationChangeScreen(GlobalTranslate.instance.get_all())

    original_get_screen = RelationChangeDomain.get_screen
    RelationChangeDomain.get_screen = Mock(return_value=relation_change_screen)

    yield relation_change_screen

    RelationChangeDomain.get_screen = original_get_screen

@fixture
def mock_step3_visuals() -> None:
    step3_visuals = Mock(step3_visuals=DataVisualisationScreen)
    main_window = Mock(step3_visuals=step3_visuals)
    global_vars.otl_wizard = Mock(main_window=main_window)

def test_fill_class_list(root_directory:Path,
                                mock_screen: InsertDataScreen,
                                mock_rel_screen: RelationChangeScreen,
                                setup_test_project,
                                mock_step3_visuals):

    test_object_lists_file_path: list[str] = [
        str(root_directory / "demo_projects" / "simpel_vergelijkings_project" / "simpel_vergelijking_template2.xlsx")]

    InsertDataDomain.add_files_to_backend_list(test_object_lists_file_path)

    error_set, objects_lists = InsertDataDomain.load_and_validate_documents()

    assert mock_rel_screen.class_list.item(0).text() == "installatie#Verkeersbordopstelling/dummy_hxOTHWe"
    assert mock_rel_screen.class_list.item(1).text() == "installatie#Verkeersbordopstelling/dummy_LGG"
    assert mock_rel_screen.class_list.item(2).text() == "onderdeel#Funderingsmassief/dummy_TyBGmXfXC"
    assert mock_rel_screen.class_list.item(3).text() == "onderdeel#Funderingsmassief/dummy_FNrHuPZCWV"
    assert mock_rel_screen.class_list.item(4).text() == "onderdeel#Pictogram/dummy_a"
    assert mock_rel_screen.class_list.item(5).text() == "onderdeel#Pictogram/dummy_C"
    assert mock_rel_screen.class_list.item(6).text() == "onderdeel#Verkeersbordsteun/dummy_J"
    assert mock_rel_screen.class_list.item(7).text() == "onderdeel#Verkeersbordsteun/dummy_s"

#######################################################
# RelationChangeScreen.fill_possible_relations_list   #
#######################################################
@fixture
def setup_demo_project_in_memory():
    global_vars.current_project = Project(subset_path=Path("C:\\sers\\chris\\PycharmProjects\\OTLMOW-GUI\\demo_projects\\" +
    "simpel_vergelijkings_project\\simpele_vergelijkings_subset.db"))

def test_full_fill_possible_relations_list(qtbot,create_translations,setup_demo_project_in_memory):
    pass


#################################################
# UNIT TESTS                                    #
#################################################

"""
Just adding the qtbot to the fixtures makes the test complete without a timeout when you call a PyQt element
"""
def test_fill_class_list_empty_list(qtbot,create_translations):
    relation_change_screen = RelationChangeScreen(GlobalTranslate.instance.get_all())

    test_objects_list = []
    relation_change_screen.fill_class_list(objects=test_objects_list)

    assert len(relation_change_screen.class_list) == 0

"""
Just adding the qtbot to the fixtures makes the test complete without a timeout when you call a PyQt element
"""
def test_fill_class_list_single_item_list(qtbot,create_translations):
    test_object = AllCasesTestClass()
    test_object.assetId.identificator = "dummy_identificator"

    relation_change_screen = RelationChangeScreen(GlobalTranslate.instance.get_all())

    test_objects_list = [test_object]
    relation_change_screen.fill_class_list(objects=test_objects_list)

    assert len(relation_change_screen.class_list) == 1
    assert relation_change_screen.class_list.item(0).text() == "onderdeel#AllCasesTestClass/dummy_identificator"

"""
Just adding the qtbot to the fixtures makes the test complete without a timeout when you call a PyQt element
"""
def test_fill_class_list_double_item_list(qtbot,create_translations):
    test_object = AllCasesTestClass()
    test_object.assetId.identificator = "dummy_identificator"

    test_object2 = AllCasesTestClass()
    test_object2.assetId.identificator = "dummy_identificator2"

    relation_change_screen = RelationChangeScreen(GlobalTranslate.instance.get_all())
    test_objects_list = [test_object, test_object2]
    relation_change_screen.fill_class_list(objects=test_objects_list)

    assert len(relation_change_screen.class_list) == 2

    assert relation_change_screen.class_list.item(0).text() == "onderdeel#AllCasesTestClass/dummy_identificator"
    assert relation_change_screen.class_list.item(1).text() == "onderdeel#AllCasesTestClass/dummy_identificator2"

