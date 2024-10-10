import sqlite3
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest
from _pytest.fixtures import fixture
from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLAttribuut
from otlmow_modelbuilder.OSLOCollector import OSLOCollector
from otlmow_modelbuilder.SQLDataClasses.OSLORelatie import OSLORelatie
from pytestqt.plugin import qtbot

from Domain.Project import Project
from Domain.RelationChangeDomain import RelationChangeDomain
from GUI.Screens.RelationChangeScreen import RelationChangeScreen
from GUI.translation.GlobalTranslate import GlobalTranslate
from UnitTests.TestClasses.Classes.ImplementatieElement.AIMObject import AIMObject
from UnitTests.TestClasses.Classes.Onderdeel.AllCasesTestClass import AllCasesTestClass
from UnitTests.TestClasses.Classes.Onderdeel.AnotherTestClass import AnotherTestClass


#################################################
# RelationChangeDomain.init_static            #
#################################################

@pytest.fixture
def mock_project():
    return Project()

@pytest.fixture
def mock_oslo_collector():
    with patch('otlmow_modelbuilder.OSLOCollector.OSLOCollector.__init__') as MockCollector:
        MockCollector.return_value = None
        yield MockCollector

@pytest.fixture
def mock_collect_all():
    # with patch('otlmow_modelbuilder.OSLOCollector.collect_all') as Mock_collect_all:
    #     yield Mock_collect_all
    mock_collect_all = Mock()
    OSLOCollector.collect_all = mock_collect_all
    yield mock_collect_all

@pytest.mark.parametrize("subset_path, expected_exception", [
    (patch('pathlib.Path')("valid/path"), None),
    ("valid/path", None),  # edge case: string instead of path
    ("", None),      # edge case: empty path
    (None, None),     # edge case: None path
], ids=["valid_path", "string_path", "empty_path", "none_path"])
def test_init_static(mock_project,mock_collect_all, mock_oslo_collector, subset_path, expected_exception):
    # Arrange
    mock_project.subset_path = subset_path

    # Act
    if expected_exception:
        with pytest.raises(expected_exception):
            RelationChangeDomain.init_static(mock_project)
    else:
        RelationChangeDomain.init_static(mock_project)

    # Assert
    if not expected_exception:
        mock_oslo_collector.assert_called_once_with(subset_path)

    if not expected_exception:
        mock_collect_all.assert_called_once()

#################################################
# RelationChangeDomain.set_objects              #
#################################################

@fixture
def create_translations():
    lang_dir = Path(Path(__file__).absolute()).parent.parent.parent / 'locale/'
    setting={"language": "DUTCH"}
    GlobalTranslate(settings=setting,lang_dir=str(lang_dir))

@fixture
def mock_screen(qtbot, create_translations):
    relation_change_screen = RelationChangeScreen(GlobalTranslate.instance.get_all())
    relation_change_screen.fill_class_list = Mock()
    RelationChangeDomain.get_screen = Mock(return_value=relation_change_screen)
    return relation_change_screen

@fixture
def mock_fill_class_list(mock_screen):
    mock_screen.fill_class_list = Mock()

def test_set_objects_empty_list(mock_fill_class_list):
    RelationChangeDomain.set_objects([])

    assert len(RelationChangeDomain.objects) == 0

def test_set_objects_single_item_list(mock_fill_class_list):
    test_object = AllCasesTestClass()
    test_object.assetId.identificator = "dummy_identificator"
    RelationChangeDomain.set_objects([test_object])

    assert len(RelationChangeDomain.objects) == 1
    assert RelationChangeDomain.objects[0].assetId.identificator == "dummy_identificator"

def test_set_objects_double_item_list(mock_fill_class_list):
    test_object = AllCasesTestClass()
    test_object.assetId.identificator = "dummy_identificator"

    test_object2 = AllCasesTestClass()
    test_object2.assetId.identificator = "dummy_identificator2"

    RelationChangeDomain.set_objects([test_object, test_object2])
    assert len(RelationChangeDomain.objects) == 2

    assert RelationChangeDomain.objects[0].assetId.identificator == "dummy_identificator"
    assert RelationChangeDomain.objects[1].assetId.identificator == "dummy_identificator2"


#################################################
# RelationChangeDomain.set_possible_relations   #
#################################################

@fixture
def mock_fill_possible_relations_list(mock_screen):
    mock_screen.fill_possible_relations_list = Mock()

@fixture
def mock_OSLORelatie():
    return Mock(spec=OSLORelatie)

@fixture
def mock_collector(mock_OSLORelatie):
    mock_find_outgoing_relations = Mock(return_value=[mock_OSLORelatie])()
    OSLOCollector.find_outgoing_relations = mock_find_outgoing_relations

    RelationChangeDomain.collector = Mock(spec=OSLOCollector)

    return mock_find_outgoing_relations

def test_set_possible_relations_single_item_list(mock_fill_possible_relations_list
                                                 ,mock_collector):
    test_object = AllCasesTestClass()
    test_object.assetId.identificator = "dummy_identificator"
    RelationChangeDomain.set_possible_relations(test_object)

    assert len(RelationChangeDomain.possible_relations_per_object.keys()) == 1
    assert list(RelationChangeDomain.possible_relations_per_object.keys())[0] == test_object.typeURI
    assert RelationChangeDomain.possible_relations_per_object[test_object.typeURI]

def test_set_possible_relations_double_item_list(mock_fill_possible_relations_list
                                                 ,mock_collector):
    test_object = AllCasesTestClass()
    test_object.assetId.identificator = "dummy_identificator"

    test_object2 = AnotherTestClass()
    test_object2.assetId.identificator = "dummy_identificator2"

    RelationChangeDomain.set_possible_relations(test_object)
    RelationChangeDomain.set_possible_relations(test_object2)
    assert len(RelationChangeDomain.possible_relations_per_object.keys()) == 2

    assert  list(RelationChangeDomain.possible_relations_per_object.keys())[0] == test_object.typeURI
    assert  list(RelationChangeDomain.possible_relations_per_object.keys())[1] == test_object2.typeURI

    # TODO: make this into a proper list of objects
    assert RelationChangeDomain.possible_relations_per_object[test_object.typeURI]
    # assert isinstance(RelationChangeDomain.possible_relations_per_object[test_object.typeURI][0],
    #                   OSLORelatie)
    assert RelationChangeDomain.possible_relations_per_object[test_object2.typeURI]
    # assert isinstance(RelationChangeDomain.possible_relations_per_object[test_object2.typeURI][0],
    #                   OSLORelatie)
