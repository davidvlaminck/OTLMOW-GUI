import asyncio
import shutil
import tempfile
from pathlib import Path

import openpyxl
import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLineEdit, QDialogButtonBox, QApplication, QPushButton

import otlmow_gui.Domain.global_vars as global_vars
from otlmow_gui.Domain.logger.OTLLogger import OTLLogger
from otlmow_gui.GUI.MainWindow import MainWindow
from otlmow_gui.GUI.dialog_windows.UpsertProjectWindow import UpsertProjectWindow
from otlmow_gui.GUI.dialog_windows.file_picker_dialog.SubsetLoadFilePickerDialog import SubsetLoadFilePickerDialog
from otlmow_gui.GUI.translation.GlobalTranslate import GlobalTranslate
from otlmow_gui.wizard_main import Settings, LANG_DIR


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


def click_ok_and_expect_close(qtbot, dialog):
    """Click OK and wait for the dialog to close (for successful validation)."""
    button_box = dialog.findChild(QDialogButtonBox)
    ok_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
    assert ok_button is not None, "OK button not found"
    qtbot.mouseClick(ok_button, Qt.MouseButton.LeftButton)
    qtbot.waitUntil(lambda: not dialog.isVisible(), timeout=10000)



@pytest.fixture(autouse=True)
def patch_template_save_file_picker_dialog(monkeypatch):
    """
    Monkeypatch TemplateSaveFilePickerDialog.summon to return the desired export path for template export.
    """
    from otlmow_gui.GUI.dialog_windows.file_picker_dialog.TemplateSaveFilePickerDialog import TemplateSaveFilePickerDialog
    def fake_summon(self, *args, **kwargs):
        import tempfile
        project_name = "FullTestRunProject_1b_4"
        export_path = Path(tempfile.gettempdir()) / f"{project_name}_template.xlsx"
        return [export_path]
    monkeypatch.setattr(TemplateSaveFilePickerDialog, "summon", fake_summon)


@pytest.mark.gui
@pytest.mark.asyncio
async def test_1_4_template_generation_and_class_selection(qtbot, patch_subset_file_picker):
    """
    TEST stap 1: Aanmaken van template
    - Maak een nieuw project aan (zoals in 1a test_3).
    - Check of alle classes initieel geselecteerd zijn
    - Deselecteer de Contactor en de Kokerafsluiting klasse
    - Genereer een EXCEL file met uitgebreide info en alle andere opties aan
    - Check of alleen de aangeduide 4 klasses aanwezig zijn
    - Verwijder in elke sheet de eerste RIJ met omschrijvingen en save
    """


    # --- Setup and Project Creation ---
    project_name = "FullTestRunProject_1b_4"
    project_dir = Path.home() / 'OTLWizardProjects' / 'Projects' / project_name
    export_path = Path(tempfile.gettempdir()) / f"{project_name}_template.xlsx"
    slagboom_subset = Path(__file__).parent.parent.parent / "otlmow_gui" / "demo_projects" / "slagbomen_project" / "voorbeeld-slagboom.db"

    # Clean up before test
    if project_dir.exists():
        shutil.rmtree(project_dir)
    if export_path.exists():
        export_path.unlink()

    try:
        # App and main window
        settings = Settings.get_or_create_settings_file()
        OTLLogger.init()
        language = GlobalTranslate(settings, LANG_DIR).get_all()
        main_window = MainWindow(language)
        global_vars.otl_wizard = type("FakeApp", (), {})()
        global_vars.otl_wizard.main_window = main_window
        qtbot.addWidget(main_window)
        main_window.show()
        assert main_window.isVisible()

        # Patch file picker for subset
        patch_subset_file_picker(slagboom_subset)

        # Create new project
        qtbot.mouseClick(main_window.home_screen.header.new_project_button, Qt.MouseButton.LeftButton)
        dialog = wait_for_dialog(qtbot, UpsertProjectWindow)
        fill_upsert_project_dialog(qtbot, dialog, eigen_ref=project_name, bestek="TestBestek", subset=str(slagboom_subset))
        click_ok_and_expect_close(qtbot, dialog)

        # Wait for project to appear in table
        qtbot.waitUntil(lambda: main_window.home_screen.table.rowCount() > 0, timeout=10000)

        # Select the project in the table (find the row, but do not double-click)
        found = any(main_window.home_screen.table.item(r, 0).text() == project_name
                    for r in range(main_window.home_screen.table.rowCount()))
        assert found, f"Project {project_name} not found in table"

        # Open the project using the application logic
        from otlmow_gui.Domain.step_domain.HomeDomain import HomeDomain
        HomeDomain.open_project(project_name)
        await asyncio.sleep(0.5)  # Give async project/domain init time

        class_table = main_window.step1.all_classes
        qtbot.waitUntil(lambda: class_table.count() > 0, timeout=5000)

        # Check all classes are initially selected
        selected_classes = [class_table.item(r).text() for r in range(class_table.count()) if
                            class_table.item(r).isSelected()]
        all_classes = [class_table.item(r).text() for r in range(class_table.count())]
        assert selected_classes, "No classes are selected initially"
        assert set(selected_classes) == set(all_classes), "Not all classes are initially selected"

        # --- Deselect Contactor and Kokerafsluiting ---
        from otlmow_gui.Domain.step_domain.TemplateDomain import TemplateDomain
        deselect_set = {"Contactor", "Kokerafsluiting"}
        indexes_to_select = [
            class_table.item(r).data(1)[1]
            for r in range(class_table.count())
            if class_table.item(r).text() not in deselect_set
        ]
        TemplateDomain.set_selected_indexes(indexes_to_select)
        class_table.clearSelection()
        for r in range(class_table.count()):
            if class_table.item(r).data(1)[1] in indexes_to_select:
                class_table.item(r).setSelected(True)
        class_table.sync_selected_items_with_backend()

        # Update label and export button state
        main_window.step1.update_label_under_list(
            total_amount_of_items=class_table.count(),
            counter=len([i for i in range(class_table.count()) if class_table.item(i).isSelected()])
        )
        main_window.step1.export_button.setEnabled(True)

        # Ensure backend selection is correct
        selected_indexes = [class_table.item(r).data(1)[1] for r in range(class_table.count()) if
                            class_table.item(r).isSelected()]
        TemplateDomain.set_selected_indexes(selected_indexes)

        # --- Enable all export options ---
        main_window.step1.add_choice_list.setChecked(True)
        main_window.step1.add_geometry_attributes.setChecked(True)
        main_window.step1.export_attribute_info.setChecked(True)
        main_window.step1.example_amount_checkbox.setChecked(True)
        main_window.step1.radio_button_expanded_info.setChecked(True)

        # --- Generate Excel with all options enabled ---
        export_btn = main_window.step1.export_button
        assert export_btn is not None, "Export button not found on TemplateScreen"
        if export_path.exists():
            export_path.unlink()
        qtbot.mouseClick(export_btn, Qt.MouseButton.LeftButton)
        await asyncio.sleep(0.2)  # Give async export a moment to start

        # Wait for file to be created (async export)
        async def wait_for_file(path, poll_interval=0.1):
            while not path.exists():
                await asyncio.sleep(poll_interval)
            return path

        try:
            await asyncio.wait_for(wait_for_file(export_path), timeout=7)
        except asyncio.TimeoutError:
            raise TimeoutError(f"Excel file {export_path} was not created after 10 seconds")
        assert export_path.exists(), f"Excel file {export_path} was not created"

        # --- Check only the 4 classes are present in the Excel ---
        wb = openpyxl.load_workbook(export_path)
        expected_classes = {
            'https://wegenenverkeer.data.vlaanderen.be/ns/installatie#Slagboom',
            'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Slagboomarm',
            'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#SlagboomarmVerlichting',
            'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Slagboomkolom'
        }
        for sheet in wb.sheetnames:
            if sheet == 'Keuzelijsten':
                continue
            ws = wb[sheet]
            uri_value = ws['A'][2].value
            assert uri_value in expected_classes, f"Unexpected value in sheet {sheet}: {uri_value}"
            expected_classes.remove(uri_value)
        assert not expected_classes, f"Not all expected classes were found in the Excel. Missing: {expected_classes}"

        # Remove first row from each sheet and save
        for ws in wb.worksheets:
            ws.delete_rows(1)
        wb.save(export_path)

    finally:
        # --- Clean up ---
        if project_dir.exists():
            shutil.rmtree(project_dir)
        if export_path.exists():
            export_path.unlink()
