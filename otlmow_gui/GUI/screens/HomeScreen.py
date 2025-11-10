
from typing import Optional, Callable

from PyQt6.QtGui import QPixmap
import qtawesome as qta

from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, \
    QLineEdit, QFrame, QPushButton, QSizePolicy
from PyQt6.QtCore import Qt

from otlmow_gui.Domain.ProgramFileStructure import ProgramFileStructure
from otlmow_gui.Domain.project.Project import Project
from otlmow_gui.Domain.step_domain.HomeDomain import HomeDomain
from otlmow_gui.Domain.network.Updater import Updater
from otlmow_gui.GUI.Styling import Styling
from otlmow_gui.GUI.dialog_windows.SuggestUpdateWindow import SuggestUpdateWindow

from otlmow_gui.GUI.header.HeaderBar import HeaderBar
from otlmow_gui.GUI.screens.Home_elements.OverviewTable import OverviewTable, \
    LastAddedProjectHighlightDelegate

from otlmow_gui.GUI.screens.screen_interface.HomeScreenInterface import HomeScreenInterface

IMG_DIR = ProgramFileStructure.get_dynamic_library_path('img')


class HomeScreen(HomeScreenInterface):
    """
    Represents the home screen of the application for managing projects.

    This class provides the user interface for searching and displaying project information,
    including options for exporting data and managing project settings. It integrates various
    UI components such as input fields, buttons, and tables to facilitate user interactions.

    Args:
        language_settings (optional): Language settings for the user interface.

    Attributes:
        project (optional): The current project associated with the home screen.
        main_window (optional): Reference to the main application window.
        main_layout (QVBoxLayout): Layout for organizing UI components vertically.
        search_input_field (QLineEdit): Input field for entering search queries.
        search_message (QLabel): Label for displaying search-related messages.
        table (OverviewTable): Table for displaying project data.
        header (HeaderBar): Header bar for the home screen.
    """


    def __init__(self, language_settings=None):
        super().__init__()
        self._ = language_settings
        self.container_home_screen = QVBoxLayout()

        # self.message_box = MessageBox(self._)
        self.head_wrapper = QFrame()
        self.search_input_field = QLineEdit()
        self.clear_search_bar_button = None
        self.search_message = QLabel()
        self.table = OverviewTable(self._)
        self.table.setItemDelegate(LastAddedProjectHighlightDelegate(self))
        self.header = HeaderBar(language=self._, table=self.table)

        self.last_added_ref = None

        self.create_main_content_ui()
        self.setLayout(self.container_home_screen)
        if Updater.needs_update:
            SuggestUpdateWindow( self._,Updater.local_version,Updater.master_version)

    def create_main_content_ui(self) -> None:
        """
        Creates the main user interface for the home screen.

        This method sets up the header, search bar, data table, and logo, arranging them in a vertical layout.

        The function constructs the main content of the home screen by adding various UI components to the layout. It includes a header bar, a search bar, a data table, and an AWV logo, ensuring proper spacing and alignment for a cohesive appearance.

        :return: None
        """
        # Header
        self.header.construct_header_bar()

        # Search bar
        search_container = QVBoxLayout()
        search_container.addWidget(self.draw_search_bar())
        search_container.setContentsMargins(16, 0, 16, 0)

        # Create the table
        self.table.draw_table()
        table_container = QVBoxLayout()
        table_container.addWidget(self.table)
        table_container.setContentsMargins(16, 0, 16, 0)

        #AWV logo
        AWV_logo_label = QLabel()
        pixmap = QPixmap(f'{IMG_DIR}/Vlaanderen_is_veilig_onderweg_vol-01_200.png')
        AWV_logo_label.setPixmap(pixmap)

        # add header to the vertical layout
        self.container_home_screen.addWidget(self.header)
        self.container_home_screen.addSpacing(39)
        # add searchbar to the vertical layout
        self.container_home_screen.addLayout(search_container)
        self.container_home_screen.addSpacing(43)
        # add table to the vertical layout with margins
        self.container_home_screen.addLayout(table_container)
        # self.container_home_screen.addStretch()
        self.container_home_screen.addSpacing(10)
        self.container_home_screen.addWidget(AWV_logo_label, alignment=Qt.AlignmentFlag.AlignRight)
        self.container_home_screen.setContentsMargins(0, 0, 0, 0)


    def fill_table(self,projects: [Project]) -> None:
        """
        Fills the table with project data based on the provided list of projects.

        This method updates the table display using the current search input to filter the projects.

        The function calls the `fill_table` method of the table component, passing the list of projects and the text from the search input field to ensure that only relevant projects are displayed.

        :param projects: A list of Project instances to populate the table.
        :type projects: list[Project]

        :return: None
        """

        self.table.fill_table(projects, self.search_input_field.text())


    def draw_search_bar(self) -> QWidget:
        """
        Creates and returns a search bar UI component.

        This method constructs a horizontal layout containing an input field for search queries
        and a message label for displaying error messages.

        The function initializes a QWidget as a wrapper for the search bar, applies a CSS class,
        and adds the input field and message label to the layout. The message label is styled to
        display text in red, indicating potential errors or prompts to the user.

        :return: The constructed search bar widget.
        :rtype: QWidget
        """

        search_wrapper = QWidget()
        search_wrapper.setProperty('class', 'search')
        search = QHBoxLayout()
        self.create_input_field()
        self.search_message.setText("")
        self.search_message.setStyleSheet("color: red")

        self.clear_search_bar_button = QPushButton()
        self.set_clear_icon(self.clear_search_bar_button)
        self.clear_search_bar_button.clicked.connect(self.clear_search_listener)
        self.clear_search_bar_button.setProperty('class', 'secondary-button')

        search.addWidget(self.search_input_field)
        search.addWidget(self.clear_search_bar_button)
        search.addWidget(self.search_message)

        search_wrapper.setLayout(search)
        return search_wrapper

    # noinspection PyMethodMayBeStatic
    def set_clear_icon(self, button: QPushButton) -> None:
        button.setIcon(qta.icon('mdi.close', color=Styling.button_icon_color))

    def clear_search_listener(self) -> None:
        self.search_input_field.setText("")
        HomeDomain.update_frontend()

    def create_input_field(self) -> None:
        """
        Initializes the search input field for the search bar.

        This method sets up a placeholder text and connects the return key event to update the frontend when the user submits a search query.

        The function configures the search input field to display a placeholder that prompts the user for input. It also establishes a connection to trigger an update of the frontend when the return key is pressed.

        :return: None
        """

        self.search_input_field.textChanged.connect(lambda: HomeDomain.update_frontend())
        self.search_input_field.setPlaceholderText(self._('search_text'))
        self.search_input_field.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Fixed)


    def remove_table_row(self, row_index: int) -> None:
        """
        Removes a specified row from the table.

        This method updates the table by removing the row at the given index, ensuring that the
        displayed data reflects the change.

        :param row_index: The index of the row to be removed from the table.
        :type row_index: int

        :return: None
        """
        self.table.removeRow(row_index)


    def reset_ui(self, lang_settings: Optional[Callable]=None) -> None:
        """
        Resets the user interface components to their default state.

        This method updates the UI elements, including the table and header, and sets the
        placeholder text for the search input field. It can also accept language settings to
        adjust the UI language if provided.

        :param lang_settings: Optional language settings to apply to the UI.
        :type lang_settings: dict or None

        :return: None
        """
        super().reset_ui(self._)
        if lang_settings is not None:
            self._ = lang_settings

        self.table.reset_ui(self._)
        self.search_input_field.setPlaceholderText(self._('search_text'))
        self.header.reset_ui(self._)
        self.last_added_ref = None
        # self.sort_on_last_edit()

    def sort_on_last_edit(self):
        self.table.activate_initial_sort_on_last_edit()
