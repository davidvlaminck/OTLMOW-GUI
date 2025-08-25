from pathlib import Path

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

def click_ok_on_dialog(qtbot, dialog):
    """Click the OK button on a dialog."""
    button_box = dialog.findChild(QDialogButtonBox)
    ok_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
    qtbot.mouseClick(ok_button, Qt.MouseButton.LeftButton)

# --- Main Test ---

@pytest.mark.gui
def test_otl_wizard_full_playthrough(qtbot, patch_subset_file_picker):
    # Setup application and main window
    settings = Settings.get_or_create_settings_file()
    OTLLogger.init()
    language = GlobalTranslate(settings, LANG_DIR).get_all()
    main_window = MainWindow(language)
    qtbot.addWidget(main_window)
    main_window.show()
    assert main_window.isVisible()

    subset_to_use = Path(__file__).parent / 'test_files' / 'voorbeeld-slagboom.db'

    # Patch the file picker to return the desired subset file
    patch_subset_file_picker(subset_to_use)

    # Step 1: Click "New Project" button to open the UpsertProjectWindow dialog
    qtbot.mouseClick(main_window.home_screen.header.new_project_button, Qt.MouseButton.LeftButton)

    # Step 2: Wait for the dialog to appear and interact with it
    dialog = wait_for_dialog(qtbot, UpsertProjectWindow)
    fill_upsert_project_dialog(qtbot, dialog, eigen_ref="TestProject", bestek="TestBestek", subset=str(subset_to_use))
    click_ok_on_dialog(qtbot, dialog)

    # --- Add more steps here as your playthrough grows ---

    # Clean up
    main_window.close()