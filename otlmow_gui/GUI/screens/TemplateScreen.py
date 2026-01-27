from copy import deepcopy
from enum import IntEnum
from pathlib import Path
from typing import NamedTuple

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush, QColor, QFont
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame, QCheckBox, QSpinBox, \
    QLabel, QListWidget, QListWidgetItem, QButtonGroup, QRadioButton, QComboBox, QSizePolicy
from otlmow_modelbuilder.SQLDataClasses.OSLOClass import OSLOClass

from otlmow_gui.Domain import global_vars
from otlmow_gui.Domain.project.Project import Project
from otlmow_gui.Domain.step_domain.TemplateDomain import TemplateDomain
from otlmow_gui.Domain.util.Helpers import Helpers
from otlmow_gui.GUI.dialog_windows.file_picker_dialog.TemplateSaveFilePickerDialog import \
    TemplateSaveFilePickerDialog
from otlmow_gui.GUI.screens.TemplateScreen_elements.ClassListWidget import ClassListWidget
from otlmow_gui.GUI.screens.general_elements.ButtonWidget import ButtonWidget
from otlmow_gui.GUI.dialog_windows.ChangeSubsetWindow import ChangeSubsetWindow
from otlmow_gui.GUI.screens.screen_interface.TemplateScreenInterface import TemplateScreenInterface
from otlmow_gui.exception_handler.ExceptionHandlers import create_task_reraise_exception


class TemplateScreen(TemplateScreenInterface):
    """Represents the template screen for managing project settings and data export.

    This class provides a user interface for exporting templates.
    It includes various UI components such as labels, buttons, checkboxes, and lists to facilitate
    user interactions and display relevant information.

    Args:f
        language_settings (optional): Language settings for the user interface.

    Attributes:
        project (optional): The current project associated with the template screen.
        main_window (optional): Reference to the main application window.
        main_layout (QVBoxLayout): Layout for organizing UI components vertically.
        subset_name (QLabel): Label for displaying the subset name.
        operator_name (QLabel): Label for displaying the operator's name.
        otl_version (QLabel): Label for displaying the OTL version.
        operator_title (QLabel): Label for the operator title.
        otl_title (QLabel): Label for the OTL title.
        change_subset_btn (ButtonWidget): Button for changing the subset.
        general_settings_title (QLabel): Title label for general settings.
        add_choice_list (QCheckBox): Checkbox for no choice list option.
        add_geometry_attributes (QCheckBox): Checkbox for geometry column addition.
        export_button (ButtonWidget): Button for exporting data.
        export_attribute_info (QCheckBox): Checkbox for exporting attribute information.
        show_deprecated_attributes (QCheckBox): Checkbox for showing deprecated attributes.
        example_amount_checkbox (QLabel): Label for the example amount setting.
        non_otl_conform_settings_title (QLabel): Title label for non-OTL conform settings.
        amount_of_examples (QSpinBox): Spin box for specifying the amount of examples.
        example_settings_title (QLabel): Title label for example settings.
        select_all_classes (QCheckBox): Checkbox for selecting all classes.
        all_classes (QListWidget): List widget for displaying available classes.
        selected (int): Counter for the number of selected classes.
        label_counter (QLabel): Label for displaying the count of selected classes.
    """

    class TemplateOptionId(IntEnum):
        DAVIE_CONFORM = 0
        EXTRA_INFO = 1




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

        # Combobox to select the export file type
        self.file_extension_selection: QComboBox = QComboBox()
        self.add_resetable_field(self.file_extension_selection)
        self.file_type_label: QLabel = QLabel()
        self.supported_export_formats: dict = deepcopy(global_vars.supported_file_formats)

        # if "SDF" in self.supported_export_formats:
        #     self.supported_export_formats.pop("SDF")  # not yet supported for export in V0.5.3
        if "JSON" in self.supported_export_formats:
            self.supported_export_formats.pop("JSON")  # Doesn't support template creation
        if "GeoJSON" in self.supported_export_formats:
            self.supported_export_formats.pop("GeoJSON")  # Doesn't support template creation

        FileTypeSettingPropertySetting = NamedTuple("FileTypeSettingPropertySetting",[
            ("enabled",bool),
            ("change_state_if_enabled",bool),
            ("default_on",bool),
            ("tooltip",str)])
        FileTypeSetting = NamedTuple("FileTypeSetting", [
            ("choice_lists",FileTypeSettingPropertySetting),
            ("example_assets",FileTypeSettingPropertySetting),
            ("geometry_attributes", FileTypeSettingPropertySetting),
            ("expansive_info", FileTypeSettingPropertySetting)])

        self.default_choice_list_tooltip = self._("Adds choice lists to relevant "
                                                           "attributes")
        self.always_on_choice_list_tooltip = self._(
            "For {filetype} choice lists cannot be disabled")
        self.always_off_choice_list_tooltip = self._("{filetype} cannot contain choice lists")

        self.default_geometry_tooltip = self._("Adds geometry information for each asset")
        self.always_on_geometry_tooltip = self._(
            "For {filetype} geometry attributes cannot be disabled")
        self.always_off_geometry_tooltip = self._("{filetype} cannot contain geometry attributes")

        self.default_example_checkbox_tooltip = self._("Adds example assets to each OTL-class")
        self.always_on_example_checkbox_tooltip = self._(
            "For {filetype} generated examples cannot be disabled")
        self.always_off_example_checkbox_tooltip = self._(
            "{filetype} cannot add generated examples")

        self.default_expansive_info_radiobutton_tooltip = (
            self._("Adds extra rows with a description of every attribute and, an indication if the"
                   " attribute is deprecated \n(Delete extra rows before uploading to DAVIE)"))
        self.always_on_expansive_info_radiobutton_tooltip = self._(
            "For {filetype} expansive information cannot be disabled")
        self.always_off_expansive_info_radiobutton_tooltip = self._(
            "{filetype} cannot add expansive information")

        self.file_type_settings:dict[str,FileTypeSetting] = {}
        self.file_type_settings = {"Excel":FileTypeSetting(
                                        choice_lists= FileTypeSettingPropertySetting(
                                            enabled=True,
                                            change_state_if_enabled=True,
                                            default_on=True,
                                            tooltip= self.default_choice_list_tooltip.format(filetype="Excel")
                                        ),
                                        geometry_attributes= FileTypeSettingPropertySetting(
                                            enabled=True,
                                            change_state_if_enabled=True,
                                            default_on=True,
                                            tooltip=self.default_geometry_tooltip
                                        ),
                                        example_assets= FileTypeSettingPropertySetting(
                                            enabled=True,
                                            change_state_if_enabled=True,
                                            default_on=False,
                                            tooltip=self.default_example_checkbox_tooltip
                                        ),
                                        expansive_info=FileTypeSettingPropertySetting(
                                            enabled=True,
                                            change_state_if_enabled=False,
                                            default_on=False,
                                            tooltip=self.default_expansive_info_radiobutton_tooltip
                                        ),
                                    ),
                                    "CSV": FileTypeSetting(
                                        choice_lists=FileTypeSettingPropertySetting(
                                            enabled=False,
                                            change_state_if_enabled=True,
                                            default_on=False,
                                            tooltip=self.always_off_choice_list_tooltip.format(filetype="CSV")
                                        ),
                                        geometry_attributes=FileTypeSettingPropertySetting(
                                            enabled=True,
                                            change_state_if_enabled=True,
                                            default_on=True,
                                            tooltip=self.default_geometry_tooltip
                                        ),
                                        example_assets=FileTypeSettingPropertySetting(
                                            enabled=True,
                                            change_state_if_enabled=False,
                                            default_on=True,
                                            tooltip=self.default_example_checkbox_tooltip
                                        ),
                                        expansive_info=FileTypeSettingPropertySetting(
                                            enabled=True,
                                            change_state_if_enabled=False,
                                            default_on=False,
                                            tooltip=self.default_expansive_info_radiobutton_tooltip
                                        ),
                                    ),
                                    "JSON": FileTypeSetting(
                                        choice_lists=FileTypeSettingPropertySetting(
                                            enabled=False,
                                            change_state_if_enabled=True,
                                            default_on=False,
                                            tooltip=self.always_off_choice_list_tooltip.format(filetype="JSON")
                                        ),
                                        geometry_attributes=FileTypeSettingPropertySetting(
                                            enabled=True,
                                            change_state_if_enabled=True,
                                            default_on=True,
                                            tooltip=self.default_geometry_tooltip
                                        ),
                                        example_assets=FileTypeSettingPropertySetting(
                                            enabled=True,
                                            change_state_if_enabled=False,
                                            default_on=False,
                                            tooltip=self.default_example_checkbox_tooltip
                                        ),
                                        expansive_info=FileTypeSettingPropertySetting(
                                            enabled=True,
                                            change_state_if_enabled=False,
                                            default_on=False,
                                            tooltip=self.default_expansive_info_radiobutton_tooltip
                                        ),
                                    ),
                                    'GeoJSON': FileTypeSetting(
                                        choice_lists=FileTypeSettingPropertySetting(
                                            enabled=False,
                                            change_state_if_enabled=True,
                                            default_on=False,
                                            tooltip=self.always_off_choice_list_tooltip.format(filetype="GeoJSON")
                                        ),
                                        geometry_attributes=FileTypeSettingPropertySetting(
                                            enabled=True,
                                            change_state_if_enabled=True,
                                            default_on=True,
                                            tooltip=self.default_geometry_tooltip
                                        ),
                                        example_assets=FileTypeSettingPropertySetting(
                                            enabled=True,
                                            change_state_if_enabled=False,
                                            default_on=False,
                                            tooltip=self.default_example_checkbox_tooltip
                                        ),
                                        expansive_info=FileTypeSettingPropertySetting(
                                            enabled=True,
                                            change_state_if_enabled=False,
                                            default_on=False,
                                            tooltip=self.default_expansive_info_radiobutton_tooltip
                                        ),
                                    ),
                                    'SDF': FileTypeSetting(
                                        choice_lists=FileTypeSettingPropertySetting(
                                            enabled=False,
                                            change_state_if_enabled=True,
                                            default_on=True,
                                            tooltip=self.always_on_choice_list_tooltip.format(filetype="SDF")
                                        ),
                                        geometry_attributes=FileTypeSettingPropertySetting(
                                            enabled=False,
                                            change_state_if_enabled=True,
                                            default_on=True,
                                            tooltip=self.always_on_geometry_tooltip.format(filetype="SDF")
                                        ),
                                        example_assets=FileTypeSettingPropertySetting(
                                            enabled=False,
                                            change_state_if_enabled=False,
                                            default_on=False,
                                            tooltip=self.always_off_example_checkbox_tooltip.format(filetype="SDF")
                                        ),
                                        expansive_info=FileTypeSettingPropertySetting(
                                            enabled=False,
                                            change_state_if_enabled=False,
                                            default_on=False,
                                            tooltip=self.always_off_expansive_info_radiobutton_tooltip.format(filetype="SDF")
                                        ),
                                    ),
                                    }

        self.template_export_file_picker = TemplateSaveFilePickerDialog(self._)

        self.has_agent = False
        # settings checkboxes and counters
        self.general_settings_title = QLabel()
        self.add_choice_list = QCheckBox()
        self.add_geometry_attributes = QCheckBox()
        self.export_button = ButtonWidget()
        self.export_attribute_info = QCheckBox()
        self.show_deprecated_attributes = QCheckBox()
        self.example_amount_checkbox = QCheckBox()
        self.non_otl_conform_settings_title = QLabel()
        self.amount_of_examples = QSpinBox()
        self.example_settings_title = QLabel()

        # class GUI list elements
        self.select_all_classes = QCheckBox()
        self.add_resetable_field(self.select_all_classes,default_value=True)
        self.all_classes = ClassListWidget()
        self.selected = 0
        self.label_counter = QLabel()

        # radio button for DAVIE conformity or extra info
        self.template_format_label = QLabel()
        self.radio_button_group = QButtonGroup()
        self.radio_button_davie_conform = QRadioButton()
        self.add_resetable_field(self.radio_button_davie_conform,True)
        self.radio_button_expanded_info = QRadioButton()
        self.add_resetable_field(self.radio_button_expanded_info, False)


        self.init_ui()
        self.update_settings_based_on_filetype(self.file_extension_selection.currentText())

    def init_ui(self) -> None:
        """
        Initializes the user interface layout for the template screen.

        This function sets up the main layout by adding spacing, a template menu widget
         and adjusting the layout's margins.
         It ensures that the user interface is properly structured and visually appealing.

        :param self: The instance of the class.
        :return: None
        """

        self.main_layout.addSpacing(10)
        self.main_layout.addWidget(self.template_menu())
        # self.main_layout.addStretch()
        self.main_layout.addSpacing(10)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)


    def options_menu(self) -> QFrame:
        """
        Creates and configures the options menu for the user interface.

        This function builds the options menu by adding various settings and controls,
        such as checkboxes and buttons, to the layout. It sets properties and connects signals
        to ensure that user interactions are handled appropriately.

        :param self: The instance of the class.
        :return: QFrame -- The configured options menu as a QFrame widget.
        """

        options_menu = QFrame()
        main_layout = QVBoxLayout()


        self.general_settings_title.setProperty('class', 'settings-title')
        self.general_settings_title.setText(self._("general_settings"))

        self.add_choice_list.setText(self._("choice_list"))
        self.add_choice_list.setProperty('class', 'settings-checkbox')

        self.add_geometry_attributes.setText(self._("geometry_attributes"))
        self.add_geometry_attributes.setProperty('class', 'settings-checkbox')
        self.add_geometry_attributes.setChecked(True)

        self.non_otl_conform_settings_title.setText(self._("add_non_otl_conform_information"))
        self.non_otl_conform_settings_title.setProperty('class', 'settings-title')

        self.show_deprecated_attributes.setText(self._("show_deprecated_attributes"))
        self.show_deprecated_attributes.setProperty('class', 'settings-checkbox')
        self.show_deprecated_attributes.setEnabled(False)

        self.export_attribute_info.setText(self._("export_attribute_info"))
        self.export_attribute_info.setProperty('class', 'settings-checkbox')

        self.example_settings_title.setProperty('class', 'settings-title')
        self.example_settings_title.setText(self._("example_settings"))

        self.export_button.setText(self._("export"))
        self.export_button.setProperty('class', 'primary-button')
        self.export_button.clicked.connect(lambda: self.export_template_listener())

        # build main layout
        main_layout.addWidget(self.create_filetype_combobox())
        main_layout.addWidget(self.create_radio_button_box())
        main_layout.addSpacing(10)

        main_layout.addWidget(self.add_choice_list)
        main_layout.addWidget(self.add_geometry_attributes)
        main_layout.addWidget(self.create_example_generation_container())
        main_layout.addSpacing(10)
        main_layout.addWidget(self.export_button, alignment=Qt.AlignmentFlag.AlignLeft)

        main_layout.addStretch()

        options_menu.setLayout(main_layout)

        return options_menu

    def create_radio_button_box(self) -> QFrame:


        button_box_frame = QFrame()
        button_box_layout = QHBoxLayout()

        # self.template_format_label.setProperty('class', 'settings-checkbox')
        self.template_format_label.setText(self._("Template format") + ":")
        self.template_format_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.radio_button_davie_conform.setText(self._('DAVIE conform'))
        self.radio_button_davie_conform.setToolTip(self._("Generates a template that is ready for upload to DAVIE"))

        self.radio_button_expanded_info.setText(self._('Expanded info'))
        self.radio_button_expanded_info.setToolTip(self.default_expansive_info_radiobutton_tooltip)

        self.radio_button_group.addButton(self.radio_button_davie_conform, self.TemplateOptionId.DAVIE_CONFORM)
        # self.button_group.setId(self.radio_button_export_all_data,
        #                         self.ExportOptionId.ALL_DATA)

        self.radio_button_group.addButton(self.radio_button_expanded_info, self.TemplateOptionId.EXTRA_INFO)

        self.radio_button_davie_conform.setChecked(True)

        button_box_layout.addWidget(self.template_format_label)
        button_box_layout.addStretch()
        button_box_layout.addWidget(self.radio_button_davie_conform)
        button_box_layout.addStretch()
        button_box_layout.addWidget(self.radio_button_expanded_info)
        button_box_layout.addStretch()

        button_box_layout.setContentsMargins(0,0,0,0)
        button_box_frame.setLayout(button_box_layout)


        return button_box_frame

    # def on_radio_button_click(self,id:int):
    #     if id == self.TemplateOptionId.DAVIE_CONFORM:
    #         OTLLogger.logger.debug("Generate DAVIE conform templates")
    #     elif id == self.TemplateOptionId.ONLY_UNEDITED_DATA:
    #         OTLLogger.logger.debug("Generate extra information templates")

    def create_example_generation_container(self) -> QFrame:
        """
        Creates a container for example generation settings.

        This function initializes a QFrame that contains a label and a spin box for specifying the
        amount of examples to generate. It sets the appropriate properties and layout to ensure a
        user-friendly interface.

        :param self: The instance of the class.
        :return: QFrame -- The configured example generation container.
        """

        example_generation_container = QFrame()
        example_box_layout = QHBoxLayout()
        self.example_amount_checkbox.setText(self._("amount_of_examples"))
        self.example_amount_checkbox.setToolTip(self.default_example_checkbox_tooltip)
        # self.example_amount_label.setProperty('class', 'settings-label')
        self.amount_of_examples.setRange(1, 100)
        self.amount_of_examples.setValue(1)
        self.amount_of_examples.setToolTip(self._("The amount of example assets added to each OTL-class"))
        example_box_layout.addWidget(self.example_amount_checkbox)
        example_box_layout.addWidget(self.amount_of_examples)
        example_box_layout.setContentsMargins(0,0,0,0)

        example_generation_container.setLayout(example_box_layout)
        example_generation_container.setProperty('class', 'settings-checkbox')

        return example_generation_container


    def template_menu(self) -> QWidget:
        """
        Constructs the template menu for the user interface.

        This function creates a QWidget that serves as the main container for the template menu,
        including a title, options menu, and a list. It organizes these components using horizontal
        and vertical layouts to ensure a structured and visually appealing interface.

        :param self: The instance of the class.
        :return: QWidget -- The constructed template menu as a QWidget.
        """

        full_window = QWidget()
        full_window.setProperty('class', 'background-box')
        horizontal_layout = QHBoxLayout()
        window = QFrame()
        layout = QVBoxLayout()
        layout.addWidget(self.subset_title_and_button())
        layout.addWidget(self.options_menu())
        layout.setContentsMargins(16, 0, 16, 0)
        window.setLayout(layout)
        horizontal_layout.addWidget(window,stretch=1)
        horizontal_layout.addWidget(self.create_list(),stretch=2)
        horizontal_layout.addSpacing(20)
        full_window.setLayout(horizontal_layout)


        return full_window


    def subset_title_and_button(self) -> QFrame:
        """
        Creates a frame containing subset information and a button.

        This function constructs a QFrame that includes a list of subset information and a button
        to change the subset. It organizes these components in a horizontal layout, ensuring that
        the button is aligned to the right for a clean user interface.

        :param self: The instance of the class.
        :return: QFrame -- The constructed frame with subset information and button.
        """

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
        """
        Constructs a field displaying operator information.

        This function creates a QFrame that contains a label for the operator and an input field
        for the operator's name. It organizes these components in a horizontal layout, ensuring
        that the label is clearly associated with the input field.

        :param self: The instance of the class.
        :return: QFrame -- The constructed frame with operator information.
        """

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
        """
        Constructs a field for displaying the OTL version information.

        This function creates a QFrame that contains a label for the OTL version and an input field
        for displaying the version. It arranges these components in a horizontal layout, ensuring
        that the label is clearly associated with the version input field.

        :param self: The instance of the class.
        :return: QFrame -- The constructed frame with OTL version information.
        """

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
        """
        Constructs a field for entering the subset name.

        This function creates a QFrame that includes a label for the subset and an input field for
        entering the subset name. It organizes these components in a horizontal layout, ensuring
        that the label is clearly associated with the input field.

        :param self: The instance of the class.
        :return: QFrame -- The constructed frame for the subset name input.
        """

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
        """Constructs a frame containing information fields for subsets.

        This function creates a QFrame that includes various input fields related to subsets,
        such as the subset name, operator information, and OTL version. It organizes these
        components in a vertical layout to provide a clear and structured user interface.

        :param self: The instance of the class.
        :return: QFrame -- The constructed frame containing subset information fields.
        """

        frame = QFrame()
        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.create_subset_name_field())
        vertical_layout.addWidget(self.create_operator_info_field())
        vertical_layout.addWidget(self.create_otl_version_field())
        frame.setLayout(vertical_layout)
        return frame


    def create_list(self) -> QFrame:
        """
        Constructs a list interface for selecting classes.

        This function creates a QFrame that contains a checkbox for selecting all classes, a list
        widget for displaying available classes, and a label that shows the count of selected
        classes. It sets up the necessary connections to handle user interactions and updates the
        display accordingly.

        :param self: The instance of the class.
        :return: QFrame -- The constructed frame containing the class selection interface.
        """

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
        """Updates the project information displayed in the user interface.

        This function retrieves the current subset name, operator name, and OTL version from the
        project and updates the corresponding UI fields. If the project data cannot be found,
        it sets the fields to default values to indicate the absence of information.

        :param self: The instance of the class.
        :param project: the new project to which the information needs to be updated to
        :return: None
        :raises FileNotFoundError: If the project data cannot be accessed.
        """
        if project:
            try:
                # model_builder = ModelBuilder(self.project.subset_path)
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

    def class_items_clicked_listener(self, selected_item):
        row_index = selected_item.data(1)[1]
        TemplateDomain.toggle_class_index(row_index)




    def update_label_under_list(self,total_amount_of_items:int,counter:int) -> None:

        self.selected = counter
        self.label_counter.setText(self._("{selected} classes selected").format(selected=self.selected))
        if counter:
            self.export_button.setEnabled(True)
            self.export_button.setToolTip(self._("Export template"))
        else:
            self.export_button.setEnabled(False)
            self.export_button.setToolTip(self._("Select at least 1 class to export"))

    def update_all_classes_selected(self,state:bool) -> None:
        self.select_all_classes.setChecked(state)

    def count_selected_items(self):
        return sum(
            1
            for i in range(self.all_classes.count())
            if self.all_classes.item(i).isSelected()
        )



    def select_all_classes_clicked(self):
        """
        Handles the selection of all classes based on the checkbox state.

        This function checks if the "select all classes" checkbox is checked and, if so, selects 
        all items in the class list. If the checkbox is unchecked, it clears the selection. 
        The function does nothing if the class list is disabled.

        :param self: The instance of the class.
        :return: None
        """

        if not self.all_classes.isEnabled():
            return
        # elif self.select_all_classes.isChecked():
        #     TemplateDomain.select_all_classes()
        #
        #     # self.all_classes.selectAll()
        # else:
        #     TemplateDomain.deselect_all_classes()

        TemplateDomain.set_select_all_classes(self.select_all_classes.isChecked())

    def deselect_all_classes(self) -> None:
        self.all_classes.clearSelection()


    def set_all_classes_selected(self) -> None:
        self.all_classes.selectAll()

    def export_template_listener(self) -> None:  # sourcery skip: use-named-expression
        """
        Handles the export of a template based on selected classes.
        Handles the export of a template based on selected classes.

        This function retrieves the selected classes from the user interface and prompts the user 
        to choose a file location for the export. If a valid file path is provided, it calls the 
        export function with the necessary parameters, including user preferences for the 
        export options.

        :param self: The instance of the class.
        :return: None
        """

        chosen_file_format = self.file_extension_selection.currentText()
        if chosen_file_format in self.supported_export_formats:
            selection_path_list = self.template_export_file_picker.summon(
                chosen_file_format=chosen_file_format,
                supported_export_formats=self.supported_export_formats,
                project_name=global_vars.current_project.eigen_referentie)
            try:
                self.save_template(selection_path_list)
            except Exception as e:
                # TODO: proper error message when template export fails
                raise e

    def save_template(self, document_paths:list[Path]):

        if not document_paths or not document_paths[0]:
            return
        document_path = document_paths[0]

        checked_radio_button_id = self.radio_button_group.checkedId()
        if checked_radio_button_id == self.TemplateOptionId.DAVIE_CONFORM:
            attribute_description = False
            deprecated_attribute_marker = False
        else:
            attribute_description = True
            deprecated_attribute_marker = True

        if self.example_amount_checkbox.isChecked():
            amount_of_examples = self.amount_of_examples.value()
        else:
            amount_of_examples = 0

        create_task_reraise_exception(TemplateDomain.async_export_template(
            document_path=document_path,
            generate_choice_list=self.add_choice_list.isChecked(),
            geometry_column_added=self.add_geometry_attributes.isChecked(),
            export_attribute_info=attribute_description,
            highlight_deprecated_attributes=deprecated_attribute_marker,
            amount_of_examples=amount_of_examples))


    def update_settings_based_on_filetype(self,filetype:str):
        # if filetype == "Excel":

        self.add_choice_list.setChecked(self.file_type_settings[filetype].choice_lists.default_on)
        self.add_choice_list.setEnabled(self.file_type_settings[filetype].choice_lists.enabled)
        self.add_choice_list.setToolTip(self.file_type_settings[filetype].choice_lists.tooltip)

        self.example_amount_checkbox.setChecked(self.file_type_settings[filetype].example_assets.default_on)
        self.example_amount_checkbox.setEnabled(self.file_type_settings[filetype].example_assets.enabled)
        self.example_amount_checkbox.setToolTip(self.file_type_settings[filetype].example_assets.tooltip)

        self.add_geometry_attributes.setChecked(self.file_type_settings[filetype].geometry_attributes.default_on)
        self.add_geometry_attributes.setEnabled(self.file_type_settings[filetype].geometry_attributes.enabled)
        self.add_geometry_attributes.setToolTip(self.file_type_settings[filetype].geometry_attributes.tooltip)

        if ((not self.file_type_settings[filetype].expansive_info.enabled) and
            self.radio_button_expanded_info.isChecked()):
            self.radio_button_expanded_info.setChecked(False)
            self.radio_button_davie_conform.setChecked(True)

        self.radio_button_expanded_info.setEnabled(self.file_type_settings[filetype].expansive_info.enabled)
        self.radio_button_expanded_info.setToolTip(self.file_type_settings[filetype].expansive_info.tooltip)


            # self.add_choice_list.setChecked(True)
            # self.add_choice_list.setEnabled(True)
            # self.add_choice_list.setToolTip(
            #     self._("Adds choice lists to relevant attributes").format(filetype=filetype))
            #
            # self.add_geometry_attributes.setChecked(True)
            # self.add_geometry_attributes.setEnabled(True)
            # self.add_geometry_attributes.setToolTip(
            #     self._("Adds geometry information for each asset"))
        # elif filetype == 'CSV':
        #     self.add_choice_list.setChecked(False)
        #     self.add_choice_list.setEnabled(False)
        #     self.add_choice_list.setToolTip(self._("{filetype} cannot contain choice lists").format(filetype=filetype))
        #
        #     self.add_geometry_attributes.setChecked(True)
        #     self.add_geometry_attributes.setEnabled(True)
        #     self.add_geometry_attributes.setToolTip(
        #         self._("Adds geometry information for each asset"))
        # elif filetype == 'JSON':
        #     self.add_choice_list.setChecked(False)
        #     self.add_choice_list.setEnabled(False)
        #     self.add_choice_list.setToolTip(self._("{filetype} cannot contain choice lists").format(filetype=filetype))
        #
        #     self.add_geometry_attributes.setChecked(True)
        #     self.add_geometry_attributes.setEnabled(True)
        #     self.add_geometry_attributes.setToolTip(
        #         self._("Adds geometry information for each asset"))
        # elif filetype == 'GeoJSON':
        #     self.add_choice_list.setChecked(False)
        #     self.add_choice_list.setEnabled(False)
        #     self.add_choice_list.setToolTip(self._("{filetype} cannot contain choice lists").format(filetype=filetype))
        #
        #     self.add_geometry_attributes.setChecked(True)
        # elif filetype == 'SDF':
        #     self.add_choice_list.setChecked(True)
        #     self.add_choice_list.setEnabled(False)
        #     self.add_choice_list.setToolTip(self._("For {filetype} choice lists cannot be disabled").format(filetype=filetype))
        #
        #     self.add_geometry_attributes.setChecked(True)
        #     self.add_geometry_attributes.setEnabled(False)
        #     self.add_choice_list.setToolTip(self._("For {filetype} geometry attributes cannot be disabled").format(filetype=filetype))
    def change_subset(self) -> None:
        """
        Opens a window to change the current subset.

        This function initializes and displays the ChangeSubsetWindow, allowing the user to modify 
        the current subset settings. It provides a user interface for selecting and applying 
        changes to the subset.

        :param self: The instance of the class.
        :return: None
        """

        ChangeSubsetWindow(self._)


    def reset_ui(self, _) -> None:
        super().reset_ui(_)
        self.update_settings_based_on_filetype(self.file_extension_selection.currentText())
        self._ = _

            
        # self.export_attribute_info.setText(self._("export_attribute_info"))
        # self.add_geometry_attributes.setText(self._("geometry_column_added"))
        # self.add_choice_list.setText(self._("choice_list"))
        # self.select_all_classes.setText(self._("select_all_classes"))
        # self.example_amount_checkbox.setText(self._("amount_of_examples"))
        # self.export_button.setText(self._("export"))
        # self.change_subset_btn.setText(self._("change_subset"))
        # self.operator_title.setText(self._("operator") + ":")
        # self.otl_title.setText(self._("otl_version") + ":")
        # self.general_settings_title.setText(self._("general_settings"))
        # self.example_settings_title.setText(self._("example_settings"))
        # self.non_otl_conform_settings_title.setText(self._("deprecated_settings"))
        # self.label_counter.setText(self._("{selected} classes selected").format(selected=self.selected))


    def set_gui_list_to_loading_state(self) -> None:
        """Sets the GUI list to a loading state.

        This function updates the list of classes in the user interface to indicate that loading is in progress. It clears the current items in the list and adds a single item displaying the text "loading" to inform the user of the ongoing operation.

        :param self: The instance of the class.
        :return: None
        """

        item = QListWidgetItem()
        item.setText(self._("loading"))
        self.all_classes.clear()
        self.all_classes.addItem(item)


    def set_gui_list_to_no_classes_found(self) -> None:
        """
        Updates the GUI list to indicate that no classes were found.

        This function disables the class list in the user interface and adds a message indicating
        that no classes were found in the specified path. It provides feedback to the user when
        the expected data is not available.

        :param self: The instance of the class.
        :return: None
        """

        self.all_classes.setEnabled(False)
        self.all_classes.addItem(self._("no classes found in specified path"))


    def set_classes(self, classes: list[OSLOClass],
                    selected_classes: list[int],
                    all_classes_selected_checked:bool,
                    has_a_class_with_deprecated_attributes: bool) -> None:
        """
        Sets the list of classes in the user interface.

        This function clears the existing items in the class list and populates it with new items
        based on the provided list of OSLOClass instances. It also enables or disables the display
        of deprecated attributes based on the provided flag.

        :param self: The instance of the class.
        :param classes: A list of OSLOClass instances to be displayed in the class list.
        :type classes: list[OSLOClass]
        :param has_a_class_with_deprecated_attributes: A flag indicating whether to show deprecated attributes.
        :type has_a_class_with_deprecated_attributes: bool
        :return: None
        """

        self.all_classes.clear()
        self.all_classes.setEnabled(True)
        self.has_agent = False

        # store indexes for class list in backend before sorting!
        class_index_tuple_list = [(OTL_class,i) for i,OTL_class in enumerate(classes)]
        sorted_classes = sorted(class_index_tuple_list,key=lambda x : x[0].name)

        for value_tuple in sorted_classes:
            class_name = value_tuple[0].name
            class_typeURI = value_tuple[0].objectUri
            backend_index = value_tuple[1]

            item = QListWidgetItem()
            item.setText(class_name)
            item.setData(1, (class_typeURI,backend_index))



            if class_name == "Agent":
                item.setBackground(QBrush(QColor("#AAAAAA")))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
                placeholder_font = QFont()
                placeholder_font.setItalic(True)
                item.setFont(placeholder_font)
                item.setToolTip(self._('Agent class is not allowed in the template'))
                self.has_agent = True


            self.all_classes.addItem(item)

        if has_a_class_with_deprecated_attributes:
            self.show_deprecated_attributes.setEnabled(False)

        if all_classes_selected_checked:
            self.set_all_classes_selected()
        else:
            self.update_all_classes_selected(False)
            # the need to be added to cls.all_classes before you can select them
            for class_display_index in range(self.all_classes.count()):
                item = self.all_classes.item(class_display_index)
                real_index = item.data(1)[1]

                if real_index in selected_classes:
                    item.setSelected(True)

        self.update_label_under_list(
            total_amount_of_items=TemplateDomain.get_total_amount_of_classes(),
            counter=len(selected_classes))


    def create_filetype_combobox(self) -> QFrame:
        """
        Creates a combo box for selecting the file type for export. This method sets up the layout,
        adds a label and a combo box populated with supported file formats, and connects the c
        ombo box's change event to a method for displaying additional options.

        :return: A QFrame containing the combo box for file type selection.
        :rtype: QFrame
        """

        frame = QFrame()
        frame_layout = QHBoxLayout()

        self.file_type_label.setText(self._('select file type for export') + ":")

        self.file_extension_selection.addItems(list(self.supported_export_formats.keys()))
        self.file_extension_selection.currentTextChanged.connect(self.update_settings_based_on_filetype)
        self.file_extension_selection.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Fixed))

        frame_layout.addWidget(self.file_type_label)
        frame_layout.addWidget(self.file_extension_selection)
        frame_layout.setContentsMargins(0,0,0,0)
        frame.setLayout(frame_layout)
        frame.setToolTip(self._("The type of file the template will be created in"))

        return frame

    def open_folder_of_created_template(self,document_path:Path):
        Helpers.open_folder_and_select_document(document_path=document_path)
