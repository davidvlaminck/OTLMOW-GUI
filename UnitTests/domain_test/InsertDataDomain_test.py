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