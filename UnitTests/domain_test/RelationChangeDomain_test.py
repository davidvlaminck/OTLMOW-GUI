import sqlite3

from ctypes.wintypes import PRECT
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest
from _pytest.fixtures import fixture
from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLAttribuut
from otlmow_model.OtlmowModel.Classes.Installatie.Verkeersbordopstelling import \
    Verkeersbordopstelling
from otlmow_model.OtlmowModel.Classes.Onderdeel.Funderingsmassief import Funderingsmassief
from otlmow_model.OtlmowModel.Classes.Onderdeel.Pictogram import Pictogram
from otlmow_model.OtlmowModel.Classes.Onderdeel.Verkeersbordsteun import Verkeersbordsteun
from otlmow_modelbuilder.OSLOCollector import OSLOCollector
from otlmow_modelbuilder.SQLDataClasses.OSLORelatie import OSLORelatie
from parso.python.tree import Function
from typing import Optional
from pytestqt.plugin import qtbot
from pytestqt.qtbot import QtBot

from Domain.InsertDataDomain import InsertDataDomain
from Domain.Project import Project
from Domain.RelationChangeDomain import RelationChangeDomain
from GUI.Screens.DataVisualisationScreen import DataVisualisationScreen
from GUI.Screens.InsertDataScreen import InsertDataScreen
from GUI.Screens.RelationChangeScreen import RelationChangeScreen
from GUI.translation.GlobalTranslate import GlobalTranslate
from UnitTests.TestClasses.Classes.ImplementatieElement.AIMObject import AIMObject
from UnitTests.TestClasses.Classes.Onderdeel.AllCasesTestClass import AllCasesTestClass
from UnitTests.TestClasses.Classes.Onderdeel.AnotherTestClass import AnotherTestClass

from UnitTests.general_fixtures.GUIFixtures import *
from UnitTests.general_fixtures.DomainFixtures import *
#################################################
# FULL TESTS                                    #
#################################################
#################################################
# RelationChangeDomain.set_possible_relations   #
#################################################
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

    original_fill_class_list = RelationChangeScreen.fill_object_list
    RelationChangeScreen.fill_object_list = Mock()

    original_get_screen = RelationChangeDomain.get_screen
    RelationChangeDomain.get_screen = Mock(return_value=relation_change_screen)

    yield relation_change_screen

    RelationChangeScreen.fill_object_list = original_fill_class_list
    RelationChangeDomain.get_screen = original_get_screen


@fixture
def mock_fill_possible_relations_list(mock_rel_screen: RelationChangeScreen):
    mock_rel_screen.fill_possible_relations_list = Mock()

@fixture
def mock_step3_visuals() -> None:
    step3_visuals = Mock(step3_visuals=DataVisualisationScreen)
    main_window = Mock(step3_visuals=step3_visuals)
    global_vars.otl_wizard = Mock(main_window=main_window)

def id(aim_object: AIMObject):
    return aim_object.assetId.identificator

def test_set_possible_relations(root_directory:Path,
                                mock_screen: InsertDataScreen,
                                mock_fill_possible_relations_list: RelationChangeScreen,
                                setup_test_project,
                                mock_step3_visuals):

    test_object_lists_file_path: list[str] = [
        str(root_directory / "demo_projects" / "simpel_vergelijkings_project" / "simpel_vergelijking_template2.xlsx")]

    InsertDataDomain.add_files_to_backend_list(test_object_lists_file_path)

    error_set, objects_lists = InsertDataDomain.load_and_validate_documents()

    for objects_list in objects_lists:
        for object in objects_list:
            RelationChangeDomain.set_possible_relations(object)

    assert len(RelationChangeDomain.possible_relations_per_class.keys()) == 4
    # search with regex for (#Verkeersbordopstelling'|#Pictogram'|#Funderingsmassief'|#verkeersbordsteun'|BevestigingGC'|#Draagconstructie'|#Fundering'|#ConstructieElement')
    class1 = "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Verkeersbordsteun"
    #TODO: update this when otlmow-converter is fixed
    assert len(RelationChangeDomain.possible_relations_per_class[class1]) == 3

    class2 = "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Funderingsmassief"
    # TODO: update this when otlmow-converter is fixed
    assert len(RelationChangeDomain.possible_relations_per_class[class2]) == 4

    class3 = "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Pictogram"
    # TODO: update this when otlmow-converter is fixed
    assert len(RelationChangeDomain.possible_relations_per_class[class3]) == 3

    class4 = "https://wegenenverkeer.data.vlaanderen.be/ns/installatie#Verkeersbordopstelling"
    # TODO: update this when otlmow-converter is fixed
    assert len(RelationChangeDomain.possible_relations_per_class[class4]) == 2

    #define the objects of each class in the test set
    for objects_list in objects_lists:
        for object in objects_list:
            if object.assetId.identificator == "dummy_vbeo":
                verkeersbordsteun1: AIMObject = object
            elif  object.assetId.identificator == "dummy_TjwXqP":
                verkeersbordsteun2: AIMObject  = object
            elif  object.assetId.identificator == "dummy_hxOTHWe":
                verkeersbordopstelling1: AIMObject  = object
            elif object.assetId.identificator == "dummy_LGG":
                verkeersbordopstelling2: AIMObject  = object
            elif object.assetId.identificator == "dummy_a":
                pictogram1: AIMObject  = object
            elif object.assetId.identificator == "dummy_C":
                pictogram2: AIMObject  = object
            elif object.assetId.identificator == "dummy_TyBGmXfXC":
                funderingsmassief1: AIMObject  = object
            elif object.assetId.identificator == "dummy_FNrHuPZCWV":
                funderingsmassief2: AIMObject  = object

    # define the relations in the test subset
    all_relations:list[OSLORelatie] = RelationChangeDomain.collector.relations
    for relation in all_relations:
        if relation.usagenote == "fund_bevestiging_vsteun":
            fund_bevestiging_vsteun: OSLORelatie = relation
        elif relation.usagenote == "vsteun_bevestiging_fund":
            vsteun_bevestiging_fund: OSLORelatie = relation
        elif relation.usagenote == "pict_hoortbij_vopstel":
            pict_hoortbij_vopstel: OSLORelatie = relation
        elif relation.usagenote == "fund_ligtop_fund":
            fund_ligtop_fund: OSLORelatie = relation
        elif relation.usagenote == "conele_ligtop_fund":
            conele_ligtop_fund: OSLORelatie = relation
        elif relation.usagenote == "pict_bevestiging_fund":
             pict_bevestiging_fund: OSLORelatie = relation
        elif relation.usagenote == "fund_bevestiging_pict":
             fund_bevestiging_pict: OSLORelatie = relation
        elif relation.usagenote == "conelem_bevestiging_pict":
             conelem_bevestiging_pict: OSLORelatie = relation
        elif relation.usagenote == "fund_bevestiging_fund":
             fund_bevestiging_fund: OSLORelatie = relation
        elif relation.usagenote == "vsteun_hoortbij_vopstel":
             vsteun_hoortbij_vopstel: OSLORelatie = relation
        elif relation.usagenote == "dracon_hoortbij_vopstel":
             dracon_hoortbij_vopstel: OSLORelatie = relation
        elif relation.usagenote == "pict_bevestiging_vsteun":
             pict_bevestiging_vsteun: OSLORelatie = relation
        elif relation.usagenote == "vsteun_bevestiging_pict":
             vsteun_bevestiging_pict: OSLORelatie = relation
        elif relation.usagenote == "dracon_bevestiging_pict":
             dracon_bevestiging_pict: OSLORelatie = relation

    relationObject = RelationChangeDomain.create_relation_object(fund_bevestiging_vsteun,funderingsmassief1,verkeersbordsteun1)

    poss_rel = {}
    fund1_id = id(funderingsmassief1)
    poss_rel[fund1_id] = {}
    poss_rel[fund1_id][id(verkeersbordsteun1)] = [RelationChangeDomain.create_relation_object(fund_bevestiging_vsteun,funderingsmassief1,verkeersbordsteun1)]
    poss_rel[fund1_id][id(verkeersbordsteun2)] = [RelationChangeDomain.create_relation_object(fund_bevestiging_vsteun,funderingsmassief1,verkeersbordsteun2)]
    poss_rel[fund1_id][id(funderingsmassief1)] = [RelationChangeDomain.create_relation_object(fund_ligtop_fund,funderingsmassief1,funderingsmassief1)] # not with itself
    poss_rel[fund1_id][id(funderingsmassief2)] = [RelationChangeDomain.create_relation_object(fund_ligtop_fund,funderingsmassief1,funderingsmassief2)]
    poss_rel[fund1_id][id(pictogram1)] = [RelationChangeDomain.create_relation_object(fund_bevestiging_pict,funderingsmassief1,pictogram1)]
    poss_rel[fund1_id][id(pictogram2)] = [RelationChangeDomain.create_relation_object(fund_bevestiging_pict,funderingsmassief1,pictogram2)]
    poss_rel[fund1_id][id(funderingsmassief1)].append(RelationChangeDomain.create_relation_object(fund_bevestiging_fund,funderingsmassief1,funderingsmassief1))# not with itself
    poss_rel[fund1_id][id(funderingsmassief2)].append(RelationChangeDomain.create_relation_object(fund_bevestiging_fund,funderingsmassief1,funderingsmassief1))

    fund2_id = id(funderingsmassief2)
    poss_rel[fund2_id] = {}
    poss_rel[fund2_id][id(verkeersbordsteun1)] = [RelationChangeDomain.create_relation_object(fund_bevestiging_vsteun,funderingsmassief2,verkeersbordsteun1)]
    poss_rel[fund2_id][id(verkeersbordsteun2)] = [RelationChangeDomain.create_relation_object(fund_bevestiging_vsteun,funderingsmassief2,verkeersbordsteun2)]
    poss_rel[fund2_id][id(funderingsmassief1)] = [RelationChangeDomain.create_relation_object(fund_ligtop_fund,funderingsmassief2,funderingsmassief1)]
    poss_rel[fund2_id][id(funderingsmassief2)] = [RelationChangeDomain.create_relation_object(fund_ligtop_fund,funderingsmassief2,funderingsmassief2)]# not with itself
    poss_rel[fund2_id][id(pictogram1)] = [RelationChangeDomain.create_relation_object(fund_bevestiging_pict,funderingsmassief2,pictogram1)]
    poss_rel[fund2_id][id(pictogram2)] = [RelationChangeDomain.create_relation_object(fund_bevestiging_pict,funderingsmassief2,pictogram2)]
    poss_rel[fund2_id][id(funderingsmassief1)].append(RelationChangeDomain.create_relation_object(fund_bevestiging_fund,funderingsmassief2,funderingsmassief1))
    poss_rel[fund2_id][id(funderingsmassief2)].append(RelationChangeDomain.create_relation_object(fund_bevestiging_fund,funderingsmassief2,funderingsmassief2))# not with itself

    vsteun1_id = id(verkeersbordsteun1)
    poss_rel[vsteun1_id] = {}
    # phase 1 : selected object is source (bron)
    poss_rel[vsteun1_id][id(funderingsmassief1)] = [RelationChangeDomain.create_relation_object(vsteun_bevestiging_fund,verkeersbordsteun1,funderingsmassief1)]
    poss_rel[vsteun1_id][id(funderingsmassief2)] = [RelationChangeDomain.create_relation_object(vsteun_bevestiging_fund,verkeersbordsteun1,funderingsmassief2)]
    poss_rel[vsteun1_id][id(pictogram1)] = [RelationChangeDomain.create_relation_object(vsteun_bevestiging_pict,verkeersbordsteun1,pictogram1)]
    poss_rel[vsteun1_id][id(pictogram2)] = [RelationChangeDomain.create_relation_object(vsteun_bevestiging_pict,verkeersbordsteun1,pictogram2)]
    poss_rel[vsteun1_id][id(verkeersbordopstelling1)] = [RelationChangeDomain.create_relation_object(vsteun_hoortbij_vopstel,verkeersbordsteun1,verkeersbordopstelling1)]
    poss_rel[vsteun1_id][id(verkeersbordopstelling2)] = [RelationChangeDomain.create_relation_object(vsteun_hoortbij_vopstel,verkeersbordsteun1,verkeersbordopstelling2)]

    vsteun2_id = id(verkeersbordsteun2)
    poss_rel[vsteun2_id] = {}
    # phase 1 : selected object is source (bron)
    poss_rel[vsteun2_id][id(funderingsmassief1)] = [RelationChangeDomain.create_relation_object(vsteun_bevestiging_fund,verkeersbordsteun2,funderingsmassief1)]
    poss_rel[vsteun2_id][id(funderingsmassief2)] = [RelationChangeDomain.create_relation_object(vsteun_bevestiging_fund,verkeersbordsteun2,funderingsmassief2)]
    poss_rel[vsteun2_id][id(pictogram1)] = [RelationChangeDomain.create_relation_object(vsteun_bevestiging_pict,verkeersbordsteun2,pictogram1)]
    poss_rel[vsteun2_id][id(pictogram2)] = [RelationChangeDomain.create_relation_object(vsteun_bevestiging_pict,verkeersbordsteun2,pictogram2)]
    poss_rel[vsteun2_id][id(verkeersbordopstelling1)] = [RelationChangeDomain.create_relation_object(vsteun_hoortbij_vopstel,verkeersbordsteun2,verkeersbordopstelling1)]
    poss_rel[vsteun2_id][id(verkeersbordopstelling2)] = [RelationChangeDomain.create_relation_object(vsteun_hoortbij_vopstel,verkeersbordsteun2,verkeersbordopstelling2)]

    pict1_id = id(pictogram1)
    poss_rel[pict1_id] = {}
    # phase 1 : selected object is source (bron)
    poss_rel[pict1_id][id(verkeersbordopstelling1)] = [RelationChangeDomain.create_relation_object(pict_hoortbij_vopstel,pictogram1,verkeersbordopstelling1)]
    poss_rel[pict1_id][id(verkeersbordopstelling2)] = [RelationChangeDomain.create_relation_object(pict_hoortbij_vopstel,pictogram1,verkeersbordopstelling2)]
    poss_rel[pict1_id][id(funderingsmassief1)] = [RelationChangeDomain.create_relation_object(pict_bevestiging_fund,pictogram1,funderingsmassief1)]
    poss_rel[pict1_id][id(funderingsmassief2)] = [RelationChangeDomain.create_relation_object(pict_bevestiging_fund,pictogram1,funderingsmassief2)]
    poss_rel[pict1_id][id(verkeersbordsteun1)] = [RelationChangeDomain.create_relation_object(pict_bevestiging_vsteun,pictogram1,verkeersbordsteun1)]
    poss_rel[pict1_id][id(verkeersbordsteun2)] = [RelationChangeDomain.create_relation_object(pict_bevestiging_vsteun,pictogram1,verkeersbordsteun2)]

    pict2_id = id(pictogram2)
    poss_rel[pict2_id] = {}
    #phase 1 : selected object is source (bron)
    poss_rel[pict2_id][id(verkeersbordopstelling1)] = [RelationChangeDomain.create_relation_object(pict_hoortbij_vopstel,pictogram2,verkeersbordopstelling1)]
    poss_rel[pict2_id][id(verkeersbordopstelling2)] = [RelationChangeDomain.create_relation_object(pict_hoortbij_vopstel,pictogram2,verkeersbordopstelling2)]
    poss_rel[pict2_id][id(funderingsmassief1)] = [RelationChangeDomain.create_relation_object(pict_bevestiging_fund,pictogram2,funderingsmassief1)]
    poss_rel[pict2_id][id(funderingsmassief2)] = [RelationChangeDomain.create_relation_object(pict_bevestiging_fund,pictogram2,funderingsmassief2)]
    poss_rel[pict2_id][id(verkeersbordsteun1)] = [RelationChangeDomain.create_relation_object(pict_bevestiging_vsteun,pictogram2,verkeersbordsteun1)]
    poss_rel[pict2_id][id(verkeersbordsteun2)] = [RelationChangeDomain.create_relation_object(pict_bevestiging_vsteun,pictogram2,verkeersbordsteun2)]
    
    vopstel1_id = id(verkeersbordopstelling1)
    poss_rel[vopstel1_id] = {}
    # phase 1 : selected object is source (bron)
    # phase 2 : selected object is target (doel) converted to incoming relation
    poss_rel[vopstel1_id][id(verkeersbordsteun1)] = [RelationChangeDomain.create_relation_object(vsteun_hoortbij_vopstel,verkeersbordsteun1,verkeersbordopstelling1)]
    poss_rel[vopstel1_id][id(verkeersbordsteun2)] = [RelationChangeDomain.create_relation_object(vsteun_hoortbij_vopstel,verkeersbordsteun2,verkeersbordopstelling1)]

    vopstel2_id = id(verkeersbordopstelling2)
    poss_rel[vopstel2_id] = {}
    # phase 1 : selected object is source (bron)
    # phase 2 : selected object is target (doel) converted to incoming relation

    RelationChangeDomain.sort_nested_dict(poss_rel)

    assert RelationChangeDomain.possible_object_to_object_relations == poss_rel
    # for selected_object_id in poss_rel.keys():
    #     print("test with selected_object id:{0}".format(selected_object_id))
    #     for rel_object_id  in poss_rel[selected_object_id].keys():
    #
    #         if "incl" in poss_rel[selected_object_id][rel_object_id].keys():
    #
    #             for relation in poss_rel[selected_object_id][rel_object_id]["incl"]:
    #                 print("test RelationChangeDomain.possible_object_to_object_relations['{0}']['{1}'] contain {2}".format(
    #                         selected_object_id, rel_object_id, relation.objectUri))
    #                 relations = RelationChangeDomain.possible_object_to_object_relations[selected_object_id][rel_object_id]
    #
    #                 assert  relations.__contains__(relation)
    #
    #         if  poss_rel[selected_object_id][rel_object_id].keys().__contains__("excl"):
    #
    #             for relation in poss_rel[selected_object_id][rel_object_id]["excl"]:
    #                 print("test RelationChangeDomain.possible_object_to_object_relations['{0}']['{1}'] not contain {2}".format(selected_object_id, rel_object_id,relation.objectUri))
    #
    #                 assert not RelationChangeDomain.possible_object_to_object_relations[selected_object_id].keys().__contains__(rel_object_id) or \
    #                        not RelationChangeDomain.possible_object_to_object_relations[selected_object_id][rel_object_id].__contains__(relation)


#################################################
# UNIT TESTS                                    #
#################################################
#################################################
# RelationChangeDomain.init_static            #
#################################################

@pytest.fixture
def mock_project() -> Project:
    return Project()

@pytest.fixture
def mock_oslo_collector() -> Function:
    with patch('otlmow_modelbuilder.OSLOCollector.OSLOCollector.__init__') as mock__init__OSLOColletor:
        mock__init__OSLOColletor.return_value = None
        yield mock__init__OSLOColletor

@pytest.fixture
def mock_collect_all() -> Mock:
    original_collect_all = OSLOCollector.collect_all

    mock_collect_all = Mock()
    OSLOCollector.collect_all = mock_collect_all
    yield mock_collect_all
    # after the test the original collect_all is restored for other tests to use
    OSLOCollector.collect_all = original_collect_all

@pytest.mark.parametrize("subset_path, expected_exception", [
    (patch('pathlib.Path')("valid/path"), None),
    ("valid/path", None),  # edge case: string instead of path
    ("", None),      # edge case: empty path
    (None, None),     # edge case: None path
], ids=["valid_path", "string_path", "empty_path", "none_path"])
def test_init_static(mock_project: Project,mock_collect_all: Mock, mock_oslo_collector: Function, subset_path: str, expected_exception: Optional[Exception]):
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

def test_set_objects_empty_list(mock_screen: RelationChangeScreen):
    RelationChangeDomain.set_instances([])

    assert len(RelationChangeDomain.objects) == 0

def test_set_objects_single_item_list(mock_screen: RelationChangeScreen,mock_collect_all,mock_rel_screen):
    RelationChangeDomain.init_static(Project())
    test_object = AllCasesTestClass()
    test_object.assetId.identificator = "dummy_identificator"
    RelationChangeDomain.set_instances([test_object])

    assert len(RelationChangeDomain.objects) == 1
    assert RelationChangeDomain.objects[0].assetId.identificator == "dummy_identificator"

def test_set_objects_double_item_list(mock_screen,mock_collect_all,mock_rel_screen):
    RelationChangeDomain.init_static(Project())
    test_object = AllCasesTestClass()
    test_object.assetId.identificator = "dummy_identificator"

    test_object2 = AllCasesTestClass()
    test_object2.assetId.identificator = "dummy_identificator2"

    RelationChangeDomain.set_instances([test_object, test_object2])
    assert len(RelationChangeDomain.objects) == 2

    assert RelationChangeDomain.objects[0].assetId.identificator == "dummy_identificator"
    assert RelationChangeDomain.objects[1].assetId.identificator == "dummy_identificator2"


#################################################
# RelationChangeDomain.set_possible_relations   #
#################################################



@fixture
def mock_OSLORelatie() -> Mock:
    return Mock(spec=OSLORelatie)

@fixture
def mock_collector(mock_OSLORelatie: Mock):
    original_find_all_concrete_relations = OSLOCollector.find_all_concrete_relations
    mock_find_all_concrete_relations = Mock(return_value=[mock_OSLORelatie])()
    OSLOCollector.find_all_concrete_relations = mock_find_all_concrete_relations

    original_collector = RelationChangeDomain.collector
    RelationChangeDomain.collector = Mock(spec=OSLOCollector)

    yield mock_find_all_concrete_relations

    OSLOCollector.find_all_concrete_relations = original_find_all_concrete_relations
    RelationChangeDomain.collector = original_collector

@pytest.mark.skip
def test_set_possible_relations_single_item_list(mock_fill_possible_relations_list: RelationChangeScreen
                                                 ,mock_collector:Mock):
    #TODO: do proper mocking of  OSLOCollector.find_all_concrete_relations
    test_object = AllCasesTestClass()
    test_object.assetId.identificator = "dummy_identificator"
    RelationChangeDomain.set_possible_relations(test_object)

    assert len(RelationChangeDomain.possible_relations_per_class.keys()) == 1
    assert list(RelationChangeDomain.possible_relations_per_class.keys())[0] == test_object.typeURI
    assert RelationChangeDomain.possible_relations_per_class[test_object.typeURI]

@pytest.mark.skip
def test_set_possible_relations_double_item_list(mock_fill_possible_relations_list: RelationChangeScreen
                                                 ,mock_collector:Mock):
    # TODO: do proper mocking of  OSLOCollector.find_all_concrete_relations
    test_object = AllCasesTestClass()
    test_object.assetId.identificator = "dummy_identificator"

    test_object2 = AnotherTestClass()
    test_object2.assetId.identificator = "dummy_identificator2"

    RelationChangeDomain.set_possible_relations(test_object)
    RelationChangeDomain.set_possible_relations(test_object2)
    assert len(RelationChangeDomain.possible_relations_per_class.keys()) == 2

    assert list(RelationChangeDomain.possible_relations_per_class.keys())[0] == test_object.typeURI
    assert list(RelationChangeDomain.possible_relations_per_class.keys())[1] == test_object2.typeURI

    # TODO: make this into a proper list of objects
    assert RelationChangeDomain.possible_relations_per_class[test_object.typeURI]
    # assert isinstance(RelationChangeDomain.possible_relations_per_object[test_object.typeURI][0],
    #                   OSLORelatie)
    assert RelationChangeDomain.possible_relations_per_class[test_object2.typeURI]
    # assert isinstance(RelationChangeDomain.possible_relations_per_object[test_object2.typeURI][0],
    #                   OSLORelatie)
