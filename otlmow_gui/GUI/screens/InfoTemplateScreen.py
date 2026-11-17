from copy import deepcopy
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush, QColor, QFont
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QListWidget, QListWidgetItem, QCheckBox

from otlmow_modelbuilder.SQLDataClasses.OSLOClass import OSLOClass

from otlmow_gui.Domain import global_vars
from otlmow_gui.Domain.project.Project import Project
from otlmow_gui.Domain.step_domain.TemplateDomain import TemplateDomain
from otlmow_gui.Domain.util.Helpers import Helpers
from otlmow_gui.GUI.dialog_windows.file_picker_dialog.InfoTemplateSaveFilePickerDialog import \
    InfoTemplateSaveFilePickerDialog
from otlmow_gui.GUI.screens.TemplateScreen_elements.ClassListWidget import ClassListWidget
from otlmow_gui.GUI.screens.general_elements.ButtonWidget import ButtonWidget
from otlmow_gui.GUI.dialog_windows.ChangeSubsetWindow import ChangeSubsetWindow
from otlmow_gui.GUI.screens.screen_interface.TemplateScreenInterface import TemplateScreenInterface
from otlmow_gui.exception_handler.ExceptionHandlers import create_task_reraise_exception
from otlmow_template.InfotemplateGenerator import InfotemplateGenerator


class InfoTemplateScreen(TemplateScreenInterface):
    """Screen for creating info templates.

    This tab provides class selection functionality identical to the aanlever template,
    but without the format options - directly exporting with expanded info settings.
    """

    def __init__(self, language_settings=None):
        super().__init__()
        self._ = language_settings

        self.project = None
        self.main_window = None
        self.main_layout = QVBoxLayout()

        # project information overview box
        self.subset_name = QLabel()
        self.operator_name = QLabel()
        self.otl_version = QLabel()
        self.operator_title = QLabel()
        self.otl_title = QLabel()
        self.change_subset_btn = ButtonWidget()

        # class GUI list elements
        self.select_all_classes = QCheckBox()
        self.all_classes = ClassListWidget()
        self.selected = 0
        self.label_counter = QLabel()

        # export button
        self.export_button = ButtonWidget()

        self.template_export_file_picker = InfoTemplateSaveFilePickerDialog(self._)

        self.init_ui()

    def init_ui(self) -> None:
        self.main_layout.addSpacing(10)
        self.main_layout.addWidget(self.template_menu())
        self.main_layout.addSpacing(10)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)

    def template_menu(self) -> QWidget:
        full_window = QWidget()
        full_window.setProperty('class', 'background-box')
        horizontal_layout = QHBoxLayout()
        window = QFrame()
        layout = QVBoxLayout()
        layout.addWidget(self.subset_title_and_button())
        layout.addWidget(self.options_menu())
        layout.setContentsMargins(16, 0, 16, 0)
        window.setLayout(layout)
        horizontal_layout.addWidget(window, stretch=1)
        horizontal_layout.addWidget(self.create_list(), stretch=2)
        horizontal_layout.addSpacing(20)
        full_window.setLayout(horizontal_layout)
        return full_window

    def subset_title_and_button(self) -> QFrame:
        frame = QFrame()
        horizontal_layout = QHBoxLayout()
        self.change_subset_btn.setText(self._("change_subset"))
        self.change_subset_btn.clicked.connect(lambda: self.change_subset())
        self.change_subset_btn.setProperty('class', 'secondary-button')
        horizontal_layout.addWidget(self.subset_info_list())
        horizontal_layout.addWidget(self.change_subset_btn, alignment=Qt.AlignmentFlag.AlignRight)
        horizontal_layout.setContentsMargins(0, 16, 0, 16)
        frame.setLayout(horizontal_layout)
        return frame

    def create_operator_info_field(self) -> QFrame:
        frame = QFrame()
        horizontal_layout = QHBoxLayout()
        self.operator_title.setText(self._("operator") + ":")
        self.operator_title.setProperty('class', 'info-label')
        self.operator_name.setText("")
        horizontal_layout.addWidget(self.operator_title)
        horizontal_layout.addWidget(self.operator_name, alignment=Qt.AlignmentFlag.AlignRight)
        horizontal_layout.setContentsMargins(0, 0, 0, 0)
        frame.setLayout(horizontal_layout)
        return frame

    def create_otl_version_field(self) -> QFrame:
        frame = QFrame()
        horizontal_layout = QHBoxLayout()
        self.otl_title.setText(self._("otl_version") + ":")
        self.otl_title.setProperty('class', 'info-label')
        self.otl_version.setText("")
        horizontal_layout.addWidget(self.otl_title)
        horizontal_layout.addWidget(self.otl_version, alignment=Qt.AlignmentFlag.AlignRight)
        horizontal_layout.setContentsMargins(0, 0, 0, 0)
        frame.setLayout(horizontal_layout)
        return frame

    def create_subset_name_field(self) -> QFrame:
        frame = QFrame()
        horizontal_layout = QHBoxLayout()
        subset_title = QLabel()
        subset_title.setText(self._("subset") + ":")
        subset_title.setProperty('class', 'info-label')
        self.subset_name.setText("")
        horizontal_layout.addWidget(subset_title)
        horizontal_layout.addWidget(self.subset_name, alignment=Qt.AlignmentFlag.AlignRight)
        horizontal_layout.setContentsMargins(0, 0, 0, 0)
        frame.setLayout(horizontal_layout)
        return frame

    def subset_info_list(self) -> QFrame:
        frame = QFrame()
        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.create_subset_name_field())
        vertical_layout.addWidget(self.create_operator_info_field())
        vertical_layout.addWidget(self.create_otl_version_field())
        frame.setLayout(vertical_layout)
        return frame

    def options_menu(self) -> QFrame:
        options_menu = QFrame()
        main_layout = QVBoxLayout()

        self.export_button.setText(self._("export"))
        self.export_button.setProperty('class', 'primary-button')
        self.export_button.clicked.connect(lambda: self.export_template_listener())
        self.export_button.setEnabled(False)
        self.export_button.setToolTip(self._("Select at least 1 class to export"))

        main_layout.addStretch()
        main_layout.addWidget(self.export_button, alignment=Qt.AlignmentFlag.AlignLeft)
        main_layout.addStretch()

        options_menu.setLayout(main_layout)
        return options_menu

    def create_list(self) -> QFrame:
        frame = QFrame()
        vertical_layout = QVBoxLayout()

        self.select_all_classes.setText(self._("select_all_classes"))
        self.select_all_classes.clicked.connect(lambda: self.select_all_classes_clicked())
        self.all_classes.setSelectionMode(QListWidget.SelectionMode.MultiSelection)

        self.all_classes.doubleClicked.connect(
            lambda item:
                 self.all_classes.itemFromIndex(item).setSelected(not self.all_classes.itemFromIndex(item).isSelected())
        )
        self.label_counter.setText(self._(f"{self.selected} classes selected"))

        vertical_layout.addWidget(self.select_all_classes, alignment=Qt.AlignmentFlag.AlignTop)
        vertical_layout.addWidget(self.all_classes)
        vertical_layout.addWidget(self.label_counter)
        frame.setLayout(vertical_layout)

        return frame

    def update_project_info(self, project: Project) -> None:
        if project:
            try:
                self.subset_name.setText(project.get_subset_db_name())
                self.operator_name.setText(project.get_operator_name())
                self.otl_version.setText(project.get_otl_version())
            except FileNotFoundError as e:
                self.subset_name.setText("/")
                self.operator_name.setText("/")
                self.otl_version.setText("/")
        else:
            self.subset_name.setText("Loading")
            self.operator_name.setText("Loading")
            self.otl_version.setText("Loading")

    def update_label_under_list(self, total_amount_of_items: int, counter: int) -> None:
        self.selected = counter
        self.label_counter.setText(self._("{selected} classes selected").format(selected=self.selected))
        if counter:
            self.export_button.setEnabled(True)
            self.export_button.setToolTip(self._("Export template"))
        else:
            self.export_button.setEnabled(False)
            self.export_button.setToolTip(self._("Select at least 1 class to export"))

    def update_all_classes_selected(self, state: bool) -> None:
        self.select_all_classes.setChecked(state)

    def select_all_classes_clicked(self):
        if not self.all_classes.isEnabled():
            return
        TemplateDomain.set_select_all_classes(self.select_all_classes.isChecked())

    def deselect_all_classes(self) -> None:
        self.all_classes.clearSelection()

    def set_all_classes_selected(self) -> None:
        self.all_classes.selectAll()

    def export_template_listener(self) -> None:
        selection_path_list = self.template_export_file_picker.summon(
            chosen_file_format="",
            supported_export_formats=None,
            project_name=global_vars.current_project.eigen_referentie)
        try:
            self.save_template(selection_path_list)
        except Exception as e:
            raise e

    def save_template(self, document_paths: list[Path]):
        if not document_paths or not document_paths[0]:
            return
        document_path = document_paths[0]

        project = global_vars.current_project
        if not project:
            return

        generator = InfotemplateGenerator()
        create_task_reraise_exception(generator.generate_infotemplate_from_subset_async(
            subset_path=project.subset_path,
            template_file_path=document_path
        ))

    def change_subset(self) -> None:
        ChangeSubsetWindow(self._)

    def reset_ui(self, _) -> None:
        super().reset_ui(_)
        self._ = _
        self.export_button.setText(self._("export"))
        self.change_subset_btn.setText(self._("change_subset"))
        self.operator_title.setText(self._("operator") + ":")
        self.otl_title.setText(self._("otl_version") + ":")
        self.select_all_classes.setText(self._("select_all_classes"))
        self.label_counter.setText(self._("{selected} classes selected").format(selected=self.selected))

    def set_gui_list_to_loading_state(self) -> None:
        item = QListWidgetItem()
        item.setText(self._("loading"))
        self.all_classes.clear()
        self.all_classes.addItem(item)

    def set_gui_list_to_no_classes_found(self) -> None:
        self.all_classes.setEnabled(False)
        self.all_classes.addItem(self._("no classes found in specified path"))

    def set_classes(self, classes: list[OSLOClass],
                    selected_classes: list[int],
                    all_classes_selected_checked: bool,
                    has_a_class_with_deprecated_attributes: bool) -> None:
        self.all_classes.clear()
        self.all_classes.setEnabled(True)

        class_index_tuple_list = [(OTL_class, i) for i, OTL_class in enumerate(classes)]
        sorted_classes = sorted(class_index_tuple_list, key=lambda x: x[0].name)

        for value_tuple in sorted_classes:
            class_name = value_tuple[0].name
            class_typeURI = value_tuple[0].objectUri
            backend_index = value_tuple[1]

            item = QListWidgetItem()
            item.setText(class_name)
            item.setData(1, (class_typeURI, backend_index))

            if class_name == "Agent":
                item.setBackground(QBrush(QColor("#AAAAAA")))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
                placeholder_font = QFont()
                placeholder_font.setItalic(True)
                item.setFont(placeholder_font)
                item.setToolTip(self._('Agent class is not allowed in the template'))

            self.all_classes.addItem(item)

        if all_classes_selected_checked:
            self.set_all_classes_selected()
        else:
            self.update_all_classes_selected(False)
            for class_display_index in range(self.all_classes.count()):
                item = self.all_classes.item(class_display_index)
                real_index = item.data(1)[1]
                if real_index in selected_classes:
                    item.setSelected(True)

        self.update_label_under_list(
            total_amount_of_items=TemplateDomain.get_total_amount_of_classes(),
            counter=len(selected_classes))

    def open_folder_of_created_template(self, document_path: Path):
        Helpers.open_folder_and_select_document(document_path=document_path)

    def opened(self):
        TemplateDomain.update_frontend()