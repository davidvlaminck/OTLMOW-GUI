from unittest.mock import Mock

from _pytest.fixtures import fixture
from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLAttribuut

from Domain.RelationChangeDomain import RelationChangeDomain
from GUI.Screens.RelationChangeScreen import RelationChangeScreen
from UnitTests.TestClasses.Classes.ImplementatieElement.AIMObject import AIMObject
from UnitTests.TestClasses.Classes.Onderdeel.AllCasesTestClass import AllCasesTestClass


@fixture
def mock_setup():
    relation_change_screen = RelationChangeScreen()
    relation_change_screen.fill_class_list = Mock()
    RelationChangeDomain.get_screen = Mock(return_value=relation_change_screen)


def test_set_objects_empty_list(mock_setup):
    RelationChangeDomain.set_objects([])

    assert len(RelationChangeDomain.objects) == 0

def test_set_objects_single_item_list(mock_setup):
    test_object = AllCasesTestClass()
    test_object.assetId.identificator = "dummy_identificator"
    RelationChangeDomain.set_objects([test_object])

    assert len(RelationChangeDomain.objects) == 1
    assert RelationChangeDomain.objects[0].assetId.identificator == "dummy_identificator"

def test_set_objects_double_item_list(mock_setup):
    test_object = AllCasesTestClass()
    test_object.assetId.identificator = "dummy_identificator"

    test_object2 = AllCasesTestClass()
    test_object2.assetId.identificator = "dummy_identificator2"

    RelationChangeDomain.set_objects([test_object, test_object2])
    assert len(RelationChangeDomain.objects) == 2

    assert RelationChangeDomain.objects[0].assetId.identificator == "dummy_identificator"
    assert RelationChangeDomain.objects[1].assetId.identificator == "dummy_identificator2"