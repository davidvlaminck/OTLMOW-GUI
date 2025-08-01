import asyncio
from unittest.mock import AsyncMock

import pytest
from openpyxl.descriptors.excel import Relation
from otlmow_model.OtlmowModel.Classes.Onderdeel.LigtOp import LigtOp
from otlmow_modelbuilder.OSLOCollector import OSLOCollector
from otlmow_modelbuilder.SQLDataClasses.OSLORelatie import OSLORelatie
from pytestqt.plugin import qtbot
from pytestqt.qtbot import QtBot

from GUI.screens.DynamicDataVisualisationScreen import DynamicDataVisualisationScreen
from GUI.screens.InsertDataScreen import InsertDataScreen
from GUI.screens.RelationChangeScreen import RelationChangeScreen
from GUI.screens.RelationChange_elements.AbstractInstanceListWidget import \
    AbstractInstanceListWidget
from UnitTests.TestClasses.Classes.Installatie.AllCasesTestClassInstallatie import \
    AllCasesTestClassInstallatie
from UnitTests.TestClasses.Classes.Onderdeel.AllCasesTestClass import AllCasesTestClass
from UnitTests.TestClasses.Classes.Onderdeel.AnotherTestClass import AnotherTestClass
from UnitTests.TestClasses.Classes.Onderdeel.Bevestiging import Bevestiging
from UnitTests.general_fixtures.DomainFixtures import *
from UnitTests.general_fixtures.GUIFixtures import *


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
    step3_visuals = Mock(step3_visuals=DynamicDataVisualisationScreen)
    main_window = Mock(step3_visuals=step3_visuals)
    global_vars.otl_wizard = Mock(main_window=main_window)


@fixture
def mock_load_validated_assets() -> None:
    original_load_validated_assets = Project.load_validated_assets_async
    Project.load_validated_assets_async = AsyncMock()
    yield
    Project.load_validated_assets_async = original_load_validated_assets


@pytest.mark.asyncio
async def test_fill_class_list(root_directory: Path,
                               setup_simpel_vergelijking_template5,
                               mock_screen: InsertDataScreen,
                               mock_rel_screen: RelationChangeScreen,
                               setup_test_project,
                               mock_step3_visuals):
    test_object_lists_file_path: list[str] = setup_simpel_vergelijking_template5

    InsertDataDomain.add_files_to_backend_list(test_object_lists_file_path)

    await InsertDataDomain.load_and_validate_documents()

    object_list = RelationChangeDomain.get_screen().objects_list_gui

    reference_items = ['BetonnenHeipaal (1)', 'Bewegingssensor (1)', 'Funderingsmassief (2)', 'Pictogram (2)',
                       'Verkeersbordopstelling (2)', 'Verkeersbordsteun (2)']
    real_items = [object_list.list_gui.model.item(x).text() for x in range(object_list.list_gui.model.rowCount())]

    assert reference_items == real_items

    child_items = {}
    child_items['BetonnenHeipaal'] = ['dummy_bcjseEAj (extern)']
    child_items['Bewegingssensor'] = ['dummy_Q (extern)']
    child_items['Funderingsmassief'] = ['dummy_FNrHuPZCWV', 'dummy_TyBGmXfXC']
    child_items['Pictogram'] = ['dummy_a', 'dummy_long_identificator_pictogram']
    child_items['Verkeersbordopstelling'] = ['dummy_LGG', 'dummy_hxOTHWe']
    child_items['Verkeersbordsteun'] = ['dummy_J', 'dummy_s']

    for i in range(len(real_items)):
        real_item = object_list.list_gui.model.item(i)
        item_text = real_item.data(object_list.data_1_index)

        real_children = [real_item.child(x).text() for x in
                         range(real_item.rowCount())]
        # print(real_children)
        assert real_children == child_items[item_text]


#######################################################
# RelationChangeScreen.fill_possible_relations_list   #
#######################################################
@pytest.mark.asyncio
async def test_full_fill_possible_relations_list(qtbot, root_directory: Path,
                                                 setup_simpel_vergelijking_template5,
                                                 mock_screen: InsertDataScreen,
                                                 mock_rel_screen: RelationChangeScreen,
                                                 setup_test_project,
                                                 mock_step3_visuals):
    test_object_lists_file_path: list[str] = setup_simpel_vergelijking_template5

    InsertDataDomain.add_files_to_backend_list(test_object_lists_file_path)

    error_set, objects_lists = await InsertDataDomain.load_and_validate_documents()

    # VerkeersOpstelling1
    vopstel1 = objects_lists[0]

    await RelationChangeDomain.set_possible_relations(selected_object=vopstel1)
    possible_relations_list = RelationChangeDomain.get_screen().possible_relation_list_gui

    child_items = {}
    child_items_col_2 = {}
    child_items['HoortBij'] = ['dummy_J', 'dummy_a', 'dummy_long_identificator_pictogram', 'dummy_s']
    child_items_col_2['HoortBij'] = ['Verkeersbordsteun', 'Pictogram', 'Pictogram', 'Verkeersbordsteun']
    item_count = len(child_items['HoortBij'])

    reference_items = [f'HoortBij ({item_count})']
    real_items = [possible_relations_list.list_gui.model.item(x).text() for x in
                  range(possible_relations_list.list_gui.model.rowCount())]
    assert reference_items == real_items

    for i in range(len(real_items)):
        real_item = possible_relations_list.list_gui.model.item(i)
        item_type_data = real_item.data(possible_relations_list.data_1_index)
        real_children = [real_item.child(x).text() for x in
                         range(real_item.rowCount())]
        real_children_col_2 = [real_item.child(x, 1).text() for x in range(real_item.rowCount())]
        assert real_children == child_items[item_type_data]
        assert real_children_col_2 == child_items_col_2[item_type_data]

    # pictogram 1
    pict1 = objects_lists[4]
    await RelationChangeDomain.set_possible_relations(selected_object=pict1)

    child_items = {}
    # child_items['HoortBij'] = ['dummy_C', 'dummy_J', 'dummy_a', 'dummy_s']
    # child_items_col_2['HoortBij'] = ['Pictogram', 'Verkeersbordsteun', 'Pictogram',
    #                                  'Verkeersbordsteun']

    child_items['Bevestiging'] = ['dummy_FNrHuPZCWV', 'dummy_J', 'dummy_TyBGmXfXC', 'dummy_bcjseEAj (extern)',
                                  'dummy_s']
    child_items_col_2['Bevestiging'] = ['Funderingsmassief', 'Verkeersbordsteun', 'Funderingsmassief',
                                        'BetonnenHeipaal', 'Verkeersbordsteun']
    child_items['HoortBij'] = ['dummy_LGG', 'dummy_hxOTHWe']
    child_items_col_2['HoortBij'] = ['Verkeersbordopstelling', 'Verkeersbordopstelling']

    bevestiging_type_size = len(child_items['Bevestiging'])
    hoortbij_type_size = len(child_items['HoortBij'])

    reference_items = [f'Bevestiging ({bevestiging_type_size})', f'HoortBij ({hoortbij_type_size})']
    real_items = [possible_relations_list.list_gui.model.item(x).text() for x in
                  range(possible_relations_list.list_gui.model.rowCount())]
    assert reference_items == real_items

    for i in range(len(real_items)):
        real_item = possible_relations_list.list_gui.model.item(i)
        item_type_data = real_item.data(possible_relations_list.data_1_index)
        real_children = [real_item.child(x).text() for x in
                         range(real_item.rowCount())]
        assert real_children == child_items[item_type_data]

        real_children_col_2 = [real_item.child(x, 1).text() for x in
                               range(real_item.rowCount())]
        assert real_children_col_2 == child_items_col_2[item_type_data]

    # funderingsMassief 1
    fund1 = objects_lists[2]
    await RelationChangeDomain.set_possible_relations(selected_object=fund1)

    child_items = {}
    child_items['Bevestiging'] = ['dummy_FNrHuPZCWV', 'dummy_J', 'dummy_Q (extern)', 'dummy_a',
                                  'dummy_bcjseEAj (extern)', 'dummy_long_identificator_pictogram',
                                  'dummy_s']
    child_items_col_2['Bevestiging'] = ['Funderingsmassief', 'Verkeersbordsteun', 'Bewegingssensor',
                                        'Pictogram', 'BetonnenHeipaal', 'Pictogram',
                                        'Verkeersbordsteun']
    child_items['LigtOp'] = ['dummy_FNrHuPZCWV', 'dummy_FNrHuPZCWV', 'dummy_bcjseEAj (extern)',
                             'dummy_bcjseEAj (extern)']
    child_items_col_2['LigtOp'] = ['Funderingsmassief', 'Funderingsmassief', 'BetonnenHeipaal', 'BetonnenHeipaal']

    bevestiging_type_size = len(child_items['Bevestiging'])
    ligtop_type_size = len(child_items['LigtOp'])

    reference_items = [f'Bevestiging ({bevestiging_type_size})', f'LigtOp ({ligtop_type_size})']
    real_items = [possible_relations_list.list_gui.model.item(x).text() for x in
                  range(possible_relations_list.list_gui.model.rowCount())]
    fund1_possible_relations_gui = ['Bevestiging', 'LigtOp']
    assert real_items == reference_items

    for i in range(len(real_items)):
        real_item = possible_relations_list.list_gui.model.item(i)
        item_type_data = real_item.data(possible_relations_list.data_1_index)
        real_children = [real_item.child(x).text() for x in
                         range(real_item.rowCount())]
        assert real_children == child_items[item_type_data]
        real_children_col_2 = [real_item.child(x, 1).text() for x in
                               range(real_item.rowCount())]
        assert real_children_col_2 == child_items_col_2[item_type_data]

    #check the data that is stored in the list elements
    data_index = possible_relations_list.item_type_data_index
    data_type = [
        possible_relations_list.list_gui.model.item(x).data(data_index)
        for x in range(possible_relations_list.list_gui.model.rowCount())]
    fund1_possible_relations_gui_data_type = ["type", "type"]
    assert data_type == fund1_possible_relations_gui_data_type

    child_items = {}
    child_items['Bevestiging'] = ['instance', 'instance', 'instance', 'instance', 'instance',
                                  'instance', 'instance']
    child_items['LigtOp'] = ['instance', 'instance', 'instance', 'instance']
    for i in range(len(fund1_possible_relations_gui_data_type)):
        real_item = possible_relations_list.list_gui.model.item(i)
        item_type_data = real_item.data(possible_relations_list.data_1_index)

        real_children = [real_item.child(x).data(data_index) for x in
                         range(real_item.rowCount())]
        assert real_children == child_items[item_type_data]

    data_index = possible_relations_list.data_1_index
    data1 = [possible_relations_list.list_gui.model.item(x).data(data_index) for x in
             range(possible_relations_list.list_gui.model.rowCount())]
    fund1_possible_relations_gui_data1 = fund1_possible_relations_gui
    assert data1 == fund1_possible_relations_gui_data1

    child_items = {}
    child_items['Bevestiging'] = [['dummy_TyBGmXfXC', 'dummy_FNrHuPZCWV', 0],
                                  ['dummy_TyBGmXfXC', 'dummy_vbeo', 0],
                                  ['dummy_TyBGmXfXC', 'dummy_Q', 0],
                                  ['dummy_TyBGmXfXC', 'dummy_a', 0],
                                  ['dummy_TyBGmXfXC', 'dummy_bcjseEAj', 0],
                                  ['dummy_TyBGmXfXC', 'dummy_long_identificator_pictogram', 0],
                                  ['dummy_TyBGmXfXC', 'dummy_TjwXqP', 0]]
    child_items['LigtOp'] = [
        ['dummy_TyBGmXfXC', 'dummy_FNrHuPZCWV', 1],
        ['dummy_TyBGmXfXC', 'dummy_FNrHuPZCWV', 2],
        ['dummy_TyBGmXfXC', 'dummy_bcjseEAj', 1],
        ['dummy_TyBGmXfXC', 'dummy_bcjseEAj', 2]]
    for i in range(len(fund1_possible_relations_gui_data1)):
        real_item = possible_relations_list.list_gui.model.item(i)
        item_type_data = real_item.data(possible_relations_list.data_1_index)

        real_children = [real_item.child(x).data(data_index) for x in
                         range(real_item.rowCount())]
        assert real_children == child_items[item_type_data]


#######################################################
# RelationChangeScreen.fill_possible_relations_list   #
#######################################################
@pytest.mark.asyncio
async def test_full_fill_existing_relations_list(qtbot, root_directory: Path,
                                                 setup_simpel_vergelijking_template5,
                                                 mock_screen: InsertDataScreen,
                                                 mock_rel_screen: RelationChangeScreen,
                                                 setup_test_project,
                                                 mock_step3_visuals):
    test_object_lists_file_path: list[str] = setup_simpel_vergelijking_template5

    InsertDataDomain.add_files_to_backend_list(test_object_lists_file_path)

    await InsertDataDomain.load_and_validate_documents()

    # existing_relations_gui =    [ 'Bevestiging | dummy_a <-> dummy_TyBGmXfXC',
    #                               'Bevestiging | None <-> None',
    #                               'HoortBij | dummy_J --> dummy_LGG',
    #                               'LigtOp | dummy_FNrHuPZCWV --> dummy_TyBGmXfXC']
    #
    # real_existing_relations_gui =[RelationChangeDomain.get_screen().existing_relation_list_gui.list_gui.item(x).text() for x in range(RelationChangeDomain.get_screen().existing_relation_list_gui.list_gui.count())]
    #
    # assert real_existing_relations_gui == existing_relations_gui
    #
    # fund1_possible_relations_gui_data3 = [0, 1, 2, 3]
    #
    # data3 = [RelationChangeDomain.get_screen().existing_relation_list_gui.list_gui.item(x).data(3) for x in
    #          range(RelationChangeDomain.get_screen().existing_relation_list_gui.list_gui.count())]
    #
    # assert data3 == fund1_possible_relations_gui_data3

    existing_relation_list = RelationChangeDomain.get_screen().existing_relation_list_gui

    reference_items = ['Bevestiging (1)', 'HoortBij (1)']
    real_items = [existing_relation_list.list_gui.model.item(x).text() for x in
                  range(existing_relation_list.list_gui.model.rowCount())]
    assert real_items == reference_items

    child_items = {}
    child_items_col_2 = {}
    child_items['Bevestiging'] = ['dummy_Q (extern)']
    child_items_col_2['Bevestiging'] = ['dummy_bcjseEAj (extern)']
    child_items['HoortBij'] = ['dummy_J']
    child_items_col_2['HoortBij'] = ['dummy_LGG']
    # child_items['LigtOp'] = ['dummy_FNrHuPZCWV']
    # child_items_col_2['LigtOp'] = ['dummy_TyBGmXfXC']
    for i in range(len(real_items)):
        real_item = existing_relation_list.list_gui.model.item(i)
        item_folder_type = real_item.data(existing_relation_list.data_1_index)
        real_children = [real_item.child(x).text() for x in range(real_item.rowCount())]
        real_children_col_2 = [real_item.child(x, 1).text() for x in range(real_item.rowCount())]
        assert real_children == child_items[item_folder_type]
        assert real_children_col_2 == child_items_col_2[item_folder_type]


#################################################
# UNIT TESTS                                    #
#################################################

"""
Just adding the qtbot to the fixtures makes the test complete without a timeout when you call a PyQt element
"""


@fixture
def mock_collect_all() -> Mock:
    original_collect_all = OSLOCollector.collect_all

    mock_collect_all = Mock()
    OSLOCollector.collect_all = mock_collect_all
    yield mock_collect_all
    # after the test the original collect_all is restored for other tests to use
    OSLOCollector.collect_all = original_collect_all


@fixture
def mock_find_all_concrete_rel_all() -> Mock:
    original_find_all_concrete_relations = OSLOCollector.find_all_concrete_relations

    mock_find_all_concrete_relations = Mock(return_value=[])
    OSLOCollector.find_all_concrete_relations = mock_find_all_concrete_relations
    yield mock_find_all_concrete_relations
    # after the test the original find_all_concrete_relations is restored for other tests to use
    OSLOCollector.find_all_concrete_relations = original_find_all_concrete_relations


@fixture
def mock_project(mock_collect_all) -> Project:
    return Project(eigen_referentie="test")


@pytest.mark.asyncio
async def test_fill_class_list_empty_list(qtbot,
                                    create_translations,
                                    mock_rel_screen: RelationChangeScreen,
                                    mock_step3_visuals,
                                    mock_project,
                                    mock_load_validated_assets):
    relation_change_screen = mock_rel_screen

    test_objects_list = []

    local_mock = RelationChangeDomain.set_instances
    RelationChangeDomain.set_instances = AsyncMock()
    RelationChangeDomain.init_static(mock_project)
    RelationChangeDomain.set_instances = local_mock

    await RelationChangeDomain.set_instances(test_objects_list)
    # relation_change_screen.fill_object_list(objects=test_objects_list)

    assert relation_change_screen.objects_list_gui.list_gui.model.rowCount() == 1


"""
Just adding the qtbot to the fixtures makes the test complete without a timeout when you call a PyQt element
"""


@pytest.mark.asyncio
async def test_fill_class_list_single_item_list(qtbot,
                                          create_translations,
                                          mock_rel_screen,
                                          mock_project,
                                          mock_load_validated_assets):
    test_object = AllCasesTestClass()
    test_object.assetId.identificator = "dummy_identificator"

    relation_change_screen = mock_rel_screen

    test_objects_list = [test_object]

    local_mock = RelationChangeDomain.set_instances
    RelationChangeDomain.set_instances = AsyncMock()
    RelationChangeDomain.init_static(mock_project)
    RelationChangeDomain.set_instances = local_mock

    await RelationChangeDomain.set_instances(test_objects_list)
    # relation_change_screen.fill_object_list(objects=test_objects_list)

    assert relation_change_screen.objects_list_gui.list_gui.model.rowCount() == 1
    assert relation_change_screen.objects_list_gui.list_gui.model.item(0).text() == "AllCasesTestClass (1)"

    assert relation_change_screen.objects_list_gui.list_gui.model.item(0).rowCount() == 1
    assert relation_change_screen.objects_list_gui.list_gui.model.item(0).child(0).text() == "dummy_identificator"


"""
Just adding the qtbot to the fixtures makes the test complete without a timeout when you call a PyQt element
"""


@pytest.mark.asyncio
async def test_fill_class_list_double_item_list(qtbot,
                                          create_translations,
                                          mock_rel_screen,
                                          mock_project,
                                          mock_load_validated_assets):
    test_object = AllCasesTestClass()
    test_object.assetId.identificator = "dummy_identificator"

    test_object2 = AllCasesTestClass()
    test_object2.assetId.identificator = "dummy_identificator2"

    relation_change_screen = mock_rel_screen
    test_objects_list = [test_object, test_object2]

    local_mock = RelationChangeDomain.set_instances
    RelationChangeDomain.set_instances = AsyncMock()
    RelationChangeDomain.init_static(mock_project,asynchronous=False)
    RelationChangeDomain.set_instances = local_mock

    await RelationChangeDomain.set_instances(test_objects_list)

    assert relation_change_screen.objects_list_gui.list_gui.model.rowCount() == 1
    assert relation_change_screen.objects_list_gui.list_gui.model.item(0).text() == "AllCasesTestClass (2)"

    assert relation_change_screen.objects_list_gui.list_gui.model.item(0).rowCount() == 2
    assert relation_change_screen.objects_list_gui.list_gui.model.item(0).child(
        0).text() == "dummy_identificator"
    assert relation_change_screen.objects_list_gui.list_gui.model.item(0).child(
        1).text() == "dummy_identificator2"


@pytest.mark.asyncio
async def test_fill_class_list_with_2_same_name_but_diff_namespace_items(qtbot,
                                                                   create_translations,
                                                                   mock_rel_screen,
                                                                   mock_project,
                                                                   mock_load_validated_assets):
    test_object = AllCasesTestClassInstallatie()
    test_object.assetId.identificator = "dummy_identificator"

    test_object2 = AllCasesTestClass()
    test_object2.assetId.identificator = "dummy_identificator2"

    test_object3 = AnotherTestClass()
    test_object3.assetId.identificator = "dummy_identificator3"

    test_objects_list = [test_object, test_object2, test_object3]

    local_mock = RelationChangeDomain.set_instances
    RelationChangeDomain.set_instances = AsyncMock()
    RelationChangeDomain.init_static(mock_project)
    RelationChangeDomain.set_instances = local_mock

    await RelationChangeDomain.set_instances(test_objects_list)
    # mock_rel_screen.fill_object_list(objects=test_objects_list)
    relation_change_screen = mock_rel_screen

    assert relation_change_screen.objects_list_gui.list_gui.model.rowCount() == 3
    assert relation_change_screen.objects_list_gui.list_gui.model.item(
        0).text() == "AnotherTestClass (1)"
    assert relation_change_screen.objects_list_gui.list_gui.model.item(
        1).text() == "installatie#AllCasesTestClass (1)"
    assert relation_change_screen.objects_list_gui.list_gui.model.item(
        2).text() == "onderdeel#AllCasesTestClass (1)"

    assert relation_change_screen.objects_list_gui.list_gui.model.item(0).rowCount() == 1
    assert relation_change_screen.objects_list_gui.list_gui.model.item(0).child(0).text() == "dummy_identificator3"
    assert relation_change_screen.objects_list_gui.list_gui.model.item(1).rowCount() == 1
    assert relation_change_screen.objects_list_gui.list_gui.model.item(1).child(0).text() == "dummy_identificator"
    assert relation_change_screen.objects_list_gui.list_gui.model.item(2).rowCount() == 1
    assert relation_change_screen.objects_list_gui.list_gui.model.item(2).child(0).text() == "dummy_identificator2"


@fixture
def mock_OSLORelatie_test():
    return [
        OSLORelatie("", "", AllCasesTestClass.typeURI, AnotherTestClass.typeURI, Bevestiging.typeURI, "Unspecified", "",
                    ""),
        OSLORelatie("", "", AnotherTestClass.typeURI, AllCasesTestClass.typeURI, Bevestiging.typeURI, "Unspecified", "",
                    ""),
        OSLORelatie("", "", AnotherTestClass.typeURI, AllCasesTestClass.typeURI, LigtOp.typeURI, "Unspecified", "", "")]

@pytest.fixture(scope="session")
def event_loop():

    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.mark.asyncio
async def test_fill_possible_relations_list_with_2_same_name_but_diff_namespace_items(
        qtbot,
        create_translations,
        mock_find_all_concrete_rel_all,
        mock_OSLORelatie_test,
        mock_rel_screen,
        mock_step3_visuals,
        mock_project,
        mock_load_validated_assets, event_loop):
    current_project = global_vars.current_project
    global_vars.current_project = mock_project
    test_object = AllCasesTestClassInstallatie()
    test_object.assetId.identificator = "dummy_identificator"

    test_object2 = AllCasesTestClass()
    test_object2.assetId.identificator = "dummy_identificator2"

    test_object3 = AnotherTestClass()
    test_object3.assetId.identificator = "dummy_identificator3"

    test_objects_list = [test_object, test_object2, test_object3]

    local_mock = RelationChangeDomain.set_instances
    RelationChangeDomain.set_instances = AsyncMock()
    RelationChangeDomain.init_static(mock_project,asynchronous=False)
    global_vars.current_project = mock_project
    RelationChangeDomain.set_instances = local_mock

    await RelationChangeDomain.set_instances(test_objects_list)
    # mock_rel_screen.fill_object_list(objects=test_objects_list)

    RelationChangeDomain.possible_relations_per_class_dict = {test_object2.typeURI: [mock_OSLORelatie_test[0]],
                                                              test_object3.typeURI: [mock_OSLORelatie_test[1]]}
    RelationChangeDomain.regenerate_relation_types = False
    await RelationChangeDomain.set_possible_relations(test_object2)
    relation_change_screen = mock_rel_screen

    assert relation_change_screen.possible_relation_list_gui.list_gui.model.rowCount() == 1
    assert relation_change_screen.possible_relation_list_gui.list_gui.model.item(
        0).text() == 'Bevestiging (1)'

    assert relation_change_screen.possible_relation_list_gui.list_gui.model.item(0).rowCount() == 1
    assert relation_change_screen.possible_relation_list_gui.list_gui.model.item(0).child(
        0).text() == "dummy_identificator3"
    assert relation_change_screen.possible_relation_list_gui.list_gui.model.item(0).child(
        0, 1).text() == "AnotherTestClass"

    await RelationChangeDomain.set_possible_relations(test_object3)

    assert relation_change_screen.possible_relation_list_gui.list_gui.model.rowCount() == 1
    assert relation_change_screen.possible_relation_list_gui.list_gui.model.item(
        0).text() == "Bevestiging (1)"

    assert relation_change_screen.possible_relation_list_gui.list_gui.model.item(0).rowCount() == 1
    assert relation_change_screen.possible_relation_list_gui.list_gui.model.item(0).child(
        0).text() == "dummy_identificator2"
    assert relation_change_screen.possible_relation_list_gui.list_gui.model.item(0).child(0,
                                                                                          1).text() == "onderdeel#AllCasesTestClass"

    global_vars.current_project = current_project