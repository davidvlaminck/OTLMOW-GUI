import logging
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFrame, QCheckBox, QSpinBox, \
    QLabel, QListWidget

from Domain.language_settings import return_language
from Domain.model_builder import ModelBuilder
from GUI.Screens.screen import Screen
from GUI.dialog_window import DialogWindow

ROOT_DIR = Path(__file__).parent
LANG_DIR = ROOT_DIR.parent.parent / 'locale/'


class TemplateScreen(Screen):
    def __init__(self):
        super().__init__()
        self._ = return_language(LANG_DIR)
        self.container_template_screen = QVBoxLayout()
        self.stacked_widget = None
        self.select_all_classes = QCheckBox()
        self.no_choice_list = QCheckBox()
        self.geometry_column_added = QCheckBox()
        self.export_attribute_info = QCheckBox()
        self.show_deprecated_attributes = QCheckBox()
        self.example_label = QLabel()
        self.export_button = QPushButton()
        self.project = None
        self.all_classes = QListWidget()
        self.selected = 0
        self.label_counter = QLabel()
        self.subset_name = QLabel()
        self.operator_name = QLabel()
        self.otl_version = QLabel()
        self.operator_title = QLabel()
        self.otl_title = QLabel()
        self.change_subset_btn = QPushButton()
        self.amount_of_examples = QSpinBox()

        self.init_ui()

    def init_ui(self):
        self.container_template_screen.addSpacing(10)
        self.container_template_screen.addWidget(self.template_menu())
        self.container_template_screen.addStretch()
        self.container_template_screen.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.container_template_screen)

    def options_menu(self):
        options_menu = QFrame()
        options_menu_layout = QVBoxLayout()
        self.select_all_classes.setText(self._("select_all_classes"))
        self.select_all_classes.stateChanged.connect(lambda: self.select_all_classes_clicked())
        self.no_choice_list.setText(self._("no_choice_list"))
        self.geometry_column_added.setText(self._("geometry_column_added"))
        self.export_attribute_info.setText(self._("export_attribute_info"))
        self.show_deprecated_attributes.setText(self._("show_deprecated_attributes"))
        example_box = QFrame()
        example_box_layout = QHBoxLayout()
        self.example_label.setText(self._("amount_of_examples"))
        self.amount_of_examples.setRange(0, 100)
        self.amount_of_examples.setValue(0)

        example_box_layout.addWidget(self.example_label)
        example_box_layout.addWidget(self.amount_of_examples)
        example_box.setLayout(example_box_layout)

        self.export_button.setText(self._("export"))
        self.export_button.setProperty('class', 'primary-button')
        self.export_button.clicked.connect(lambda: self.export_function())

        options_menu_layout.addWidget(self.select_all_classes)
        options_menu_layout.addSpacing(10)
        options_menu_layout.addWidget(self.no_choice_list)
        options_menu_layout.addWidget(self.geometry_column_added)
        options_menu_layout.addWidget(self.export_attribute_info)
        options_menu_layout.addWidget(self.show_deprecated_attributes)
        options_menu_layout.addWidget(example_box, alignment=Qt.AlignmentFlag.AlignLeft)
        options_menu_layout.addWidget(self.export_button, alignment=Qt.AlignmentFlag.AlignLeft)
        options_menu_layout.addStretch()
        options_menu.setLayout(options_menu_layout)
        return options_menu

    def template_menu(self):
        full_window = QWidget()
        full_window.setProperty('class', 'background-box')
        horizontal_layout = QHBoxLayout()
        window = QFrame()
        layout = QVBoxLayout()
        layout.addWidget(self.subset_title_and_button())
        layout.addWidget(self.create_operator_info_field(), alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.create_otl_version_field(), alignment=Qt.AlignmentFlag.AlignLeft)
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
        subset_title = QLabel()
        subset_title.setText(self._("subset") + ":")
        self.subset_name.setText("")
        self.change_subset_btn.setText(self._("change_subset"))
        self.change_subset_btn.clicked.connect(lambda: self.change_subset())
        self.change_subset_btn.setProperty('class', 'secondary-button')
        horizontal_layout.addWidget(subset_title)
        horizontal_layout.addWidget(self.subset_name)
        horizontal_layout.addSpacing(30)
        horizontal_layout.addWidget(self.change_subset_btn, alignment=Qt.AlignmentFlag.AlignRight)
        horizontal_layout.setContentsMargins(0, 16, 0, 16)
        frame.setLayout(horizontal_layout)
        return frame

    def create_operator_info_field(self):
        frame = QFrame()
        horizontal_layout = QHBoxLayout()
        self.operator_title.setText(self._("operator") + ":")
        self.operator_name.setText("")
        horizontal_layout.addWidget(self.operator_title)
        horizontal_layout.addWidget(self.operator_name)
        horizontal_layout.setContentsMargins(0, 0, 0, 0)
        frame.setLayout(horizontal_layout)
        return frame

    def create_otl_version_field(self):
        frame = QFrame()
        horizontal_layout = QHBoxLayout()
        self.otl_title.setText(self._("otl_version") + ":")
        self.otl_version.setText("")
        horizontal_layout.addWidget(self.otl_title)
        horizontal_layout.addWidget(self.otl_version, alignment=Qt.AlignmentFlag.AlignLeft)
        horizontal_layout.setContentsMargins(0, 0, 0, 0)
        frame.setLayout(horizontal_layout)
        return frame

    def fill_list(self):
        self.all_classes.clear()
        try:
            self.all_classes.setEnabled(True)
            values = ModelBuilder(self.project.subset_path).filter_relations_and_abstract()
            for value in values:
                self.all_classes.addItem(value.name)
        except FileNotFoundError as e:
            self.all_classes.setEnabled(False)
            self.all_classes.addItem(self._("no classes found in specified path"))

    def create_list(self):
        frame = QFrame()
        vertical_layout = QVBoxLayout()
        self.all_classes.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.all_classes.itemSelectionChanged.connect(lambda: self.update_label_under_list())
        vertical_layout.addWidget(self.all_classes)
        self.label_counter.setText(self._(f"{self.selected} classes selected"))
        vertical_layout.addWidget(self.label_counter)
        frame.setLayout(vertical_layout)
        return frame

    def update_project_info(self):
        try:
            model_builder = ModelBuilder(self.project.subset_path)
            self.subset_name.setText(model_builder.get_name_project())
            self.operator_name.setText(model_builder.get_operator_name())
            self.otl_version.setText(model_builder.get_otl_version())
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
        self.label_counter.setText(self._(f"{self.selected} classes selected"))

    def select_all_classes_clicked(self):
        if not self.all_classes.isEnabled():
            return
        elif self.select_all_classes.isChecked():
            self.all_classes.selectAll()
        else:
            self.all_classes.clearSelection()

    def export_function(self):
        logging.debug("No choice list: " + str(self.no_choice_list.isChecked()))
        logging.debug("Geometry column added: " + str(self.geometry_column_added.isChecked()))
        logging.debug("Export attribute info: " + str(self.export_attribute_info.isChecked()))
        logging.debug("Show deprecated attributes: " + str(self.show_deprecated_attributes.isChecked()))
        logging.debug("Amount of examples: " + str(self.amount_of_examples.value()))

    def reset_ui(self, _):
        self._ = _

        self.fill_list()
        self.update_project_info()

        self.show_deprecated_attributes.setText(self._("show_deprecated_attributes"))
        self.export_attribute_info.setText(self._("export_attribute_info"))
        self.geometry_column_added.setText(self._("geometry_column_added"))
        self.no_choice_list.setText(self._("no_choice_list"))
        self.select_all_classes.setText(self._("select_all_classes"))
        self.example_label.setText(self._("amount_of_examples"))
        self.export_button.setText(self._("export"))
        self.change_subset_btn.setText(self._("change_subset"))
        self.operator_title.setText(self._("operator") + ":")
        self.otl_title.setText(self._("otl_version") + ":")

    def change_subset(self):
        dialog_window = DialogWindow(self._)
        dialog_window.change_subset_window(self.project, self.stacked_widget)

