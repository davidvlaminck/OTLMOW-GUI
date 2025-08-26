from pathlib import Path

import shutil
import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLineEdit, QDialogButtonBox, QApplication, QPushButton

from otlmow_gui.Domain.logger.OTLLogger import OTLLogger
from otlmow_gui.wizard_main import Settings, LANG_DIR
from otlmow_gui.GUI.MainWindow import MainWindow
from otlmow_gui.GUI.translation.GlobalTranslate import GlobalTranslate
from otlmow_gui.GUI.dialog_windows.UpsertProjectWindow import UpsertProjectWindow
from otlmow_gui.GUI.dialog_windows.file_picker_dialog.SubsetLoadFilePickerDialog import SubsetLoadFilePickerDialog

# --- Fixtures ---

@pytest.fixture(autouse=True)
def patch_upsert_project_window_exec():
    """Monkeypatch UpsertProjectWindow.exec to use show() for testability."""
    original_exec = UpsertProjectWindow.exec
    def fake_exec(self):
        self.show()
        return 0
    UpsertProjectWindow.exec = fake_exec
    yield
    UpsertProjectWindow.exec = original_exec

@pytest.fixture
def patch_subset_file_picker(monkeypatch):
    """
    Returns a function that monkeypatches SubsetLoadFilePickerDialog.summon
    to return the given file path.
    """
    def do_patch(subset_path):
        def fake_summon(self, directory=None):
            return [str(subset_path)]
        monkeypatch.setattr(SubsetLoadFilePickerDialog, "summon", fake_summon)
    return do_patch

# --- Helper Functions ---

def wait_for_dialog(qtbot, dialog_cls, timeout=10000):
    """Wait for a dialog of type dialog_cls to appear and return it."""
    def dialog_shown():
        return [w for w in QApplication.instance().allWidgets() if isinstance(w, dialog_cls) and w.isVisible()]
    qtbot.waitUntil(lambda: len(dialog_shown()) > 0, timeout=timeout)
    return dialog_shown()[0]

def fill_upsert_project_dialog(qtbot, dialog, eigen_ref, bestek, subset=None):
    eigen_ref_edit = dialog.findChild(QLineEdit, "eigen_ref_edit")
    assert eigen_ref_edit is not None, "eigen_ref_edit not found"
    eigen_ref_edit.setText(eigen_ref)

    bestek_edit = dialog.findChild(QLineEdit, "bestek_edit")
    assert bestek_edit is not None, "bestek_edit not found"
    bestek_edit.setText(bestek)

    if subset:
        file_picker_btn = dialog.findChild(QPushButton, "file_picker_btn")
        assert file_picker_btn is not None, "file_picker_btn not found"
        qtbot.mouseClick(file_picker_btn, Qt.MouseButton.LeftButton)
        subset_edit = dialog.findChild(QLineEdit, "subset_edit")
        qtbot.waitUntil(lambda: subset_edit.text() == subset, timeout=10000)

def click_ok_and_expect_error(qtbot, dialog, expected_error_substring):
    """Click OK and assert the dialog stays open and shows the expected error."""
    button_box = dialog.findChild(QDialogButtonBox)
    ok_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
    assert ok_button is not None, "OK button not found"
    qtbot.mouseClick(ok_button, Qt.MouseButton.LeftButton)
    # Wait for the error label to update
    qtbot.waitUntil(lambda: expected_error_substring.lower() in dialog.error_label.text().lower(), timeout=10000)
    assert dialog.isVisible(), "Dialog should remain open on validation error"
    assert expected_error_substring.lower() in dialog.error_label.text().lower(), (
        f"Expected error containing '{expected_error_substring}', got: '{dialog.error_label.text()}'"
    )

def click_ok_and_expect_close(qtbot, dialog):
    """Click OK and wait for the dialog to close (for successful validation)."""
    button_box = dialog.findChild(QDialogButtonBox)
    ok_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
    assert ok_button is not None, "OK button not found"
    qtbot.mouseClick(ok_button, Qt.MouseButton.LeftButton)
    qtbot.waitUntil(lambda: not dialog.isVisible(), timeout=10000)

def verify_project_in_table(qtbot, main_window, project_name):
    """Verify the project appears in the table and can be found via search."""
    qtbot.waitUntil(lambda: main_window.home_screen.table.rowCount() > 0, timeout=10000)
    assert main_window.home_screen.table.rowCount() >= 1, "No projects found in the table after creation."
    # Use the search bar to filter for the new project
    main_window.home_screen.search_input_field.setText(project_name)
    qtbot.waitUntil(lambda: main_window.home_screen.table.rowCount() == 1, timeout=10000)
    assert main_window.home_screen.table.item(0, 0).text() == project_name

def verify_project_files(project_dir, project_name, bestek, subset_filename):
    """Verify the project directory, subset file, and project details exist and are correct."""
    assert project_dir.exists(), f"Project directory {project_dir} does not exist."
    subset_file = project_dir / subset_filename
    assert subset_file.exists(), f"Subset file {subset_file} does not exist in project directory."
    details_file = project_dir / 'project_details.json'
    assert details_file.exists(), f"Details file {details_file} does not exist."
    import json
    with open(details_file, 'r', encoding='utf-8') as f:
        details = json.load(f)
    assert details['eigen_referentie'] == project_name
    assert details['bestek'] == bestek
    assert details['subset'] == subset_filename
    assert 'laatst_bewerkt' in details


# --- Main Test ---
@pytest.mark.gui
def test_1_checking_errors_when_creating_projects(qtbot, patch_subset_file_picker):
    # Setup
    project_dir = Path.home() / 'OTLWizardProjects' / 'Projects' / 'FullTestRunProject'
    if project_dir.exists():
        shutil.rmtree(project_dir)

    settings = Settings.get_or_create_settings_file()
    OTLLogger.init()
    language = GlobalTranslate(settings, LANG_DIR).get_all()
    main_window = MainWindow(language)

    import otlmow_gui.Domain.global_vars as global_vars
    global_vars.otl_wizard = type("FakeApp", (), {})()
    global_vars.otl_wizard.main_window = main_window

    qtbot.addWidget(main_window)
    main_window.show()
    assert main_window.isVisible()

    # Paths for test files
    good_subset = Path(__file__).parent.parent / 'test_files' / 'input' / 'voorbeeld-slagboom.db'
    bad_subset = Path(__file__).parent.parent.parent / 'otlmow_gui' / 'demo_projects' / 'slagbomen_project' / 'bad_subset.db'

    # Step 1: Open the new project dialog
    qtbot.mouseClick(main_window.home_screen.header.new_project_button, Qt.MouseButton.LeftButton)
    dialog = wait_for_dialog(qtbot, UpsertProjectWindow)

    # Step 2: Click OK with all fields empty
    click_ok_and_expect_error(qtbot, dialog, "referentie is leeg")

    # Step 3: Fill in Eigen referentie, leave others empty, click OK
    eigen_ref_edit = dialog.findChild(QLineEdit, "eigen_ref_edit")
    eigen_ref_edit.setText("FullTestRunProject")
    click_ok_and_expect_error(qtbot, dialog, "bestek is leeg")

    # Step 4: Fill in Bestek, leave Subset empty, click OK
    bestek_edit = dialog.findChild(QLineEdit, "bestek_edit")
    bestek_edit.setText("TestBestek")
    click_ok_and_expect_error(qtbot, dialog, "subset is leeg")

    # Step 5: Try to set subset to empty string and click OK
    subset_edit = dialog.findChild(QLineEdit, "subset_edit")
    subset_edit.setText("")
    click_ok_and_expect_error(qtbot, dialog, "subset is leeg")

    # Step 6: Select a bad subset file and click OK
    patch_subset_file_picker(bad_subset)
    file_picker_btn = dialog.findChild(QPushButton, "file_picker_btn")
    qtbot.mouseClick(file_picker_btn, Qt.MouseButton.LeftButton)
    qtbot.waitUntil(lambda: subset_edit.text() == str(bad_subset), timeout=10000)
    click_ok_and_expect_error(qtbot, dialog, "kan niet gelezen worden")

    # Step 7: Cancel the dialog
    button_box = dialog.findChild(QDialogButtonBox)
    cancel_button = button_box.button(QDialogButtonBox.StandardButton.Cancel)
    qtbot.mouseClick(cancel_button, Qt.MouseButton.LeftButton)
    qtbot.waitUntil(lambda: not dialog.isVisible(), timeout=10000)

    # Clean up
    main_window.close()
    if project_dir.exists():
        shutil.rmtree(project_dir)

@pytest.mark.gui
def test_2_project_table_sorting(qtbot, patch_subset_file_picker):
    """Test that clicking the project table column headers changes the sort order."""
    import otlmow_gui.Domain.global_vars as global_vars
    from random import shuffle

    # Clean up any old test projects
    base_dir = Path.home() / 'OTLWizardProjects' / 'Projects'
    test_projects = ["SortTestA", "SortTestB", "SortTestC"]
    for name in test_projects:
        pdir = base_dir / name
        if pdir.exists():
            shutil.rmtree(pdir)

    # Setup application and main window
    settings = Settings.get_or_create_settings_file()
    OTLLogger.init()
    language = GlobalTranslate(settings, LANG_DIR).get_all()
    main_window = MainWindow(language)
    global_vars.otl_wizard = type("FakeApp", (), {})()
    global_vars.otl_wizard.main_window = main_window
    qtbot.addWidget(main_window)
    main_window.show()
    assert main_window.isVisible()

    # Use the same subset for all projects
    subset_to_use = Path(__file__).parent.parent / 'test_files' / 'input' / 'voorbeeld-slagboom.db'
    patch_subset_file_picker(subset_to_use)

    # Create projects in random order
    shuffled = test_projects[:]
    shuffle(shuffled)
    for name in shuffled:
        qtbot.mouseClick(main_window.home_screen.header.new_project_button, Qt.MouseButton.LeftButton)
        dialog = wait_for_dialog(qtbot, UpsertProjectWindow)
        fill_upsert_project_dialog(qtbot, dialog, eigen_ref=name, bestek="B", subset=str(subset_to_use))
        click_ok_and_expect_close(qtbot, dialog)

    # Wait for all projects to appear
    qtbot.waitUntil(lambda: main_window.home_screen.table.rowCount() >= len(test_projects), timeout=10000)

    # Helper to get only the test project names in the table, in order
    def get_test_project_names_in_table():
        names = [main_window.home_screen.table.item(row, 0).text() for row in
                 range(main_window.home_screen.table.rowCount())]
        return [name for name in names if name in test_projects]

    # Click the column header to sort (assuming column 0 is the project name)
    header = main_window.home_screen.table.horizontalHeader()
    from PyQt6.QtCore import QPoint
    section_pos = header.sectionPosition(0)
    section_size = header.sectionSize(0)
    center_x = section_pos + section_size // 2
    center_y = header.height() // 2
    qtbot.mouseClick(header.viewport(), Qt.MouseButton.LeftButton, pos=QPoint(center_x, center_y))
    qtbot.wait(500)  # Give time for sorting

    sorted_order = get_test_project_names_in_table()
    assert sorted_order == sorted(test_projects), f"Expected sorted order {sorted(test_projects)}, got {sorted_order}"

    # Click again to reverse sort
    qtbot.mouseClick(header.viewport(), Qt.MouseButton.LeftButton, pos=QPoint(center_x, center_y))
    qtbot.wait(500)
    reverse_sorted_order = get_test_project_names_in_table()
    assert reverse_sorted_order == sorted(test_projects,
                                          reverse=True), f"Expected reverse sorted order {sorted(test_projects, reverse=True)}, got {reverse_sorted_order}"

    # Clean up
    main_window.close()
    for name in test_projects:
        pdir = base_dir / name
        if pdir.exists():
            shutil.rmtree(pdir)
