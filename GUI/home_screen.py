import datetime
from typing import Union

from Domain.language_settings import return_language
from PyQt6.QtWidgets import QWidget, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QTableWidget, \
    QTableWidgetItem, QLineEdit, QHeaderView
from PyQt6.QtCore import Qt
import qtawesome as qta
import Domain.home_domain as HomeDomain
import GUI.dialog_window as DialogWindow
from GUI.message_box import MessageBox


class HomeScreen(QWidget):

    def __init__(self, database):
        super().__init__()
        self.database = database
        self._ = return_language('../locale/')
        self.home_domain = HomeDomain.HomeDomain(database, self._)
        self.container_home_screen = QVBoxLayout()
        self.table = QTableWidget()
        self.projects: list
        self.message_box = MessageBox(self._, self.home_domain)

        self.main_content_ui()
        self.init_ui()

    def main_content_ui(self):
        # Header
        head_wrapper = self.construct_header_bar()

        # Search bar
        search_container = QVBoxLayout()
        search_container.addWidget(self.draw_search_bar())
        search_container.setContentsMargins(16, 0, 16, 0)

        # Create the table
        self.draw_table()
        table_container = QVBoxLayout()
        table_container.addWidget(self.table)
        table_container.setContentsMargins(16, 0, 16, 0)

        # add header to the vertical layout
        self.container_home_screen.addWidget(head_wrapper)
        self.container_home_screen.addSpacing(39)
        # add searchbar to the vertical layout
        self.container_home_screen.addLayout(search_container)
        self.container_home_screen.addSpacing(43)
        # add table to the vertical layout with margins
        self.container_home_screen.addLayout(table_container)
        self.container_home_screen.addStretch()
        self.container_home_screen.setContentsMargins(0, 0, 0, 0)

    def init_ui(self):
        self.setLayout(self.container_home_screen)
        self.show()

    def construct_header_bar(self):
        head_wrapper = QWidget()
        head_wrapper.setProperty('class', 'header')
        header = QHBoxLayout()
        title = QLabel('OTLWizard')
        title.setProperty('class', 'title')
        header.addWidget(title)
        new_project_button = QPushButton(self._('new_project_button'))
        new_project_button.setProperty('class', 'new-project')
        header.addWidget(new_project_button)
        header.setAlignment(new_project_button, Qt.AlignmentFlag.AlignLeft)
        user_settings = self.construct_settings_bar()
        header.addLayout(user_settings)
        header.setAlignment(user_settings, Qt.AlignmentFlag.AlignRight)
        head_wrapper.setLayout(header)
        new_project_button.clicked.connect(
            lambda: self.start_dialog_window(home_screen=self, is_project=True))
        return head_wrapper

    def construct_settings_bar(self):
        user_pref_container = QHBoxLayout()
        settings = QPushButton()
        settings.setIcon(qta.icon('mdi.cog'))
        settings.setProperty('class', 'settings')
        settings.clicked.connect(lambda: self.start_dialog_window(home_screen=self))
        user_pref_container.addWidget(settings)
        help_widget = QPushButton()
        help_widget.setIcon(qta.icon('mdi.help-circle'))
        help_widget.setProperty('class', 'settings')
        user_pref_container.addWidget(help_widget)
        return user_pref_container

    def draw_search_bar(self) -> QWidget:
        search_wrapper = QWidget()
        search_wrapper.setProperty('class', 'search')
        search = QHBoxLayout()
        input_field = QLineEdit()
        input_field.setPlaceholderText(self._('search_text'))
        search.addWidget(input_field)
        search_button = QPushButton(self._('search_button'), self)
        search_button.clicked.connect(lambda: self.draw_table(input_field.text()))
        search.addWidget(search_button)
        search.addStretch()
        search_wrapper.setLayout(search)
        return search_wrapper

    def draw_table(self, input_text: str = None):
        self.filter_projects(input_text)
        self.table.setRowCount(len(self.projects))
        self.table.verticalHeader().setVisible(False)
        self.table.setColumnCount(6)
        # Set the width of the columns to stretch except the last two columns for buttons
        for column in range(self.table.columnCount() - 2):
            self.table.horizontalHeader().setSectionResizeMode(column, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setShowGrid(False)
        # Zorgt ervoor dat selectie op row is niet op cell
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        # Zorgt ervoor dat de table niet editable is
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setHorizontalHeaderLabels(
            [self._('own_reference'), self._('service_order'), self._('subset'), self._('last_edited'), '', ''])
        # ALign titles of header to the left
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft)

        # TODO: add data to the table in aparte functie
        for count, element in enumerate(self.projects):
            for i in range(4):
                self.add_cell_to_table(self.table, count, i, element[i + 1])
            self.add_update_and_delete_button(count, element[0], self.table)

    def start_dialog_window(self, id_: int = None, home_screen=None, is_project=False) -> None:
        dialog_window = DialogWindow.DialogWindow(self.database, self._)
        if is_project:
            dialog_window.draw_upsert_project(id_=id_, home_screen=home_screen)
        else:
            dialog_window.language_window(home_screen=home_screen)

    def add_update_and_delete_button(self, count: int, id_: int, table: QTableWidget) -> None:
        edit = QPushButton()
        edit.setIcon(qta.icon('mdi.pencil'))
        edit.setProperty('class', 'alter-button')
        edit.clicked.connect(
            lambda _, row_id=id_: self.start_dialog_window(id_=row_id, home_screen=self, is_project=True))
        table.setCellWidget(count, 4, edit)
        button = QPushButton()
        button.setIcon(qta.icon('mdi.trash-can'))
        button.setProperty('class', 'alter-button')
        button.clicked.connect(lambda _, i=id_:
                               self.message_box.draw_remove_project_screen(i, table))
        table.setCellWidget(count, 5, button)

    @staticmethod
    def add_cell_to_table(table: QTableWidget, row: int, column: int, item: Union[str, datetime.datetime]) -> None:
        if isinstance(item, datetime.date):
            table.setItem(row, column, QTableWidgetItem(item.strftime("%d-%m-%Y")))
        else:
            table.setItem(row, column, QTableWidgetItem(item))

    def reset_ui(self, lang_settings=None) -> None:
        if lang_settings is not None:
            self._ = lang_settings
            self.home_domain = HomeDomain.HomeDomain(self.database, self._)
        self.construct_header_bar()
        self.draw_table()
        self.construct_header_bar()

    def filter_projects(self, input_text: str):
        if type(input_text) is str:
            input_text.strip()
            try:
                if len(input_text) != 0:
                    self.table.clear()
                    self.projects = [k for k in self.projects if input_text in k]
                    return
                else:
                    self.projects = self.home_domain.get_all_projects()
            except Exception as e:
                print(e)
        else:
            self.projects = self.home_domain.get_all_projects()
