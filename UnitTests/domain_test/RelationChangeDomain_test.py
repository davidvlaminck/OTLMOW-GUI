from unittest.mock import patch

from otlmow_model.OtlmowModel.Helpers.OTLObjectHelper import is_relation
from otlmow_modelbuilder.OSLOCollector import OSLOCollector
from otlmow_modelbuilder.SQLDataClasses.OSLORelatie import OSLORelatie
from parso.python.tree import Function
from typing import Optional
from pytestqt.plugin import qtbot
from pytestqt.qtbot import QtBot

from otlmow_gui.GUI.screens.InsertDataScreen import InsertDataScreen
from otlmow_gui.GUI.screens.RelationChangeScreen import RelationChangeScreen
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
    return Path(__file__).parent.parent.parent / 'otlmow_gui'


@pytest.fixture(scope="function")
def mock_screen(qtbot: QtBot, create_translations) -> InsertDataScreen:
    insert_data_screen = InsertDataScreen(GlobalTranslate.instance.get_all())
    InsertDataDomain.get_screen = Mock(return_value=insert_data_screen)
    return insert_data_screen

@pytest.fixture(scope="function")
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
def mock_step3_step3_relations() -> None:
    step3_relations = Mock(step3_visuals=DynamicDataVisualisationScreen)
    main_window = Mock(step3_visuals=step3_relations)
    global_vars.otl_wizard = Mock(main_window=main_window)

def id(aim_object: AIMObject):
    return aim_object.assetId.identificator

@pytest.mark.asyncio
async def test_full_set_possible_relations(root_directory:Path,
                                mock_screen: InsertDataScreen,
                                     setup_simpel_vergelijking_template5,
                                # mock_fill_possible_relations_list: RelationChangeScreen,
                                setup_test_project,
                                mock_step3_visuals,
                                mock_step3_step3_relations,
                                mock_save_validated_assets_function,
                                mock_load_validated_assets):

    test_object_lists_file_path: list[str] = setup_simpel_vergelijking_template5

    InsertDataDomain.add_files_to_backend_list(test_object_lists_file_path)

    error_set, objects_list = await InsertDataDomain.load_and_validate_documents()


    for object in objects_list:
        if not is_relation(object):
            await RelationChangeDomain.set_possible_relations(object)

    assert len(RelationChangeDomain.possible_relations_per_class_dict.keys()) == 4
    # search with regex for (#Verkeersbordopstelling'|#Pictogram'|#Funderingsmassief'|#verkeersbordsteun'|BevestigingGC'|#Draagconstructie'|#Fundering'|#ConstructieElement')
    # with external objects added every relation possible in the entire OTL model is found
    class1 = "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Verkeersbordsteun"
    assert len(RelationChangeDomain.possible_relations_per_class_dict[class1]) == 74

    class2 = "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Funderingsmassief"
    assert len(RelationChangeDomain.possible_relations_per_class_dict[class2]) == 731

    class3 = "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Pictogram"
    assert len(RelationChangeDomain.possible_relations_per_class_dict[class3]) == 118

    class4 = "https://wegenenverkeer.data.vlaanderen.be/ns/installatie#Verkeersbordopstelling"
    assert len(RelationChangeDomain.possible_relations_per_class_dict[class4]) == 33

    #define the objects of each class in the test set

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
        elif object.assetId.identificator == "dummy_long_identificator_pictogram":
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

    poss_rel = {}
    fund1_id = id(funderingsmassief1)
    poss_rel[fund1_id] = {}
    poss_rel[fund1_id][id(verkeersbordsteun1)] = [RelationChangeDomain.create_relation_object(fund_bevestiging_vsteun,funderingsmassief1,verkeersbordsteun1)]
    poss_rel[fund1_id][id(verkeersbordsteun2)] = [RelationChangeDomain.create_relation_object(fund_bevestiging_vsteun,funderingsmassief1,verkeersbordsteun2)]
    # poss_rel[fund1_id][id(funderingsmassief1)] = [RelationChangeDomain.create_relation_object(fund_ligtop_fund,funderingsmassief1,funderingsmassief1)] # not with itself
    poss_rel[fund1_id][id(funderingsmassief2)] =  RelationChangeDomain.get_same_relations_in_list(
        RelationChangeDomain.aim_id_relations, fund_ligtop_fund, funderingsmassief2,
        funderingsmassief1)# already in existing relations
    poss_rel[fund1_id][id(funderingsmassief2)].extend([RelationChangeDomain.create_relation_object(fund_ligtop_fund,funderingsmassief1,funderingsmassief2)])  # already in existing relations

    # poss_rel[fund1_id][id(pictogram1)] = [RelationChangeDomain.create_relation_object(fund_bevestiging_pict,funderingsmassief1,pictogram1)]# already in existing relations
    poss_rel[fund1_id][id(pictogram2)] = [RelationChangeDomain.create_relation_object(fund_bevestiging_pict,funderingsmassief1,pictogram2)]
    # poss_rel[fund1_id][id(funderingsmassief1)].append(RelationChangeDomain.create_relation_object(fund_bevestiging_fund,funderingsmassief1,funderingsmassief1))# not with itself
    poss_rel[fund1_id][id(funderingsmassief2)].append(RelationChangeDomain.create_relation_object(fund_bevestiging_fund,funderingsmassief1,funderingsmassief2))

    fund2_id = id(funderingsmassief2)
    poss_rel[fund2_id] = {}
    poss_rel[fund2_id][id(verkeersbordsteun1)] = [RelationChangeDomain.create_relation_object(fund_bevestiging_vsteun,funderingsmassief2,verkeersbordsteun1)]
    poss_rel[fund2_id][id(verkeersbordsteun2)] = [RelationChangeDomain.create_relation_object(fund_bevestiging_vsteun,funderingsmassief2,verkeersbordsteun2)]
    poss_rel[fund2_id][id(funderingsmassief1)] = RelationChangeDomain.get_same_relations_in_list(RelationChangeDomain.aim_id_relations,fund_ligtop_fund,funderingsmassief2,funderingsmassief1) # already in existing relations
    poss_rel[fund2_id][id(funderingsmassief1)].append(RelationChangeDomain.create_relation_object(
        fund_ligtop_fund, funderingsmassief1, funderingsmassief2))  # already in existing relations
    # poss_rel[fund2_id][id(funderingsmassief2)] = [RelationChangeDomain.create_relation_object(fund_ligtop_fund,funderingsmassief2,funderingsmassief2)]# not with itself
    poss_rel[fund2_id][id(pictogram1)] = [RelationChangeDomain.create_relation_object(fund_bevestiging_pict,funderingsmassief2,pictogram1)]
    poss_rel[fund2_id][id(pictogram2)] = [RelationChangeDomain.create_relation_object(fund_bevestiging_pict,funderingsmassief2,pictogram2)]
    poss_rel[fund2_id][id(funderingsmassief1)].append(RelationChangeDomain.create_relation_object(fund_bevestiging_fund,funderingsmassief2,funderingsmassief1))
    # poss_rel[fund2_id][id(funderingsmassief2)].append(RelationChangeDomain.create_relation_object(fund_bevestiging_fund,funderingsmassief2,funderingsmassief2))# not with itself

    vsteun1_id = id(verkeersbordsteun1)
    poss_rel[vsteun1_id] = {}
    # phase 1 : selected object is source (bron)
    poss_rel[vsteun1_id][id(funderingsmassief1)] = [RelationChangeDomain.create_relation_object(vsteun_bevestiging_fund,verkeersbordsteun1,funderingsmassief1)]
    poss_rel[vsteun1_id][id(funderingsmassief2)] = [RelationChangeDomain.create_relation_object(vsteun_bevestiging_fund,verkeersbordsteun1,funderingsmassief2)]
    poss_rel[vsteun1_id][id(pictogram1)] = [RelationChangeDomain.create_relation_object(vsteun_bevestiging_pict,verkeersbordsteun1,pictogram1)]
    poss_rel[vsteun1_id][id(pictogram2)] = [RelationChangeDomain.create_relation_object(vsteun_bevestiging_pict,verkeersbordsteun1,pictogram2)]
    poss_rel[vsteun1_id][id(verkeersbordopstelling1)] = [RelationChangeDomain.create_relation_object(vsteun_hoortbij_vopstel,verkeersbordsteun1,verkeersbordopstelling1)]
    # poss_rel[vsteun1_id][id(verkeersbordopstelling2)] = [RelationChangeDomain.create_relation_object(vsteun_hoortbij_vopstel,verkeersbordsteun1,verkeersbordopstelling2)] # already in existing relations

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
    # poss_rel[pict1_id][id(funderingsmassief1)] = [RelationChangeDomain.create_relation_object(pict_bevestiging_fund,pictogram1,funderingsmassief1)] # already in existing relations
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
    poss_rel[vopstel1_id][id(pictogram1)] = [RelationChangeDomain.create_relation_object(vsteun_hoortbij_vopstel, pictogram1,verkeersbordopstelling1)]
    poss_rel[vopstel1_id][id(pictogram2)] = [RelationChangeDomain.create_relation_object(vsteun_hoortbij_vopstel, pictogram2,verkeersbordopstelling1)]

    vopstel2_id = id(verkeersbordopstelling2)
    poss_rel[vopstel2_id] = {}
    # phase 1 : selected object is source (bron)
    # phase 2 : selected object is target (doel) converted to incoming relation
    # poss_rel[vopstel2_id][id(verkeersbordsteun1)] = [RelationChangeDomain.create_relation_object(vsteun_hoortbij_vopstel, verkeersbordsteun1,verkeersbordopstelling2)] # already in existing relations
    poss_rel[vopstel2_id][id(verkeersbordsteun2)] = [RelationChangeDomain.create_relation_object(vsteun_hoortbij_vopstel, verkeersbordsteun2,verkeersbordopstelling2)]
    poss_rel[vopstel2_id][id(pictogram1)] = [RelationChangeDomain.create_relation_object(vsteun_hoortbij_vopstel, pictogram1,verkeersbordopstelling2)]
    poss_rel[vopstel2_id][id(pictogram2)] = [RelationChangeDomain.create_relation_object(vsteun_hoortbij_vopstel, pictogram2,verkeersbordopstelling2)]


    poss_rel = Helpers.sort_nested_dict(poss_rel)

    for selected_object_id in poss_rel.keys():
        print("test with selected_object id:{0}".format(selected_object_id))
        for rel_object_id  in poss_rel[selected_object_id].keys():
            assert RelationChangeDomain.possible_object_to_object_relations_dict[selected_object_id][rel_object_id] == poss_rel[selected_object_id][rel_object_id]


@pytest.mark.asyncio
async def test_full_add_possible_relation_to_existing_relation(root_directory:Path,
                                                         setup_simpel_vergelijking_template2,
                                mock_screen: InsertDataScreen,
                                mock_fill_possible_relations_list: RelationChangeScreen,
                                setup_test_project,
                                mock_step3_visuals,mock_save_validated_assets_function,
                                 mock_load_validated_assets):
    test_object_lists_file_path: list[str] = setup_simpel_vergelijking_template2

    InsertDataDomain.add_files_to_backend_list(test_object_lists_file_path)

    error_set, objects_list = await InsertDataDomain.load_and_validate_documents()


    for object in objects_list:
        await RelationChangeDomain.set_possible_relations(object)

    bron_asset_id = list(RelationChangeDomain.possible_object_to_object_relations_dict.keys())[0]
    target_asset_id = list(RelationChangeDomain.possible_object_to_object_relations_dict[bron_asset_id].keys())[0]
    relation_object_index = 0

    previous_possible_relations_list_length = len(RelationChangeDomain.possible_object_to_object_relations_dict[bron_asset_id][target_asset_id])
    relation_object = RelationChangeDomain.possible_object_to_object_relations_dict[bron_asset_id][target_asset_id][relation_object_index]

    RelationChangeDomain.add_possible_relation_to_existing_relations(bron_asset_id, target_asset_id, relation_object_index)

    # is the correct relation object in the existing_relations list?
    assert len(RelationChangeDomain.existing_relations) == 1
    assert RelationChangeDomain.existing_relations[0].bronAssetId.identificator == bron_asset_id
    assert RelationChangeDomain.existing_relations[0].doelAssetId.identificator == target_asset_id
    assert RelationChangeDomain.existing_relations[0] == relation_object

    # is the correct relation removed from the possible relation list?
    assert previous_possible_relations_list_length == len(RelationChangeDomain.possible_object_to_object_relations_dict[bron_asset_id][target_asset_id]) + 1
    assert relation_object not in RelationChangeDomain.possible_object_to_object_relations_dict[bron_asset_id][target_asset_id]


@pytest.mark.asyncio
async def test_full_set_possible_relations_unique_situations(root_directory: Path,
                                                       setup_simpel_vergelijking_template4,
                                     mock_screen: InsertDataScreen,
                                     mock_fill_possible_relations_list: RelationChangeScreen,
                                     setup_test_project,
                                     mock_step3_visuals):
    test_object_lists_file_path: list[str] = setup_simpel_vergelijking_template4

    InsertDataDomain.add_files_to_backend_list(test_object_lists_file_path)

    error_set, objects_list = await InsertDataDomain.load_and_validate_documents()


    for object in objects_list:
        if not is_relation(object):
            if(object.assetId.identificator == "dummy_e"):
               fund1 = object
            elif(object.assetId.identificator == "dummy_yq"):
                fund2 = object
            elif (object.assetId.identificator == "dummy_AieZ"):
                fund3 = object
    await RelationChangeDomain.set_possible_relations(fund1)

    fund1_id =fund1.assetId.identificator
    fund2_id = fund2.assetId.identificator
    fund3_id = fund3.assetId.identificator
    assert len(RelationChangeDomain.possible_object_to_object_relations_dict[fund1_id][fund2_id]) == 3
    assert len(
        RelationChangeDomain.possible_object_to_object_relations_dict[fund1_id][fund3_id]) == 3


@pytest.mark.asyncio
async def test_full_add_possible_relation_to_existing_relation(root_directory: Path,
                                                         setup_simpel_vergelijking_template2,
                                                         mock_screen: InsertDataScreen,
                                                         mock_fill_possible_relations_list: RelationChangeScreen,
                                                         setup_test_project,
                                                         mock_step3_visuals,mock_save_validated_assets_function,
                                 mock_load_validated_assets):
    test_object_lists_file_path: list[str] = setup_simpel_vergelijking_template2

    InsertDataDomain.add_files_to_backend_list(test_object_lists_file_path)

    error_set, objects_list = await InsertDataDomain.load_and_validate_documents()

    for object in objects_list:
        await RelationChangeDomain.set_possible_relations(object)

    bron_asset_id = list(RelationChangeDomain.possible_object_to_object_relations_dict.keys())[0]
    target_asset_id = \
    list(RelationChangeDomain.possible_object_to_object_relations_dict[bron_asset_id].keys())[0]
    relation_object_index = 0

    previous_possible_relations_list_length = len(
        RelationChangeDomain.possible_object_to_object_relations_dict[bron_asset_id][
            target_asset_id])
    relation_object = \
    RelationChangeDomain.possible_object_to_object_relations_dict[bron_asset_id][target_asset_id][
        relation_object_index]

    RelationChangeDomain.add_possible_relation_to_existing_relations(bron_asset_id,
                                                                     target_asset_id,
                                                                     relation_object_index)

    # is the correct relation object in the existing_relations list?
    assert len(RelationChangeDomain.existing_relations) == 1
    assert RelationChangeDomain.existing_relations[0].bronAssetId.identificator == bron_asset_id
    assert RelationChangeDomain.existing_relations[0].doelAssetId.identificator == target_asset_id
    assert RelationChangeDomain.existing_relations[0] == relation_object

    # is the correct relation removed from the possible relation list?
    assert previous_possible_relations_list_length == len(
        RelationChangeDomain.possible_object_to_object_relations_dict[bron_asset_id][
            target_asset_id]) + 1
    assert relation_object not in \
           RelationChangeDomain.possible_object_to_object_relations_dict[bron_asset_id][
               target_asset_id]


@pytest.mark.asyncio
async def test_full_add_possible_relation_to_existing_relation(root_directory:Path,
                                                         setup_simpel_vergelijking_template5,
                                mock_screen: InsertDataScreen,
                                mock_fill_possible_relations_list: RelationChangeScreen,
                                setup_test_project,
                                mock_step3_visuals,
                                mock_save_validated_assets_function,
                                mock_load_validated_assets
                                                         ):
    test_object_lists_file_path: list[str] = setup_simpel_vergelijking_template5

    InsertDataDomain.add_files_to_backend_list(test_object_lists_file_path)

    error_set, objects_list = await InsertDataDomain.load_and_validate_documents()

    for object in objects_list:
        if not is_relation(object):
            await RelationChangeDomain.set_possible_relations(object)

    bron_asset_id = list(RelationChangeDomain.possible_object_to_object_relations_dict.keys())[0]
    target_asset_id = list(RelationChangeDomain.possible_object_to_object_relations_dict[bron_asset_id].keys())[0]
    relation_object_index = 0

    previous_possible_relations_list_length = len(RelationChangeDomain.possible_object_to_object_relations_dict[bron_asset_id][target_asset_id])
    relation_object = RelationChangeDomain.possible_object_to_object_relations_dict[bron_asset_id][target_asset_id][relation_object_index]

    RelationChangeDomain.add_possible_relation_to_existing_relations(bron_asset_id, target_asset_id, relation_object_index)

    # is the correct relation object in the existing_relations list?
    assert len(RelationChangeDomain.existing_relations) == 3
    assert RelationChangeDomain.existing_relations[2].bronAssetId.identificator == bron_asset_id
    assert RelationChangeDomain.existing_relations[2].doelAssetId.identificator == target_asset_id
    assert RelationChangeDomain.existing_relations[2] == relation_object

    # is the correct relation removed from the possible relation list?
    assert previous_possible_relations_list_length == len(RelationChangeDomain.possible_object_to_object_relations_dict[bron_asset_id][target_asset_id]) + 1
    assert relation_object not in RelationChangeDomain.possible_object_to_object_relations_dict[bron_asset_id][target_asset_id]


@pytest.mark.asyncio
async def test_full_remove_existing_relation(root_directory:Path,
                                       setup_simpel_vergelijking_template5,
                                mock_screen: InsertDataScreen,
                                mock_fill_possible_relations_list: RelationChangeScreen,
                                setup_test_project,
                                mock_step3_visuals,mock_save_validated_assets_function,
                                 mock_load_validated_assets):
    test_object_lists_file_path: list[str] = setup_simpel_vergelijking_template5

    InsertDataDomain.add_files_to_backend_list(test_object_lists_file_path)

    error_set, objects_list = await InsertDataDomain.load_and_validate_documents()


    for object in RelationChangeDomain.shown_objects:
            await RelationChangeDomain.set_possible_relations(object)

    to_remove_index = 0

    to_remove_relation = RelationChangeDomain.existing_relations[to_remove_index]

    bron_asset_id =  to_remove_relation.bronAssetId.identificator
    target_asset_id =  to_remove_relation.doelAssetId.identificator

    if(target_asset_id == 'dummy_TyBGmXfXC' and bron_asset_id == 'dummy_a'):
        print("found")
    previous_possible_relations_list_length = (len(RelationChangeDomain.possible_object_to_object_relations_dict[bron_asset_id][target_asset_id]) if target_asset_id in RelationChangeDomain.possible_object_to_object_relations_dict[bron_asset_id] else 0)
    previous_possible_relations_list_length2 = len(RelationChangeDomain.possible_object_to_object_relations_dict[target_asset_id][bron_asset_id])  if bron_asset_id in RelationChangeDomain.possible_object_to_object_relations_dict[target_asset_id] else 0

    # RelationChangeDomain.add_possible_relation_to_existing_relations(bron_asset_id, target_asset_id, relation_object_index)
    removed_relation = RelationChangeDomain.remove_existing_relation(index=0)

    # is the correct relation object in the existing_relations list?
    assert len(RelationChangeDomain.existing_relations) == 1
    assert removed_relation not in RelationChangeDomain.existing_relations

    # force update of the backend possible relations lists
    await RelationChangeDomain.set_possible_relations(
        selected_object=RelationChangeDomain.get_object(identificator=bron_asset_id))
    await RelationChangeDomain.set_possible_relations(
        selected_object=RelationChangeDomain.get_object(identificator=target_asset_id))

    l1 = RelationChangeDomain.possible_object_to_object_relations_dict[bron_asset_id][target_asset_id]
    l2 = RelationChangeDomain.possible_object_to_object_relations_dict[target_asset_id][bron_asset_id]

    # is the correct relation removed from the possible relation list?
    assert previous_possible_relations_list_length == len(l1)-1
    assert previous_possible_relations_list_length2 == len(l2) - 1
    #TODO: make it so removed relations are added to possible relations with all previous data
    # assert l1[len(l1)-1] == removed_relation
    # assert l2[len(l2)-1] == removed_relation

    # removed_relation.typeURI = 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Bevestiging'
    assert l1[len(l1)-1].bronAssetId.identificator == removed_relation.bronAssetId.identificator
    assert l1[len(l1) - 1].doelAssetId.identificator == removed_relation.doelAssetId.identificator
    assert l1[len(l1) - 1].typeURI == removed_relation.typeURI

    assert l2[len(l2) - 1].bronAssetId.identificator == removed_relation.doelAssetId.identificator
    assert l2[len(l2) - 1].doelAssetId.identificator == removed_relation.bronAssetId.identificator
    assert l2[len(l2) - 1].typeURI == removed_relation.typeURI

#################################################
# UNIT TESTS                                    #
#################################################
#################################################
# RelationChangeDomain.init_static            #
#################################################

@pytest.fixture
def mock_project() -> Project:
    return Project("test")

@pytest.fixture
def mock_oslo_collector() -> Function:
    with patch('otlmow_modelbuilder.OSLOCollector.OSLOCollector.__init__') as mock__init__OSLOColletor:
        mock__init__OSLOColletor.return_value = None
        yield mock__init__OSLOColletor

@pytest.fixture(scope="function")
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
def test_init_static(mock_project: Project,mock_collect_all: Mock, mock_oslo_collector: Function, subset_path: str, expected_exception: Optional[Exception],mock_save_validated_assets_function,
                                 mock_load_validated_assets):
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

@pytest.mark.asyncio
async def test_set_objects_empty_list(mock_project: Project,
                                mock_collect_all: Mock,
                                mock_oslo_collector: Function,
                                mock_screen: InsertDataScreen,
                                mock_rel_screen: RelationChangeScreen,
                                mock_save_validated_assets_function,
                                 mock_load_validated_assets):
    local_mock = RelationChangeDomain.set_instances
    RelationChangeDomain.set_instances = Mock()
    RelationChangeDomain.init_static(mock_project)
    RelationChangeDomain.set_instances = local_mock

    await RelationChangeDomain.set_instances([])

    assert len(RelationChangeDomain.shown_objects) == 0

@pytest.mark.asyncio
async def test_set_objects_single_item_list(mock_screen: RelationChangeScreen,mock_collect_all,
                                      mock_rel_screen,mock_save_validated_assets_function,
                                      mock_load_validated_assets,mock_step3_visuals):
    RelationChangeDomain.init_static(Project(eigen_referentie="test"))
    test_object = AllCasesTestClass()
    test_object.assetId.identificator = "dummy_identificator"
    await RelationChangeDomain.set_instances([test_object])

    assert len(RelationChangeDomain.shown_objects) == 1
    assert RelationChangeDomain.shown_objects[0].assetId.identificator == "dummy_identificator"

@pytest.mark.asyncio
async def test_set_objects_double_item_list(mock_screen,mock_collect_all,mock_rel_screen,mock_save_validated_assets_function,
                                 mock_load_validated_assets,mock_step3_visuals):
    """
    used RelationChangeDomain.init_static(..., asynchronous=False) to avoid race condition
    if this was not used, the async call of init_static would add another copy of the first object in this list
    """
    test_project = Project(eigen_referentie="test")
    global_vars.current_project = test_project
    RelationChangeDomain.init_static(test_project, asynchronous=False)
    test_object = AllCasesTestClass()
    test_object.assetId.identificator = "dummy_identificator"

    test_object2 = AllCasesTestClass()
    test_object2.assetId.identificator = "dummy_identificator2"

    await RelationChangeDomain.set_instances([test_object, test_object2])
    assert len(RelationChangeDomain.shown_objects) == 2

    assert RelationChangeDomain.shown_objects[0].assetId.identificator == "dummy_identificator"
    assert RelationChangeDomain.shown_objects[1].assetId.identificator == "dummy_identificator2"

    global_vars.current_project = None

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

    test_object = AllCasesTestClass()
    test_object.assetId.identificator = "dummy_identificator"
    RelationChangeDomain.set_possible_relations(test_object)

    assert len(RelationChangeDomain.possible_relations_per_class_dict.keys()) == 1
    assert list(RelationChangeDomain.possible_relations_per_class_dict.keys())[0] == test_object.typeURI
    assert RelationChangeDomain.possible_relations_per_class_dict[test_object.typeURI]

@pytest.mark.skip
def test_set_possible_relations_double_item_list(mock_fill_possible_relations_list: RelationChangeScreen
                                                 ,mock_collector:Mock,mock_save_validated_assets_function,
                                 mock_load_validated_assets):

    test_object = AllCasesTestClass()
    test_object.assetId.identificator = "dummy_identificator"

    test_object2 = AnotherTestClass()
    test_object2.assetId.identificator = "dummy_identificator2"

    RelationChangeDomain.set_possible_relations(test_object)
    RelationChangeDomain.set_possible_relations(test_object2)

    assert len(RelationChangeDomain.possible_relations_per_class_dict.keys()) == 2

    assert list(RelationChangeDomain.possible_relations_per_class_dict.keys())[0] == test_object.typeURI
    assert list(RelationChangeDomain.possible_relations_per_class_dict.keys())[1] == test_object2.typeURI

    assert RelationChangeDomain.possible_relations_per_class_dict[test_object.typeURI]
    assert RelationChangeDomain.possible_relations_per_class_dict[test_object2.typeURI]
