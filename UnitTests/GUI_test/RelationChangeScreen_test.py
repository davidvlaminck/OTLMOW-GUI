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

    assert mock_rel_screen.object_list_gui.item(0).text() == "installatie#Verkeersbordopstelling | dummy_hxOTHWe"
    assert mock_rel_screen.object_list_gui.item(1).text() == "installatie#Verkeersbordopstelling | dummy_LGG"
    assert mock_rel_screen.object_list_gui.item(2).text() == "onderdeel#Funderingsmassief | dummy_TyBGmXfXC"
    assert mock_rel_screen.object_list_gui.item(3).text() == "onderdeel#Funderingsmassief | dummy_FNrHuPZCWV"
    assert mock_rel_screen.object_list_gui.item(4).text() == "onderdeel#Pictogram | dummy_a"
    assert mock_rel_screen.object_list_gui.item(5).text() == "onderdeel#Pictogram | dummy_C"
    assert mock_rel_screen.object_list_gui.item(6).text() == "onderdeel#Verkeersbordsteun | dummy_J"
    assert mock_rel_screen.object_list_gui.item(7).text() == "onderdeel#Verkeersbordsteun | dummy_s"

#######################################################
# RelationChangeScreen.fill_possible_relations_list   #
#######################################################
def test_full_fill_possible_relations_list(qtbot,root_directory:Path,
                                mock_screen: InsertDataScreen,
                                mock_rel_screen: RelationChangeScreen,
                                setup_test_project,
                                mock_step3_visuals):
    test_object_lists_file_path: list[str] = [
        str(root_directory / "demo_projects" / "simpel_vergelijkings_project" / "simpel_vergelijking_template2.xlsx")]

    InsertDataDomain.add_files_to_backend_list(test_object_lists_file_path)

    error_set, objects_lists = InsertDataDomain.load_and_validate_documents()

    vopstel1 = InsertDataDomain.flatten_list(objects_lists)[0]

    RelationChangeDomain.set_possible_relations(selected_object=vopstel1)

    vopstel1_possible_relations_gui =    [
        'HoortBij <-- dummy_C | onderdeel#Pictogram',
        'HoortBij <-- dummy_a | onderdeel#Pictogram',
        'HoortBij <-- dummy_J | onderdeel#Verkeersbordsteun',
        'HoortBij <-- dummy_s | onderdeel#Verkeersbordsteun']

    real_vopstel1_possible_relations_gui =[RelationChangeDomain.get_screen().possible_relation_list_gui.item(x).text() for x in
                                           range(RelationChangeDomain.get_screen().possible_relation_list_gui.count())]

    assert real_vopstel1_possible_relations_gui == vopstel1_possible_relations_gui

    fund1 = InsertDataDomain.flatten_list(objects_lists)[2]

    RelationChangeDomain.set_possible_relations(selected_object=fund1)
    fund1_possible_relations_gui = [
        'Bevestiging <-> dummy_FNrHuPZCWV | onderdeel#Funderingsmassief',
        'LigtOp --> dummy_FNrHuPZCWV | onderdeel#Funderingsmassief',
        'Bevestiging <-> dummy_C | onderdeel#Pictogram',
        'Bevestiging <-> dummy_a | onderdeel#Pictogram',
        'Bevestiging <-> dummy_J | onderdeel#Verkeersbordsteun',
        'Bevestiging <-> dummy_s | onderdeel#Verkeersbordsteun']

    real_fund1_possible_relations_gui = [RelationChangeDomain.get_screen().possible_relation_list_gui.item(x).text() for x in
                                         range(RelationChangeDomain.get_screen().possible_relation_list_gui.count())]

    assert real_fund1_possible_relations_gui == fund1_possible_relations_gui

    #check the data that is stored in the list elements
    data1 = [RelationChangeDomain.get_screen().possible_relation_list_gui.item(x).data(3) for x in
             range(RelationChangeDomain.get_screen().possible_relation_list_gui.count())]

    fund1_possible_relations_gui_data1 = [fund1.assetId.identificator for _ in fund1_possible_relations_gui]

    assert data1 == fund1_possible_relations_gui_data1

    data2 = [RelationChangeDomain.get_screen().possible_relation_list_gui.item(x).data(4) for x in
             range(RelationChangeDomain.get_screen().possible_relation_list_gui.count())]

    fund1_possible_relations_gui_data2 = [
        'dummy_FNrHuPZCWV',
        'dummy_FNrHuPZCWV',
        'dummy_C',
        'dummy_a',
        'dummy_vbeo',
        'dummy_TjwXqP']

    assert data2 == fund1_possible_relations_gui_data2

    fund1_possible_relations_gui_data3 = [0,1,0,0,0,0]

    data3 = [RelationChangeDomain.get_screen().possible_relation_list_gui.item(x).data(5) for x in
             range(RelationChangeDomain.get_screen().possible_relation_list_gui.count())]

    assert data3 == fund1_possible_relations_gui_data3


#######################################################
# RelationChangeScreen.fill_possible_relations_list   #
#######################################################
def test_full_fill_existing_relations_list(qtbot,root_directory:Path,
                                mock_screen: InsertDataScreen,
                                mock_rel_screen: RelationChangeScreen,
                                setup_test_project,
                                mock_step3_visuals):
    test_object_lists_file_path: list[str] = [
        str(root_directory / "demo_projects" / "simpel_vergelijkings_project" / "simpel_vergelijking_template2.xlsx")]

    InsertDataDomain.add_files_to_backend_list(test_object_lists_file_path)

    error_set, objects_lists = InsertDataDomain.load_and_validate_documents()

    existing_relations_gui =    ['Bevestiging | dummy_a <-> dummy_TyBGmXfXC',
                                          'Bevestiging | None <-> None',
                                          'HoortBij | dummy_J --> dummy_LGG',
                                          'LigtOp | dummy_FNrHuPZCWV --> dummy_TyBGmXfXC']

    real_existing_relations_gui =[RelationChangeDomain.get_screen().existing_relation_list_gui.item(x).text() for x in range(RelationChangeDomain.get_screen().existing_relation_list_gui.count())]

    assert real_existing_relations_gui == existing_relations_gui

#################################################
# UNIT TESTS                                    #
#################################################

"""
Just adding the qtbot to the fixtures makes the test complete without a timeout when you call a PyQt element
"""
def test_fill_class_list_empty_list(qtbot,create_translations):
    relation_change_screen = RelationChangeScreen(GlobalTranslate.instance.get_all())

    test_objects_list = []
    relation_change_screen.fill_object_list(objects=test_objects_list)

    assert len(relation_change_screen.object_list_gui) == 0

"""
Just adding the qtbot to the fixtures makes the test complete without a timeout when you call a PyQt element
"""
def test_fill_class_list_single_item_list(qtbot,create_translations):
    test_object = AllCasesTestClass()
    test_object.assetId.identificator = "dummy_identificator"

    relation_change_screen = RelationChangeScreen(GlobalTranslate.instance.get_all())

    test_objects_list = [test_object]
    relation_change_screen.fill_object_list(objects=test_objects_list)

    assert len(relation_change_screen.object_list_gui) == 1
    assert relation_change_screen.object_list_gui.item(0).text() == "onderdeel#AllCasesTestClass | dummy_identificator"

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
    relation_change_screen.fill_object_list(objects=test_objects_list)

    assert len(relation_change_screen.object_list_gui) == 2

    assert relation_change_screen.object_list_gui.item(0).text() == "onderdeel#AllCasesTestClass | dummy_identificator"
    assert relation_change_screen.object_list_gui.item(1).text() == "onderdeel#AllCasesTestClass | dummy_identificator2"

