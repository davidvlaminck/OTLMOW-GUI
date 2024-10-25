import os
from pathlib import Path
from unittest.mock import Mock

from _pytest.fixtures import fixture
from openpyxl.reader.excel import load_workbook
from pytestqt.qtbot import QtBot
from pytestqt.plugin import qtbot

from Domain.ExportDataDomain import ExportDataDomain
from Domain.InsertDataDomain import InsertDataDomain
from Domain.RelationChangeDomain import RelationChangeDomain
from GUI.Screens.DataVisualisationScreen import DataVisualisationScreen
from GUI.Screens.InsertDataScreen import InsertDataScreen
from GUI.Screens.RelationChangeScreen import RelationChangeScreen

from UnitTests.general_fixtures.GUIFixtures import *
from UnitTests.general_fixtures.DomainFixtures import *

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


@fixture
def get_export_path_with_cleanup(root_directory: Path) -> Path:
    export_path = (root_directory / "UnitTests" / "project_files_test" / "OTLWizardProjects" / "TestFiles" /
                   "testExport.xlsx")
    yield export_path

    if export_path.exists():
        os.remove(export_path)

def test_unedited_generate_files(root_directory: Path,
                                 mock_screen: InsertDataScreen,
                                mock_fill_possible_relations_list: RelationChangeScreen,
                                setup_test_project,
                                mock_step3_visuals,
                                 get_export_path_with_cleanup:Path):

    test_object_lists_file_path: list[str] = [
        str(root_directory / "demo_projects" / "simpel_vergelijkings_project" /
            "simpel_vergelijking_template2.xlsx")]

    InsertDataDomain.add_files_to_backend_list(test_object_lists_file_path)

    InsertDataDomain.load_and_validate_documents()

    export_path = get_export_path_with_cleanup

    ExportDataDomain.generate_files(export_path,global_vars.current_project,False,False)

    assert export_path.exists()

    wb = load_workbook(export_path)

    expected_wb = load_workbook(Path(test_object_lists_file_path[0]))

    if 'Keuzelijsten' in expected_wb.sheetnames:
        expected_wb.remove(expected_wb['Keuzelijsten'])

    expected_sheet_titles = ['ins#Verkeersbordopstelling',
                             'ond#Funderingsmassief',
                             'ond#Pictogram',
                             'ond#Verkeersbordsteun',
                             'ond#Bevestiging',
                             'ond#HoortBij',
                             'ond#LigtOp']

    assert list(wb.sheetnames)  == expected_sheet_titles

    list_expected_values = [list(sh.iter_rows(0,4,0,26,True)) for sh in  wb.worksheets]
    list_values = [list(sh.iter_rows(0,4,0,26,True))for sh in expected_wb.worksheets]

    assert list_values == list_expected_values


def test_add_remove_generate_files(root_directory: Path,
                                 mock_screen: InsertDataScreen,
                                mock_fill_possible_relations_list: RelationChangeScreen,
                                setup_test_project,
                                mock_step3_visuals,
                                 get_export_path_with_cleanup:Path):

    test_object_lists_file_path: list[str] = [
        str(root_directory / "demo_projects" / "simpel_vergelijkings_project" /
            "simpel_vergelijking_template2.xlsx")]

    InsertDataDomain.add_files_to_backend_list(test_object_lists_file_path)

    InsertDataDomain.load_and_validate_documents()

    RelationChangeDomain.set_possible_relations(RelationChangeDomain.objects[0])

    bron_id = 'dummy_hxOTHWe'
    target_id = 'dummy_C'
    index = 0
    RelationChangeDomain.add_possible_relation_to_existing_relations(bron_id,target_id,index)

    RelationChangeDomain.remove_existing_relation(0)

    export_path = get_export_path_with_cleanup

    ExportDataDomain.generate_files(export_path,global_vars.current_project,False,False)

    assert export_path.exists()

    wb = load_workbook(export_path)

    ref_path_expected_workbook = (root_directory / "UnitTests" / "project_files_test" / "OTLWizardProjects" / "reference_files" / "ref_add_remove_test.xlsx")
    expected_wb = load_workbook(Path(ref_path_expected_workbook))

    if 'Keuzelijsten' in expected_wb.sheetnames:
        expected_wb.remove(expected_wb['Keuzelijsten'])

    expected_sheet_titles = ['ins#Verkeersbordopstelling',
                             'ond#Funderingsmassief',
                             'ond#Pictogram',
                             'ond#Verkeersbordsteun',
                             'ond#Bevestiging',
                             'ond#HoortBij',
                             'ond#LigtOp']

    assert list(wb.sheetnames)  == expected_sheet_titles

    list_expected_values = [list(sh.iter_rows(0,4,0,26,True)) for sh in  wb.worksheets]
    list_values = [list(sh.iter_rows(0,4,0,26,True))for sh in expected_wb.worksheets]

    assert list_values == list_expected_values