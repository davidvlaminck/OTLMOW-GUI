import pytest
from pytestqt.plugin import qtbot
from pytestqt.qtbot import QtBot

from Domain.enums import FileState
from GUI.screens.InsertDataScreen import InsertDataScreen
from GUI.screens.RelationChangeScreen import RelationChangeScreen

from UnitTests.general_fixtures.GUIFixtures import *
from UnitTests.general_fixtures.DomainFixtures import *

#################################################
# FULL TESTS                                    #
#################################################
#######################################################
# InsertDataDomain.load_and_validate_document         #
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
    original_fill_class_list = RelationChangeScreen.fill_object_list

    RelationChangeScreen.fill_object_list = Mock()

    original_get_screen = RelationChangeDomain.get_screen
    RelationChangeDomain.get_screen = Mock(return_value=relation_change_screen)

    yield relation_change_screen

    RelationChangeScreen.fill_object_list = original_fill_class_list
    RelationChangeDomain.get_screen = original_get_screen

def test_load_and_validate_document_good_path(mock_screen: InsertDataScreen,
                                              setup_simpel_vergelijking_template5,
                                              root_directory: Path,
                                              setup_test_project,
                                              mock_rel_screen: RelationChangeScreen,
                                              mock_step3_visuals) -> None:

    test_object_lists_file_path: list[str] = setup_simpel_vergelijking_template5
    InsertDataDomain.init_static()

    InsertDataDomain.add_files_to_backend_list(test_object_lists_file_path)

    assert(len(global_vars.current_project.saved_project_files) == 1)

    location_dir = global_vars.current_project.get_project_files_dir_path()
    if not location_dir.exists():
        old_path = global_vars.current_project.get_old_project_files_dir_path()
        if old_path.exists():
            location_dir = old_path
        else:
            location_dir.mkdir()

    expected_saved_file_path = location_dir / Path(test_object_lists_file_path[0]).name


    assert(global_vars.current_project.saved_project_files[0].file_path == expected_saved_file_path)
    assert(global_vars.current_project.saved_project_files[0].state == FileState.WARNING)

    error_set, objects_lists = InsertDataDomain.load_and_validate_documents()

    assert(len(error_set) == 0)
    assert(len(objects_lists) == 1)
    assert(len(objects_lists[0]) == 12)
    assert (global_vars.current_project.saved_project_files[0].state == FileState.OK)


@pytest.mark.parametrize("rel_sdf_file_path, expected_output_filepath, object_count", [

    ("UnitTests/test_files/input/DA-2025-00023_export_sdf_example.sdf",
     Path(
         "UnitTests/test_files/output_ref/output_load_and_validate_documents_SDF_DA-2025-00023_export.txt"),
     254),

    ("UnitTests/test_files/input/DA-2024-03992_export_sdf_example.sdf",
     Path("UnitTests/test_files/output_ref/output_load_and_validate_documents_SDF_DA-2024-03992_export.txt"),2028)

], ids=[
    "DA-2025-00023_export_sdf_example",
    "DA-2024-03992_export_sdf_example"
        ])
def test_load_and_validate_document_sdf(mock_screen: InsertDataScreen,
                                        get_and_cleanup_empty_project_no_param,
                                        root_directory: Path,
                                        setup_test_project,
                                        mock_rel_screen: RelationChangeScreen,
                                        mock_step3_visuals,
                                        rel_sdf_file_path:str,
                                        expected_output_filepath, object_count:int):
    #SETUP
    sdf_path_example = root_directory / rel_sdf_file_path
    expected_output_path = root_directory / expected_output_filepath

    InsertDataDomain.init_static()

    InsertDataDomain.add_files_to_backend_list([str(sdf_path_example.absolute())])

    assert(len(global_vars.current_project.saved_project_files) == 1)

    location_dir = global_vars.current_project.get_project_files_dir_path()
    if not location_dir.exists():
        old_path = global_vars.current_project.get_old_project_files_dir_path()
        if old_path.exists():
            location_dir = old_path
        else:
            location_dir.mkdir()

    expected_saved_file_path = location_dir / sdf_path_example.name


    assert(global_vars.current_project.saved_project_files[0].file_path == expected_saved_file_path)
    assert(global_vars.current_project.saved_project_files[0].state == FileState.WARNING)

    #ACT
    error_set, objects_lists = InsertDataDomain.load_and_validate_documents()

    #TEST
    assert(len(error_set) == 0)
    assert(len(objects_lists) == 1)
    assert(len(objects_lists[0]) == object_count)
    assert (global_vars.current_project.saved_project_files[0].state == FileState.OK)

    #get expected output
    if not os.path.exists(expected_output_path):
        raise FileNotFoundError(
            f"Reference file doesn't exist: {expected_output_path}")


    # the print output written by python to the .txt file is encoded in utf-16
    test_output_content = expected_output_path.read_text(encoding='utf-16')

    assert f"{objects_lists}\n" == f"{test_output_content}".replace("mm┬▓","mmÂ²")
