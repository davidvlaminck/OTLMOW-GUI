import logging
from pathlib import Path

import pytest
from _pytest.fixtures import fixture
from otlmow_converter.FileFormats.ExcelImporter import ExcelImporter
from pytestqt.qtbot import QtBot

from Domain.logger.OTLLogger import OTLLogger
from Domain.step_domain.ExportFilteredDataSubDomain import ExportFilteredDataSubDomain, ReportItem
from Domain.enums import ReportAction, FileState
from Domain.step_domain.InsertDataDomain import InsertDataDomain
from GUI.screens.ExportData_elements.ExportFilteredDataSubScreen import ExportFilteredDataSubScreen
from GUI.screens.InsertDataScreen import InsertDataScreen
from GUI.screens.RelationChangeScreen import RelationChangeScreen
from UnitTests.project_files_test.OTLWizardProjects.Model.OtlmowModel.Classes.Onderdeel.AllCasesTestClass import \
    AllCasesTestClass
from UnitTests.project_files_test.OTLWizardProjects.Model.OtlmowModel.Classes.Onderdeel.AnotherTestClass import \
    AnotherTestClass

model_directory_path = Path(__file__).parent.parent / 'project_files_test' / 'OTLWizardProjects' / 'Model'

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

#TODO: cannot find the output of this test, has to be an async issue but it doesn't happen locally
@pytest.mark.skip
@pytest.mark.parametrize("get_and_cleanup_empty_project",
    # "eigen_referentie, project_path, subset_path, saved_documents_overview_path, bestek,"
    # "laatst_bewerkt, last_quick_save, subset_operator, otl_version,"
    # "expected_project_path, expected_subset_operator, expected_otl_version,"
    # "expected_saved_documents_overview_path, expected_last_quick_save",
    [
        # Happy path with all parameters provided
        ( "empty_project", None, None, None, None, None, None, None, None,
        # expected values
         Path("empty_project"), None,None, None, None),
    ],
    ids=[
        "empty_project",
    ],indirect=True
)
@pytest.mark.asyncio
async def test_export_diff_report(root_directory: Path,
                            get_and_cleanup_empty_project,
                            mock_screen: InsertDataScreen,
                            mock_rel_screen: RelationChangeScreen,
                            mock_step3_visuals,
                            cleanup_after_creating_a_file_to_delete):
    #SETUP
    project,properties,param = get_and_cleanup_empty_project
    global_vars.current_project = project
    edited_file_path = root_directory / "UnitTests"/"test_files"/"input"/"slagbomen_project_edited_agent.xlsx"
    original_file_path = root_directory / "UnitTests"/"test_files"/"input"/"original_slagbomen_DAVIE_export.xlsx"
    output_file_path = root_directory / "UnitTests" / "test_files" / "output_test" / "output_slagbomen_project_edited_agent_diff.xlsx"
    output_ref_file_path = root_directory / "UnitTests" / "test_files" / "output_ref" / "output_slagbomen_project_edited_agent_diff_export.xlsx"
    cleanup_after_creating_a_file_to_delete.append(output_file_path)

    project.save_project_to_dir()
    project.copy_and_add_project_file(edited_file_path,FileState.WARNING)

    InsertDataDomain.init_static()
    await InsertDataDomain.load_and_validate_documents()

    ExportFilteredDataSubDomain.add_original_documents(paths_str=[str(original_file_path.absolute())])

    #ACT
    print("output_file_path: " + str(output_file_path.absolute()))
    ExportFilteredDataSubDomain.sync_export_diff_report(file_name=str(output_file_path.absolute()),synchronous=True)

    #TEST
    assert(output_file_path.exists())


    objects_ref = ExcelImporter.to_objects(output_ref_file_path)
    objects_output = ExcelImporter.to_objects(output_file_path)

    assert objects_ref == objects_output





def test_generate_report():

    instance_1_1 = AllCasesTestClass()
    instance_1_1.assetId.identificator = '1'
    instance_1_1.isActief = True

    instance_2_1 = AllCasesTestClass()
    instance_2_1.assetId.identificator = '1'
    instance_2_1.isActief = True

    instance_1_2 = AllCasesTestClass()
    instance_1_2.assetId.identificator = '2'
    instance_1_2.isActief = True
    instance_1_2.testStringField = 'test'
    instance_1_2.testComplexType.testStringField = 'complexe waarde'

    instance_2_2 = AllCasesTestClass()
    instance_2_2.assetId.identificator = '2'
    instance_2_2.isActief = False
    instance_2_2.testStringField = 'gewijzigd'
    instance_2_2.testComplexType.testStringField = 'gewijzigde complexe waarde'

    instance_1_3 = AllCasesTestClass()
    instance_1_3.assetId.identificator = '3'
    instance_1_3.isActief = True
    # TODO bert navragen of dit de bedoeling is

    instance_2_4 = AnotherTestClass()
    instance_2_4.assetId.identificator = '4'
    instance_2_4.isActief = True

    instance_list_1 = [ instance_1_2, instance_1_3]
    instance_list_2 = [ instance_2_2, instance_2_4]

    report = ExportFilteredDataSubDomain().generate_diff_report(original_data=instance_list_1, new_data=instance_list_2,
                                                                model_directory=model_directory_path)

    assert report == [
        ReportItem(id='2', actie=ReportAction.ATC, attribute='isActief', original_value='True', new_value='False'),
        ReportItem(id='2', actie=ReportAction.ATC, attribute='testComplexType',
                   original_value="testStringField: complexe waarde",
                   new_value="testStringField: gewijzigde complexe waarde"),
        ReportItem(id='2', actie=ReportAction.ATC, attribute='testStringField', original_value='test',
                   new_value='gewijzigd'),
        ReportItem(id='4', actie=ReportAction.ASS, attribute='', original_value='', new_value='')
    ]
