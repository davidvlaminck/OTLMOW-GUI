from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFrame, QCheckBox, QSpinBox, \
    QLabel, QListWidget

from Domain.language_settings import return_language
from Domain.model_builder import ModelBuilder
from GUI.Screens.Screen import Screen
from GUI.header_bar import HeaderBar
from GUI.stepper import StepperWidget

ROOT_DIR = Path(__file__).parent
LANG_DIR = ROOT_DIR.parent.parent / 'locale/'


class TemplateScreen(Screen):
    def __init__(self, database):
        super().__init__()
        self.database = database
        self._ = self._ = return_language(LANG_DIR)
        self.header = HeaderBar(self._, self.database)
        self.container_template_screen = QVBoxLayout()
        self.stacked_widget = None
        self.stepper_widget = StepperWidget(self._)
        self.select_all_classes = QCheckBox()
        self.no_choice_list = QCheckBox()
        self.geometry_column_added = QCheckBox()
        self.export_attribute_info = QCheckBox()
        self.show_deprecated_attributes = QCheckBox()
        self.example_label = QLabel()
        self.export_button = QPushButton()
        self.path = None
        self.all_classes = QListWidget()

        self.init_ui()

    def init_ui(self):
        button = self.header.header_bar_detail_screen('subtitle_page_1')
        button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        self.container_template_screen.addWidget(self.header)
        self.container_template_screen.addSpacing(10)
        self.container_template_screen.addWidget(self.stepper_widget.stepper_widget())
        self.container_template_screen.addSpacing(10)
        self.container_template_screen.addWidget(self.template_menu())
        self.container_template_screen.addStretch()
        self.container_template_screen.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.container_template_screen)

    def options_menu(self):
        options_menu = QFrame()
        options_menu.setProperty('class', 'options-menu')
        options_menu_layout = QVBoxLayout()
        self.select_all_classes.setText(self._("select_all_classes"))
        self.no_choice_list.setText(self._("no_choice_list"))
        self.geometry_column_added.setText(self._("geometry_column_added"))
        self.export_attribute_info.setText(self._("export_attribute_info"))
        self.show_deprecated_attributes.setText(self._("show_deprecated_attributes"))
        example_box = QFrame()
        example_box_layout = QHBoxLayout()
        self.example_label.setText(self._("amount_of_examples"))
        amount_of_examples = QSpinBox()
        amount_of_examples.setRange(0, 100)
        amount_of_examples.setValue(0)

        example_box_layout.addWidget(self.example_label)
        example_box_layout.addWidget(amount_of_examples)
        example_box.setLayout(example_box_layout)

        self.export_button.setText(self._("export"))
        self.export_button.setProperty('class', 'primary-button')

        options_menu_layout.addWidget(self.select_all_classes)
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
        horizontal_layout = QHBoxLayout()
        window = QFrame()
        window.setProperty('class', 'template-menu')
        layout = QVBoxLayout()
        layout.addWidget(self.subset_title_and_button(), alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.options_menu())
        layout.setContentsMargins(16, 0, 16, 0)
        window.setLayout(layout)
        horizontal_layout.addWidget(window)
        horizontal_layout.addWidget(self.all_classes)
        full_window.setLayout(horizontal_layout)
        return full_window

    def subset_title_and_button(self):
        frame = QFrame()
        title = QLabel()
        title.setText(self._("subset")+":")
        subset_name = QLabel()
        subset_name.setText("test")
        button = QPushButton()
        button.setText(self._("change_subset"))
        button.setProperty('class', 'secondary-button')
        horizontal_layout = QHBoxLayout()
        horizontal_layout.addWidget(title)
        horizontal_layout.addWidget(subset_name)
        horizontal_layout.addSpacing(30)
        horizontal_layout.addWidget(button)
        frame.setLayout(horizontal_layout)
        return frame

    def fill_list(self):
        self.all_classes.clear()
        for value in ModelBuilder(self.path).get_all_classes():
            self.all_classes.addItem(value.name)

    def reset_ui(self, _):
        self._ = _

        self.show_deprecated_attributes.setText(self._("show_deprecated_attributes"))
        self.export_attribute_info.setText(self._("export_attribute_info"))
        self.geometry_column_added.setText(self._("geometry_column_added"))
        self.no_choice_list.setText(self._("no_choice_list"))
        self.select_all_classes.setText(self._("select_all_classes"))
        self.example_label.setText(self._("amount_of_examples"))
        self.export_button.setText(self._("export"))

        self.header.reset_ui(self._, 'subtitle_page_1')
        self.stepper_widget.reset_ui(self._)