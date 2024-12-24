from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame, QCheckBox, QSpinBox, \
    QLabel, QListWidget, QListWidgetItem

from Domain.project.Project import Project
from Domain.step_domain.TemplateDomain import TemplateDomain
from GUI.dialog_windows.ExportToTemplateWindow import ExportToTemplateWindow
from GUI.screens.general_elements.ButtonWidget import ButtonWidget
from GUI.dialog_windows.ChangeSubsetWindow import ChangeSubsetWindow
from GUI.screens.screen_interface.TemplateScreenInterface import TemplateScreenInterface
from LatestReleaseMulti.OTLWizard.data.otlmow_modelbuilder.SQLDataClasses.OSLOClass import \
    OSLOClass


class TemplateScreen(TemplateScreenInterface):
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

        # settings checkboxes and counters
        self.general_settings_title = QLabel()
        self.no_choice_list = QCheckBox()
        self.geometry_column_added = QCheckBox()
        self.export_button = ButtonWidget()
        self.export_attribute_info = QCheckBox()
        self.show_deprecated_attributes = QCheckBox()
        self.example_amount_label = QLabel()
        self.non_otl_conform_settings_title = QLabel()
        self.amount_of_examples = QSpinBox()
        self.example_settings_title = QLabel()

        # class GUI list elements
        self.select_all_classes = QCheckBox()
        self.all_classes = QListWidget()
        self.selected = 0
        self.label_counter = QLabel()

        self.init_ui()


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
        self.main_layout.addStretch()
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
        self.export_button.clicked.connect(lambda: self.export_template_listener())

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
        self.example_amount_label.setText(self._("amount_of_examples"))
        self.example_amount_label.setProperty('class', 'settings-label')
        self.amount_of_examples.setRange(0, 100)
        self.amount_of_examples.setValue(0)
        example_box_layout.addWidget(self.example_amount_label)
        example_box_layout.addWidget(self.amount_of_examples)
        example_generation_container.setLayout(example_box_layout)
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
        horizontal_layout.addWidget(window)
        horizontal_layout.addWidget(self.create_list())
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
        self.select_all_classes.stateChanged.connect(lambda: self.select_all_classes_clicked())
        self.all_classes.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.all_classes.itemSelectionChanged.connect(lambda: self.update_label_under_list())
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

        try:
            # model_builder = ModelBuilder(self.project.subset_path)
            self.subset_name.setText(project.get_subset_db_name())
            self.operator_name.setText(project.get_operator_name())
            self.otl_version.setText(project.get_otl_version())
        except FileNotFoundError as e:
            self.subset_name.setText("/")
            self.operator_name.setText("/")
            self.otl_version.setText("/")


    def update_label_under_list(self):
        counter = sum(
            1
            for i in range(self.all_classes.count())
            if self.all_classes.item(i).isSelected()
        )
        self.selected = counter
        self.label_counter.setText(self._("{selected} classes selected").format(selected=self.selected))


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
        elif self.select_all_classes.isChecked():
            self.all_classes.selectAll()
        else:
            self.all_classes.clearSelection()


    def export_template_listener(self) -> None:  # sourcery skip: use-named-expression
        """
        Handles the export of a template based on selected classes.

        This function retrieves the selected classes from the user interface and prompts the user 
        to choose a file location for the export. If a valid file path is provided, it calls the 
        export function with the necessary parameters, including user preferences for the 
        export options.

        :param self: The instance of the class.
        :return: None
        """
        
        selected_classes = [item.data(1) for item in self.all_classes.selectedItems()]
        file_picker = ExportToTemplateWindow()
        
        document_path_str = file_picker.get_file_location()
        if document_path_str:
            
            document_path = Path(document_path_str)

            TemplateDomain.export_template(
                document_path=document_path,
                selected_classes=selected_classes,
                generate_choice_list=not self.no_choice_list.isChecked(),
                geometry_column_added=self.geometry_column_added.isChecked(),
                export_attribute_info=self.export_attribute_info.isChecked(),
                highlight_deprecated_attributes=self.show_deprecated_attributes.isChecked(),
                amount_of_examples=self.amount_of_examples.value())


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
        self._ = _
        
        TemplateDomain.init_static()
            
        self.export_attribute_info.setText(self._("export_attribute_info"))
        self.geometry_column_added.setText(self._("geometry_column_added"))
        self.no_choice_list.setText(self._("no_choice_list"))
        self.select_all_classes.setText(self._("select_all_classes"))
        self.example_amount_label.setText(self._("amount_of_examples"))
        self.export_button.setText(self._("export"))
        self.change_subset_btn.setText(self._("change_subset"))
        self.operator_title.setText(self._("operator") + ":")
        self.otl_title.setText(self._("otl_version") + ":")
        self.general_settings_title.setText(self._("general_settings"))
        self.example_settings_title.setText(self._("example_settings"))
        self.non_otl_conform_settings_title.setText(self._("deprecated_settings"))
        self.label_counter.setText(self._("{selected} classes selected").format(selected=self.selected))


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

        for value in classes:
            item = QListWidgetItem()
            item.setText(value.name)
            item.setData(1, value.objectUri)
            self.all_classes.addItem(item)
            if has_a_class_with_deprecated_attributes:
                self.show_deprecated_attributes.setEnabled(False)

