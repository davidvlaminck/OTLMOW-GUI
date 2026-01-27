import traceback
from pathlib import Path

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QVBoxLayout, QWidget, QLabel, QPushButton, QFrame, QHBoxLayout, \
    QListWidget, \
    QListWidgetItem, QTreeWidget, QTreeWidgetItem, QHeaderView, QSizePolicy

from otlmow_gui.Domain.logger.OTLLogger import OTLLogger
from otlmow_converter.Exceptions.ExceptionsGroup import ExceptionsGroup
from otlmow_model.OtlmowModel.Helpers.OTLObjectHelper import count_assets_by_type

from otlmow_gui.Domain import global_vars
from otlmow_gui.Domain.enums import FileState
from otlmow_gui.Domain.step_domain.InsertDataDomain import InsertDataDomain
from otlmow_gui.GUI.dialog_windows.NotificationWindow import NotificationWindow
from otlmow_gui.GUI.dialog_windows.file_picker_dialog.LoadFilePickerDialog import LoadFilePickerDialog
from otlmow_gui.GUI.screens.general_elements.ButtonWidget import ButtonWidget
from otlmow_gui.GUI.dialog_windows.RemoveProjectFilesWindow import RemoveProjectFilesWindow
from otlmow_gui.GUI.dialog_windows.RevalidateDocumentsWindow import RevalidateDocumentsWindow
from otlmow_gui.GUI.screens.Screen import Screen
import qtawesome as qta

from otlmow_gui.GUI.translation.ValidationErrorReportTranslations import ValidationErrorReportTranslations
from otlmow_gui.exception_handler.ExceptionHandlers import create_task_reraise_exception


class InsertDataScreen(Screen):
    """
    Represents the screen for inserting and validating documents with objects.

    This class manages the user interface for inserting data, including 
    file selection, validation, and feedback display. It provides methods 
    for interacting with project files and displaying relevant messages to 
    the user.

    Args:
        language_settings (optional): Language settings for the user interface.

    Attributes:
        container_insert_data_screen (QVBoxLayout): Layout for the insert data screen.
        message_icon (QLabel): Label for displaying message icons.
        message (QLabel): Label for displaying messages to the user.
        input_file_label (QLabel): Label for the input file section.
        project_files_overview_field (QTreeWidget): Widget for displaying project files.
        feedback_message_box (QFrame): Frame for displaying feedback messages.
        asset_info (QListWidget): List widget for displaying asset information.
        input_file_button (ButtonWidget): Button for selecting input files.
        control_button (ButtonWidget): Button for controlling data processing.
        reset_button (ButtonWidget): Button for resetting the input fields.
        assets (list): List to store asset information.
        main_window (optional): Reference to the main application window.
    """
    feedback_message_icon_color = "white"

    def __init__(self, language_settings=None):
        super().__init__()
        self._ = language_settings

        self.load_file_dialog_window = LoadFilePickerDialog(self._)

        self.container_insert_data_screen = QVBoxLayout()

        self.message_icon = QLabel()
        self.message = QLabel()
        self.input_file_label = QLabel()

        self.project_files_overview_field: QTreeWidget = QTreeWidget()
        self.feedback_message_box = QFrame()
        self.asset_info = QListWidget()

        self.input_file_button = ButtonWidget()
        self.control_button = ButtonWidget()
        self.reset_button = ButtonWidget()

        self.assets = []
        self.main_window = None

        self.init_ui()


    def init_ui(self) -> None:
        """
        Sets up the user interface for the insert data screen.

        This method configures the layout by adding spacing and a menu to the
        insert data screen. It ensures that the UI elements are properly aligned
        and displayed within the designated container.

        :param self: The instance of the class.
        :returns: None
        """

        self.container_insert_data_screen.addSpacing(10)
        self.container_insert_data_screen.addWidget(self.create_menu())
        self.container_insert_data_screen.addSpacing(10)
        self.container_insert_data_screen.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.container_insert_data_screen)


    def create_menu(self) -> QWidget:  # sourcery skip: class-extract-method
        """
        Creates a menu layout for the insert data screen.

        This method constructs a QWidget that serves as a menu, organizing
        its components into a horizontal layout. It includes left and right
        sections that expand to fill available space, ensuring a responsive
        design.

        :param self: The instance of the class.
        :returns: QWidget -- The constructed menu widget.
        """

        window = QWidget()
        window.setProperty('class', 'background-box')
        window_layout = QHBoxLayout()

        left_side = self.left_side()
        left_side.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Expanding )

        right_side = self.right_side()
        right_side.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Expanding )

        window_layout.setContentsMargins(32, 0, 16, 0)
        window_layout.addWidget(left_side)
        window_layout.addWidget(right_side)

        window.setLayout(window_layout)

        return window


    def button_set(self) -> QFrame:
        """
        Creates and configures a frame containing control buttons.

        This method sets up a button frame with three buttons: a control button,
        a reset button, and a file selection button. Each button is configured
        with appropriate text, properties, and click event handlers to manage
        user interactions.

        :param self: The instance of the class.
        :returns: QFrame -- The configured button frame containing the buttons.
        """

        button_frame = QFrame()
        button_frame_layout = QHBoxLayout()

        self.control_button.setText(self._('control_button'))
        self.control_button.setDisabled(True)
        self.control_button.clicked.connect(lambda: self.try_to_validate_documents())
        self.control_button.setProperty('class', 'primary-button')

        reset_button = QPushButton()
        reset_button.setText(self._('reset_fields'))
        reset_button.setProperty('class', 'secondary-button')
        # noinspection PyUnresolvedReferences
        reset_button.clicked.connect(lambda: self.reset_button_functionality())

        self.input_file_button.setText(self._('choose_file'))
        self.input_file_button.setProperty('class', 'primary-button')
        self.input_file_button.clicked.connect(lambda: self.open_file_picker())

        button_frame_layout.addWidget(self.input_file_button)
        button_frame_layout.addStretch()
        button_frame_layout.addWidget(self.control_button)
        button_frame_layout.addWidget(reset_button)
        button_frame_layout.setContentsMargins(11, 11, 11, 0)

        button_frame.setLayout(button_frame_layout)

        self.warning_feedback_message()
        self.clear_feedback_message()

        return button_frame


    def try_to_validate_documents(self) -> None:
        """
        Attempts to validate documents and handle potential overwrites.

        This method checks if there is a recent quick save for the current project.
        If a quick save exists, it prompts the user with a warning about overwriting
        previous changes; otherwise, it proceeds to validate the documents.

        :param self: The instance of the class.
        :returns: None
        """

        # if there is a quick_save warns the user that they are overwriting the previous changes
        if global_vars.current_project.get_last_quick_save_path():
            RevalidateDocumentsWindow(self,self._)
        else:
            missing_project_files = InsertDataDomain.check_current_project_project_files_existence()
            if len(missing_project_files):
                self.show_missing_project_files_notification_window(missing_project_files)
                return

            create_task_reraise_exception(self.validate_documents())

    def show_missing_project_files_notification_window(self, missing_project_files):
        message = self._(
            "There are files missing.\nRemove these from the list and re-insert them:\n")
        for project_file in missing_project_files:
            filename = project_file.file_path.name
            message += f"   -{filename}\n"
        msgbox = NotificationWindow(message=message, title=self._("Missing project files"))
        msgbox.exec()

    async def validate_documents(self) -> None:
        """
        Validates documents and provides user feedback based on the results.

        This method clears any previous feedback and then attempts to load and
        validate the documents. Depending on whether errors are found, it
        provides appropriate feedback to the user and updates the UI accordingly.

        :param self: The instance of the class.
        :returns: None
        """

        self.clear_feedback()

        error_set, objects_list = await InsertDataDomain.load_and_validate_documents()
        self.asset_info.clear()
        if error_set:
            OTLLogger.logger.debug('negative feedback needed')
            self.negative_feedback_message()
            self.fill_error_feedback_list(error_set=error_set)
        else:
            OTLLogger.logger.debug('positive feedback needed')
            self.main_window.reset_ui(self._)
            self.positive_feedback_message()

        self.fill_feedback_list(objects_list)


    def fill_error_feedback_list(self, error_set: list[dict]):
        """Processes a set of errors and populates the feedback list.

        This method iterates through the provided error set, extracting exceptions
        and their associated document paths. It adds each error to the feedback
        list, handling both individual exceptions and groups of exceptions.

        Args:
            self: The instance of the class.
            error_set (list): A list of error items, each containing an exception
                              and a document path.

        Returns:
            None
        """



        for item in error_set:
            exception = item["exception"]
            doc = item["path_str"]

            if isinstance(exception, ExceptionsGroup):
                for ex in exception.exceptions:
                    self.add_error_to_feedback_list(ex, doc)
            else:
                self.add_error_to_feedback_list(exception, doc)


    def add_input_file_field(self) -> QFrame:
        """
        Creates and configures a frame for displaying project files.

        This method sets up a QFrame that contains a layout for displaying
        project files in a table format. It configures the table's column
        count, size policy, and header properties to ensure a user-friendly
        interface.

        Args:
            self: The instance of the class.

        Returns:
            QFrame: The configured frame containing the project files overview field.
        """

        input_file_frame = QFrame()
        input_file_layout = QHBoxLayout()

        self.project_files_overview_field.setColumnCount(3)
        self.project_files_overview_field.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Expanding )

        header = self.project_files_overview_field.header()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setStretchLastSection(False)
        self.project_files_overview_field.setHeaderHidden(True)

        input_file_layout.addWidget(self.project_files_overview_field)

        input_file_frame.setLayout(input_file_layout)

        return input_file_frame


    def left_side(self) -> QFrame:
        """
        Constructs the left side layout of the insert data screen.

        This method creates a QFrame that organizes various UI components
        vertically, including an input file label, input file field,
        control buttons, and a feedback message. It ensures proper spacing
        and layout for a cohesive user interface.

        Args:
            self: The instance of the class.

        Returns:
            QFrame: The configured frame representing the left side of the screen.
        """

        left_side = QFrame()
        left_side_layout = QVBoxLayout()
        left_side_layout.addSpacing(10)

        self.input_file_label.setText(self._('input_file'))

        left_side_layout.addWidget(self.input_file_label)
        left_side_layout.addWidget(self.add_input_file_field())
        left_side_layout.addWidget(self.button_set(),alignment=Qt.AlignmentFlag.AlignBottom)
        left_side_layout.addSpacing(10)
        left_side_layout.setStretch(2, 1)


        left_side.setLayout(left_side_layout)
        return left_side


    def right_side(self) -> QFrame:
        """
        Constructs the right side layout of the insert data screen.

        This method creates a QFrame that organizes various UI components
        vertically, including a list and a feedback message box. It ensures
        proper spacing and layout for a cohesive user interface.

        Args:
            self: The instance of the class.

        Returns:
            QFrame: The configured frame representing the right side of the screen.
        """

        right_side = QFrame()
        right_side_layout = QVBoxLayout()

        self.construct_feedback_message()

        right_side_layout.addSpacing(10)
        right_side_layout.addWidget(self.add_list())
        right_side_layout.addWidget(self.feedback_message_box)
        right_side_layout.addSpacing(10)
        right_side_layout.setStretch(1, 1)

        right_side.setLayout(right_side_layout)

        return right_side


    def construct_feedback_message(self) -> None:
        """
        Constructs and configures the feedback message display.

        This method sets up the layout for the feedback message box,
        including an icon and the message itself. It ensures that the
        message is styled appropriately for user visibility.

        Args:
            self: The instance of the class.

        Returns:
            None
        """

        OTLLogger.logger.debug("constructing feedback message")
        frame_layout = QHBoxLayout()

        self.message.setProperty('class', 'feedback-message')

        frame_layout.addWidget(self.message_icon)
        frame_layout.addWidget(self.message)

        self.feedback_message_box.setLayout(frame_layout)


    @classmethod
    def construct_dummy_feedback_message(cls) -> QFrame:
        """Creates a dummy feedback message display.

        This method constructs a QFrame that contains a placeholder for a
        feedback message. It sets up the layout to ensure that the dummy
        message is displayed correctly within the user interface.

        Args:
            cls: this class

        Returns:
            QFrame: The configured frame containing the dummy feedback message.
        """

        dummy_feedback = QFrame()
        frame_layout = QHBoxLayout()

        dummy_message = QLabel()
        dummy_message.setProperty('class', 'feedback-message')

        frame_layout.addWidget(QLabel())
        frame_layout.addWidget(dummy_message)

        dummy_feedback.setLayout(frame_layout)

        return dummy_feedback


    def add_list(self) -> QFrame:
        """Creates and configures a frame for displaying asset information.

        This method sets up a QFrame that contains a layout for displaying
        asset information. It ensures that the asset info widget is properly
        sized and positioned within the frame.

        Args:
            self: The instance of the class.

        Returns:
            QFrame: The configured frame containing the asset information.
        """

        frame = QFrame()
        frame_layout = QHBoxLayout()

        self.asset_info.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Expanding)

        frame_layout.addWidget(self.asset_info)
        frame_layout.setContentsMargins(0, 30, 0, 85)

        frame.setLayout(frame_layout)

        return frame


    def positive_feedback_message(self) -> None:
        """
        Displays a positive feedback message to the user.

        This method updates the feedback message box to indicate that all
        information is correct. It sets an appropriate icon, message text,
        and styles the message box for visual clarity.

        Args:
            self: The instance of the class.

        Returns:
            None
        """
        self.message_icon.setVisible(True)
        self.message_icon.setPixmap(qta.icon(
            'mdi.check',
            color=InsertDataScreen.feedback_message_icon_color).pixmap(QSize(48, 48)))
        self.message.setText(self._('all_info_correct'))
        self.feedback_message_box.setStyleSheet('background-color: #1DCA94; border-radius: 10px;')


    def warning_feedback_message(self) -> None:
        """
        Displays a warning feedback message to the user.

        This method updates the feedback message box to indicate a warning condition.
        It sets an appropriate icon, message text, and styles the message box to visually alert
        the user.

        Args:
            self: The instance of the class.

        Returns:
            None
        """
        self.message_icon.setVisible(True)
        self.message_icon.setPixmap(qta.icon(
            'mdi.alert',
            color=InsertDataScreen.feedback_message_icon_color).pixmap(QSize(48, 48)))
        self.message.setText(self._('warning'))
        self.feedback_message_box.setStyleSheet('background-color: #F8AA62; border-radius: 10px;')


    def clear_feedback_message(self) -> None:
        """
        Clears the feedback message display.

        This method resets the feedback message box by clearing the message
        text and removing any custom styles. It prepares the UI for new
        feedback messages.

        Args:
            self: The instance of the class.

        Returns:
            None
        """

        self.message.setText('')
        self.message_icon.setVisible(False)
        self.feedback_message_box.setStyleSheet('')



    def negative_feedback_message(self) -> None:
        """
        Displays a negative feedback message to the user.

        This method updates the feedback message box to indicate an error
        condition. It sets an appropriate icon, message text, and styles the
        message box to visually alert the user of the issue.

        Args:
            self: The instance of the class.

        Returns:
            None
        """
        self.message_icon.setVisible(True)
        self.message_icon.setPixmap(qta.icon(
            'mdi.alert-circle-outline',
            color=InsertDataScreen.feedback_message_icon_color).pixmap(QSize(48, 48)))
        self.message.setText(self._('error'))

        self.feedback_message_box.setStyleSheet('background-color: #CC3300; border-radius: 10px;')


    def reset_ui(self, language) -> None:
        super().reset_ui(self._)
        self._ = language
        self.input_file_label.setText(self._('input_file'))
        self.control_button.setText(self._('control_button'))
        self.clear_feedback()
        self.update_file_list()


    def open_file_picker(self) -> None:
        """
        Opens a file picker dialog for selecting files.

        This method initializes and displays a file picker dialog, allowing
        the user to select one or more files from their system. It sets the
        dialog's title, directory, and file filters based on supported file
        formats, and processes the selected files upon confirmation.

        Args:
            self: The instance of the class.

        Returns:
            None
        """

        selected_file_path_list = self.load_file_dialog_window.summon()

        if selected_file_path_list:
            try:
                InsertDataDomain.add_files_to_backend_list(files=selected_file_path_list)
            except Exception as e:
                # TODO: proper error message when file fails to be added to project
                raise e
            self.clear_feedback()


    def add_file_to_frontend_list(self,
                                  file: str,
                                  asset_state: FileState = FileState.WARNING) -> None:
        """Adds a file to the frontend list with a specified asset state.

        This method creates a new list item in the project files overview field
        for the specified file, setting its display name and icon based on the
        provided asset state. It also enables the control button and adds a
        delete button next to the list item for user interaction.

        Args:
            self: The instance of the class.
            file (str): The path of the file to be added to the list.
            asset_state (FileState, optional): The state of the asset, which
                                                determines the icon displayed.
                                                Defaults to FileState.WARNING.

        Returns:
            None
        """

        self.control_button.setDisabled(False)

        doc_name = Path(file).name

        list_item = QTreeWidgetItem()
        list_item.setText(1, doc_name)

        if asset_state == FileState.OK:
            list_item.setIcon(0, qta.icon('mdi.check', color="green"))
        elif asset_state == FileState.WARNING:
            list_item.setIcon(0, qta.icon('mdi.alert', color="orange"))
        elif asset_state == FileState.ERROR:
            list_item.setIcon(0, qta.icon('mdi.close', color="red"))

        list_item.setData(1, 1, file)
        list_item.setSizeHint(1, QSize(0, 30))

        button = ButtonWidget()
        button.clicked.connect(self.delete_file_from_list)
        button.setIcon(qta.icon('mdi.close'))

        self.project_files_overview_field.addTopLevelItem(list_item)
        self.project_files_overview_field.setItemWidget(list_item, 2, button)

    def add_file_overview_placeholder_to_front_end_list(self):
        file_place_holder_item = QTreeWidgetItem()
        file_place_holder_item.setText(1, self._("There are no files added to this project"))
        file_place_holder_item.setDisabled(True)


        placeholder_font = QFont()
        placeholder_font.setItalic(True)
        file_place_holder_item.setFont(1,placeholder_font)

        self.project_files_overview_field.addTopLevelItem(file_place_holder_item)




    def add_feedback_placeholder_to_front_end_list(self):
        place_holder_item = QListWidgetItem(
            self._(
                "Press validate to get feedback on the OTL-conformity of the files in this project"))

        placeholder_font = QFont()
        placeholder_font.setItalic(True)

        place_holder_item.setFont(placeholder_font)
        place_holder_item.setForeground(Qt.GlobalColor.gray)

        self.asset_info.addItem(place_holder_item)

    def delete_file_from_list(self) -> None:
        # sourcery skip: use-named-expression
        """
        Deletes the selected file from the project files list.

        This method retrieves the currently selected item in the project files
        overview field and deletes the corresponding file from the backend.
        If no item is selected, no action is taken.

        Args:
            self: The instance of the class.

        Returns:
            None
        """

        items = self.project_files_overview_field.selectedItems()

        if items:
            item_file_path = items[0].data(1,1)
            InsertDataDomain.delete_backend_document(item_file_path=item_file_path)

    def update_file_list(self) -> None:
        """
        Updates the frontend file list to synchronize with the backend.

        This method clears the current file list and synchronizes it with the
        backend documents. It also disables the control button if all documents
        are valid, indicating that no further actions can be taken.

        Args:
            self: The instance of the class.

        Returns:
            None
        """

        OTLLogger.logger.debug("[CLEAR] update_file_list")

        all_valid = InsertDataDomain.update_frontend()

    def update_control_button_state(self):
        self.control_button.setDisabled(self.project_files_overview_field.topLevelItemCount() == 0)

    def reset_button_functionality(self) -> None:
        """
        Resets the project by removing project files.

        This method opens a window to confirm the removal of project files associated with the
        current project and synchronizes the backend documents with the frontend.
        It also clears any existing feedback messages to provide a fresh state.

        Args:
            self: The instance of the class.

        Returns:
            None
        """

        RemoveProjectFilesWindow(project=global_vars.current_project, language_settings=self._)
        InsertDataDomain.update_frontend()
        self.clear_feedback()

    def clear_all(self) -> None:
        """
        Clears all feedback and resets the project files overview field.

        This method removes any feedback messages displayed to the user and
        clears the contents of the project files overview field, providing a
        fresh state for user interaction.

        Args:
            self: The instance of the class.

        Returns:
            None
        """

        self.clear_feedback()
        self.project_files_overview_field.clear()
        self.add_file_overview_placeholder_to_front_end_list()



    def clear_feedback(self) -> None:
        """
        Clears the feedback information displayed to the user.

        This method removes any asset information and resets the feedback
        message display, ensuring that the user interface is free of previous
        feedback.

        Args:
            self: The instance of the class.

        Returns:
            None
        """

        OTLLogger.logger.debug("[CLEAR] clear_feedback")
        self.asset_info.clear()
        self.add_feedback_placeholder_to_front_end_list()
        self.clear_feedback_message()

    def add_error_to_feedback_list(self, exception: Exception, doc: str) -> None:
        """Adds an error message to the feedback list based on the exception type.

        This method constructs a user-friendly error message from the provided
        exception and document name, then adds it to the feedback list. It
        handles various types of errors, formatting the message accordingly,
        and highlights the error in red for visibility.

        Args:
            self: The instance of the class.
            exception (Exception): The exception that occurred, used to determine the error message.
            doc (str): The path of the document associated with the error.

        Returns:
            None
        """

        OTLLogger.logger.debug(str(exception))
        traceback.print_exception(exception)
        doc_name = Path(doc).name
        error_widget = QListWidgetItem()

        error_text = ValidationErrorReportTranslations.translate_exception(doc_name, exception)

        error_widget.setText(error_text)
        self.asset_info.addItem(error_widget)

        item = self.asset_info.findItems(error_text, Qt.MatchFlag.MatchExactly)
        for item in item:
            self.asset_info.item(self.asset_info.row(item)).setForeground(Qt.GlobalColor.red)

    def fill_feedback_list(self, assets: list) -> None:
        """
        µFills the feedback list with asset information based on the provided assets.

        This method processes a list of assets, counting the number of objects
        by type and adding formatted messages to the feedback list. It also
        summarizes the total number of objects loaded that conform to the OTL
        standard.

        Args:
            self: The instance of the class.
            assets (list): A list of assets to be processed. If None, no action is taken.

        Returns:
            None
        """

        total_assets = 0
        if assets is None:
            return

        asset_dict = count_assets_by_type(objects=assets)
        for key, value in asset_dict.items():
            key_split = key.split('#')

            asset_widget = QListWidgetItem()
            asset_widget.setText(f'{value} objecten van het type {key_split[-1]} ingeladen\n')

            total_assets += value

            self.asset_info.addItem(asset_widget)

        asset_widget = QListWidgetItem()
        asset_widget.setText(
            f'In het totaal zijn er {total_assets} objecten ingeladen die conform zijn met de OTL '
            f'standaard\n')

        self.asset_info.addItem(asset_widget)
