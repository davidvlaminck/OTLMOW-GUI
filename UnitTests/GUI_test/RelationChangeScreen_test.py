from pathlib import Path
from unittest.mock import Mock

import pytest
from _pytest.fixtures import fixture
from pytestqt.plugin import qtbot

from Domain import global_vars
from Domain.Project import Project
from Domain.enums import Language
from GUI.Screens.RelationChangeScreen import RelationChangeScreen
from GUI.Screens.Screen import Screen
from GUI.translation.GlobalTranslate import GlobalTranslate
from UnitTests.TestClasses.Classes.Onderdeel.AllCasesTestClass import AllCasesTestClass

@fixture
def create_translations():
    lang_dir = Path(Path(__file__).absolute()).parent.parent.parent / 'locale/'
    setting={"language": "DUTCH"}
    GlobalTranslate(settings=setting,lang_dir=str(lang_dir))

#################################################
# FULL TESTS                                    #
#################################################
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

