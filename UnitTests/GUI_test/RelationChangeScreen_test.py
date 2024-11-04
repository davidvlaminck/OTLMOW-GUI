from openpyxl.descriptors.excel import Relation
from otlmow_model.OtlmowModel.Classes.Onderdeel.LigtOp import LigtOp
from otlmow_modelbuilder.OSLOCollector import OSLOCollector
from otlmow_modelbuilder.SQLDataClasses.OSLORelatie import OSLORelatie
from pytestqt.plugin import qtbot
from pytestqt.qtbot import QtBot

from GUI.Screens.DataVisualisationScreen import DataVisualisationScreen
from GUI.Screens.InsertDataScreen import InsertDataScreen
from GUI.Screens.RelationChangeScreen import RelationChangeScreen
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

    InsertDataDomain.load_and_validate_documents()

    assert mock_rel_screen.objects_list_gui.list_gui.item(0).text() == "dummy_hxOTHWe | Verkeersbordopstelling"
    assert mock_rel_screen.objects_list_gui.list_gui.item(1).text() == "dummy_LGG | Verkeersbordopstelling"
    assert mock_rel_screen.objects_list_gui.list_gui.item(2).text() == "dummy_TyBGmXfXC | Funderingsmassief"
    assert mock_rel_screen.objects_list_gui.list_gui.item(3).text() == "dummy_FNrHuPZCWV | Funderingsmassief"
    assert mock_rel_screen.objects_list_gui.list_gui.item(4).text() == "dummy_a | Pictogram"
    assert mock_rel_screen.objects_list_gui.list_gui.item(5).text() == "dummy_C | Pictogram"
    assert mock_rel_screen.objects_list_gui.list_gui.item(6).text() == "dummy_J | Verkeersbordsteun"
    assert mock_rel_screen.objects_list_gui.list_gui.item(7).text() == "dummy_s | Verkeersbordsteun"

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
        'HoortBij <-- dummy_C | Pictogram',
        'HoortBij <-- dummy_a | Pictogram',
        'HoortBij <-- dummy_J | Verkeersbordsteun',
        'HoortBij <-- dummy_s | Verkeersbordsteun']

    real_vopstel1_possible_relations_gui =[RelationChangeDomain.get_screen().possible_relation_list_gui.list_gui.item(x).text() for x in
                                           range(RelationChangeDomain.get_screen().possible_relation_list_gui.list_gui.count())]

    assert real_vopstel1_possible_relations_gui == vopstel1_possible_relations_gui

    fund1 = InsertDataDomain.flatten_list(objects_lists)[2]

    RelationChangeDomain.set_possible_relations(selected_object=fund1)
    fund1_possible_relations_gui = [
        'Bevestiging <-> dummy_FNrHuPZCWV | Funderingsmassief',
        'Bevestiging <-> dummy_C | Pictogram',
        'Bevestiging <-> dummy_J | Verkeersbordsteun',
        'Bevestiging <-> dummy_s | Verkeersbordsteun']

    real_fund1_possible_relations_gui = [RelationChangeDomain.get_screen().possible_relation_list_gui.list_gui.item(x).text() for x in
                                         range(RelationChangeDomain.get_screen().possible_relation_list_gui.list_gui.count())]

    assert real_fund1_possible_relations_gui == fund1_possible_relations_gui

    #check the data that is stored in the list elements
    data1 = [RelationChangeDomain.get_screen().possible_relation_list_gui.list_gui.item(x).data(3) for x in
             range(RelationChangeDomain.get_screen().possible_relation_list_gui.list_gui.count())]

    fund1_possible_relations_gui_data1 = [fund1.assetId.identificator for _ in fund1_possible_relations_gui]

    assert data1 == fund1_possible_relations_gui_data1

    data2 = [RelationChangeDomain.get_screen().possible_relation_list_gui.list_gui.item(x).data(4) for x in
             range(RelationChangeDomain.get_screen().possible_relation_list_gui.list_gui.count())]

    fund1_possible_relations_gui_data2 = [
        'dummy_FNrHuPZCWV',
        'dummy_C',
        'dummy_vbeo',
        'dummy_TjwXqP']

    assert data2 == fund1_possible_relations_gui_data2

    fund1_possible_relations_gui_data3 = [0,0,0,0]

    data3 = [RelationChangeDomain.get_screen().possible_relation_list_gui.list_gui.item(x).data(5) for x in
             range(RelationChangeDomain.get_screen().possible_relation_list_gui.list_gui.count())]

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

    InsertDataDomain.load_and_validate_documents()

    existing_relations_gui =    [ 'Bevestiging | dummy_a <-> dummy_TyBGmXfXC',
                                  'Bevestiging | None <-> None',
                                  'HoortBij | dummy_J --> dummy_LGG',
                                  'LigtOp | dummy_FNrHuPZCWV --> dummy_TyBGmXfXC']

    real_existing_relations_gui =[RelationChangeDomain.get_screen().existing_relation_list_gui.list_gui.item(x).text() for x in range(RelationChangeDomain.get_screen().existing_relation_list_gui.list_gui.count())]

    assert real_existing_relations_gui == existing_relations_gui

    fund1_possible_relations_gui_data3 = [0, 1, 2, 3]

    data3 = [RelationChangeDomain.get_screen().existing_relation_list_gui.list_gui.item(x).data(3) for x in
             range(RelationChangeDomain.get_screen().existing_relation_list_gui.list_gui.count())]

    assert data3 == fund1_possible_relations_gui_data3

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
def mock_project(mock_collect_all) -> Project:
    return Project()

def test_fill_class_list_empty_list(qtbot,
                                    create_translations,
                                    mock_rel_screen: RelationChangeScreen,
                                    mock_project):
    relation_change_screen = mock_rel_screen

    test_objects_list = []
    RelationChangeDomain.init_static(mock_project)
    RelationChangeDomain.set_instances(test_objects_list)
    # relation_change_screen.fill_object_list(objects=test_objects_list)

    assert len(relation_change_screen.objects_list_gui.list_gui) == 0

"""
Just adding the qtbot to the fixtures makes the test complete without a timeout when you call a PyQt element
"""
def test_fill_class_list_single_item_list(qtbot,
                                          create_translations,
                                          mock_rel_screen,
                                          mock_project):


    test_object = AllCasesTestClass()
    test_object.assetId.identificator = "dummy_identificator"

    relation_change_screen = mock_rel_screen

    test_objects_list = [test_object]
    RelationChangeDomain.init_static(mock_project)
    RelationChangeDomain.set_instances(test_objects_list)
    # relation_change_screen.fill_object_list(objects=test_objects_list)

    assert len(relation_change_screen.objects_list_gui.list_gui) == 1
    assert relation_change_screen.objects_list_gui.list_gui.item(0).text() == "dummy_identificator | AllCasesTestClass"

"""
Just adding the qtbot to the fixtures makes the test complete without a timeout when you call a PyQt element
"""
def test_fill_class_list_double_item_list(qtbot,
                                          create_translations,
                                          mock_rel_screen,
                                          mock_project):
    test_object = AllCasesTestClass()
    test_object.assetId.identificator = "dummy_identificator"

    test_object2 = AllCasesTestClass()
    test_object2.assetId.identificator = "dummy_identificator2"

    relation_change_screen = mock_rel_screen
    test_objects_list = [test_object, test_object2]
    RelationChangeDomain.init_static(mock_project)
    RelationChangeDomain.set_instances(test_objects_list)
    # relation_change_screen.fill_object_list(objects=test_objects_list)

    assert len(relation_change_screen.objects_list_gui.list_gui) == 2

    assert relation_change_screen.objects_list_gui.list_gui.item(0).text() == "dummy_identificator | AllCasesTestClass"
    assert relation_change_screen.objects_list_gui.list_gui.item(1).text() == "dummy_identificator2 | AllCasesTestClass"

def test_fill_class_list_with_2_same_name_but_diff_namespace_items(qtbot,
                                                                   create_translations,
                                                                   mock_rel_screen,
                                                                   mock_project):
    test_object = AllCasesTestClassInstallatie()
    test_object.assetId.identificator = "dummy_identificator"

    test_object2 = AllCasesTestClass()
    test_object2.assetId.identificator = "dummy_identificator2"

    test_object3 = AnotherTestClass()
    test_object3.assetId.identificator = "dummy_identificator3"


    test_objects_list = [test_object, test_object2, test_object3]
    RelationChangeDomain.init_static(mock_project)
    RelationChangeDomain.set_instances(test_objects_list)
    # mock_rel_screen.fill_object_list(objects=test_objects_list)

    assert len(mock_rel_screen.objects_list_gui.list_gui) == 3

    assert mock_rel_screen.objects_list_gui.list_gui.item(0).text() == "dummy_identificator | installatie#AllCasesTestClass"
    assert mock_rel_screen.objects_list_gui.list_gui.item(1).text() == "dummy_identificator2 | onderdeel#AllCasesTestClass"
    assert mock_rel_screen.objects_list_gui.list_gui.item(2).text() == "dummy_identificator3 | AnotherTestClass"

@fixture
def mock_OSLORelatie_test():
    return [OSLORelatie("","",AllCasesTestClass.typeURI,AnotherTestClass.typeURI,Bevestiging.typeURI,"Unspecified","",""),
            OSLORelatie("","",AnotherTestClass.typeURI,AllCasesTestClass.typeURI,Bevestiging.typeURI,"Unspecified","",""),
            OSLORelatie("","",AnotherTestClass.typeURI,AllCasesTestClass.typeURI,LigtOp.typeURI,"Unspecified","","")]


def test_fill_possible_relations_list_with_2_same_name_but_diff_namespace_items(
        qtbot,
        create_translations,
        mock_OSLORelatie_test,
        mock_rel_screen,
        mock_project):
    test_object = AllCasesTestClassInstallatie()
    test_object.assetId.identificator = "dummy_identificator"

    test_object2 = AllCasesTestClass()
    test_object2.assetId.identificator = "dummy_identificator2"

    test_object3 = AnotherTestClass()
    test_object3.assetId.identificator = "dummy_identificator3"

    test_objects_list = [test_object, test_object2, test_object3]

    RelationChangeDomain.init_static(mock_project)
    RelationChangeDomain.set_instances(test_objects_list)
    # mock_rel_screen.fill_object_list(objects=test_objects_list)

    RelationChangeDomain.possible_relations_per_class_dict={test_object2.typeURI :[mock_OSLORelatie_test[0]],
                                                            test_object3.typeURI :[mock_OSLORelatie_test[1]]}
    RelationChangeDomain.set_possible_relations(test_object2)

    assert len(mock_rel_screen.possible_relation_list_gui.list_gui) == 1

    assert mock_rel_screen.possible_relation_list_gui.list_gui.item(0).text() == "Bevestiging <-> dummy_identificator3 | AnotherTestClass"

    RelationChangeDomain.set_possible_relations(test_object3)

    assert len(mock_rel_screen.possible_relation_list_gui.list_gui) == 1

    assert mock_rel_screen.possible_relation_list_gui.list_gui.item(
        0).text() == "Bevestiging <-> dummy_identificator2 | onderdeel#AllCasesTestClass"
