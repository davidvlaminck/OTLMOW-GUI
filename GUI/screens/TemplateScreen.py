import asyncio
import logging
import os
import platform

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame, QCheckBox, QSpinBox, \
    QLabel, QListWidget, QListWidgetItem

from Domain import global_vars
from Domain.step_domain.InsertDataDomain import InsertDataDomain
from Domain.step_domain.RelationChangeDomain import RelationChangeDomain
from Domain.step_domain.TemplateDomain import TemplateDomain
from GUI.screens.general_elements.ButtonWidget import ButtonWidget
from GUI.dialog_windows.ChangeSubsetWindow import ChangeSubsetWindow
from GUI.screens.Screen import Screen


class TemplateScreen(Screen):
    def __init__(self, language_settings=None):
        super().__init__()
        self._ = language_settings
        self.container_template_screen = QVBoxLayout()
        self.main_window = None
        self.select_all_classes = QCheckBox()
        self.no_choice_list = QCheckBox()
        self.geometry_column_added = QCheckBox()
        self.export_attribute_info = QCheckBox()
        self.show_deprecated_attributes = QCheckBox()
        self.example_label = QLabel()
        self.export_button = ButtonWidget()
        self.project = None
        self.all_classes = QListWidget()
        self.selected = 0
        self.label_counter = QLabel()
        self.subset_name = QLabel()
        self.operator_name = QLabel()
        self.otl_version = QLabel()
        self.operator_title = QLabel()
        self.otl_title = QLabel()
        self.change_subset_btn = ButtonWidget()
        self.amount_of_examples = QSpinBox()
        self.example_settings_title = QLabel()
        self.non_otl_conform_settings_title = QLabel()
        self.general_settings_title = QLabel()

        self.init_ui()

    def init_ui(self):
        self.container_template_screen.addSpacing(10)
        self.container_template_screen.addWidget(self.template_menu())
        self.container_template_screen.addStretch()
        self.container_template_screen.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.container_template_screen)

    def options_menu(self):
        options_menu = QFrame()
        main_layout = QVBoxLayout()

        self.select_all_classes.setText(self._("select_all_classes"))
        self.select_all_classes.stateChanged.connect(lambda: self.select_all_classes_clicked())

        self.general_settings_title.setProperty('class', 'settings-title')
        self.general_settings_title.setText(self._("general_settings"))

        self.no_choice_list.setText(self._("no_choice_list"))
        self.no_choice_list.setProperty('class', 'settings-checkbox')

        self.geometry_column_added.setText(self._("geometry_column_added"))
        self.geometry_column_added.setProperty('class', 'settings-checkbox')
        self.geometry_column_added.setChecked(True)

        self.non_otl_conform_settings_title.setText(self._("add_non_otl_conform_information"))
        self.non_otl_conform_settings_title.setProperty('class', 'settings-title')

        self.show_deprecated_attributes.setText(self._("show_deprecated_attributes"))
        self.show_deprecated_attributes.setProperty('class', 'settings-checkbox')
        self.show_deprecated_attributes.setEnabled(False)

        self.export_attribute_info.setText(self._("export_attribute_info"))
        self.export_attribute_info.setProperty('class', 'settings-checkbox')

        self.example_settings_title.setProperty('class', 'settings-title')
        self.example_settings_title.setText(self._("example_settings"))

        example_generation_container = self.create_example_generation_container()

        self.export_button.setText(self._("export"))
        self.export_button.setProperty('class', 'primary-button')
        self.export_button.clicked.connect(lambda: self.export_function())

        # build main layout
        main_layout.addSpacing(10)
        main_layout.addWidget(self.general_settings_title)

        main_layout.addWidget(self.no_choice_list)
        main_layout.addWidget(self.geometry_column_added)

        main_layout.addSpacing(10)
        main_layout.addWidget(self.non_otl_conform_settings_title)

        main_layout.addWidget(self.show_deprecated_attributes)
        main_layout.addWidget(self.export_attribute_info)

        main_layout.addSpacing(10)
        main_layout.addWidget(self.example_settings_title)

        main_layout.addWidget(example_generation_container)
        main_layout.addWidget(self.export_button, alignment=Qt.AlignmentFlag.AlignLeft)

        main_layout.addStretch()

        options_menu.setLayout(main_layout)

        return options_menu

    def create_example_generation_container(self):
        example_generation_container = QFrame()
        example_box_layout = QHBoxLayout()
        self.example_label.setText(self._("amount_of_examples"))
        self.example_label.setProperty('class', 'settings-label')
        self.amount_of_examples.setRange(0, 100)
        self.amount_of_examples.setValue(0)
        example_box_layout.addWidget(self.example_label)
        example_box_layout.addWidget(self.amount_of_examples)
        example_generation_container.setLayout(example_box_layout)
        return example_generation_container

    def template_menu(self):
        full_window = QWidget()
        full_window.setProperty('class', 'background-box')
        horizontal_layout = QHBoxLayout()
        window = QFrame()
        layout = QVBoxLayout()
        layout.addWidget(self.subset_title_and_button())
        layout.addWidget(self.options_menu())
        layout.setContentsMargins(16, 0, 16, 0)
        window.setLayout(layout)
        horizontal_layout.addWidget(window)
        horizontal_layout.addWidget(self.create_list())
        horizontal_layout.addSpacing(20)
        full_window.setLayout(horizontal_layout)
        return full_window

    def subset_title_and_button(self):
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

    def create_operator_info_field(self):
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

    def create_otl_version_field(self):
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

    def create_subset_name_field(self):
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

    def subset_info_list(self):
        frame = QFrame()
        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.create_subset_name_field())
        vertical_layout.addWidget(self.create_operator_info_field())
        vertical_layout.addWidget(self.create_otl_version_field())
        frame.setLayout(vertical_layout)
        return frame

    async def fill_list(self):
        self.all_classes.clear()
        item = QListWidgetItem()
        item.setText(self._("loading"))
        self.all_classes.addItem(item)
        try:
            await asyncio.sleep(1)
            self.all_classes.clear()
            self.all_classes.setEnabled(True)
            modelbuilder = self.project.get_model_builder()
            values = modelbuilder.filter_relations_and_abstract()
            for value in values:
                item = QListWidgetItem()
                item.setText(value.name)
                item.setData(1, value.objectUri)
                self.all_classes.addItem(item)
                if TemplateDomain.check_for_no_deprecated_present(values):
                    self.show_deprecated_attributes.setEnabled(False)
        except FileNotFoundError as e:
            self.all_classes.setEnabled(False)
            self.all_classes.addItem(self._("no classes found in specified path"))

        RelationChangeDomain.init_static(global_vars.current_project)
        InsertDataDomain.init_static()
        global_vars.otl_wizard.main_window.enable_steps()

    def create_list(self):
        frame = QFrame()
        vertical_layout = QVBoxLayout()
        self.select_all_classes.setText(self._("select_all_classes"))
        self.select_all_classes.stateChanged.connect(lambda: self.select_all_classes_clicked())
        self.all_classes.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.all_classes.itemSelectionChanged.connect(lambda: self.update_label_under_list())
        vertical_layout.addWidget(self.select_all_classes, alignment=Qt.AlignmentFlag.AlignTop)
        vertical_layout.addWidget(self.all_classes)
        self.label_counter.setText(self._(f"{self.selected} classes selected"))
        vertical_layout.addWidget(self.label_counter)
        frame.setLayout(vertical_layout)
        return frame

    def update_project_info(self):
        try:
            # model_builder = ModelBuilder(self.project.subset_path)
            self.subset_name.setText(self.project.get_subset_db_name())
            self.operator_name.setText(self.project.get_operator_name())
            self.otl_version.setText(self.project.get_otl_version())
        except FileNotFoundError as e:
            self.subset_name.setText("/")
            self.operator_name.setText("/")
            self.otl_version.setText("/")

    def update_label_under_list(self):
        counter = 0
        for i in range(self.all_classes.count()):
            if self.all_classes.item(i).isSelected():
                counter += 1
        self.selected = counter
        self.label_counter.setText(self._("{selected} classes selected").format(selected=self.selected))

    def select_all_classes_clicked(self):
        if not self.all_classes.isEnabled():
            return
        elif self.select_all_classes.isChecked():
            self.all_classes.selectAll()
        else:
            self.all_classes.clearSelection()

    # TODO: niet naar verdere functie gaan indien selected_classes leeg is
    def export_function(self):
        selected_classes = []
        generate_choice_list = not self.no_choice_list.isChecked()
        for item in self.all_classes.selectedItems():
            selected_classes.append(item.data(1))
        document_path = ExportToTemplateWindow().export_to_template_window()
        if document_path is None:
            return
        TemplateDomain().create_template(self.project.subset_path, document_path, selected_classes,
                                         generate_choice_list, self.geometry_column_added.isChecked(),
                                         self.export_attribute_info.isChecked(),
                                         False,
                                         self.amount_of_examples.value())
        if platform.system() == 'Linux':
            os.open(document_path, os.O_WRONLY)
        elif platform.system() == 'Windows':
            os.startfile(document_path)
        else:
            logging.error("Opening a file on this OS is not implemented yet")

    def change_subset(self):
        change_subset_window = ChangeSubsetWindow(self._)
        change_subset_window.change_subset_window(self.project, self.main_window)

    def reset_ui(self, _):
        self._ = _
        if self.project is not None:
            event_loop = asyncio.get_event_loop()
            event_loop.create_task(self.fill_list())
            self.update_project_info()

        # self.show_deprecated_attributes.setText(self._("show_deprecated_attributes"))
        self.export_attribute_info.setText(self._("export_attribute_info"))
        self.geometry_column_added.setText(self._("geometry_column_added"))
        self.no_choice_list.setText(self._("no_choice_list"))
        self.select_all_classes.setText(self._("select_all_classes"))
        self.example_label.setText(self._("amount_of_examples"))
        self.export_button.setText(self._("export"))
        self.change_subset_btn.setText(self._("change_subset"))
        self.operator_title.setText(self._("operator") + ":")
        self.otl_title.setText(self._("otl_version") + ":")
        self.general_settings_title.setText(self._("general_settings"))
        self.example_settings_title.setText(self._("example_settings"))
        self.non_otl_conform_settings_title.setText(self._("deprecated_settings"))
        self.label_counter.setText(self._("{selected} classes selected").format(selected=self.selected))
