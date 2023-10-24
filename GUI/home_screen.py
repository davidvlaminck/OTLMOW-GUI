import datetime
from Domain.language_settings import LanguageSettings
from PyQt6.QtWidgets import QWidget, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QTableWidget, \
    QTableWidgetItem, QLineEdit, QHeaderView
from PyQt6.QtCore import Qt
import qtawesome as qta
import Domain.home_domain as HomeDomain
import GUI.dialog_window as DialogWindow


class HomeScreen(QWidget):
    dialog_window = None

    def __init__(self, database):
        super().__init__()
        self.database = database
        self.lang_settings = LanguageSettings()
        self._ = self.lang_settings.return_language()
        self.home_func = HomeDomain.HomeDomain(database, self.lang_settings)
        self.container_home_screen = QVBoxLayout()
        self.dialog_window = DialogWindow.DialogWindow(database, self.lang_settings)
        self.search_wrapper = QWidget()
        self.table = QTableWidget()
        self.layouts = []
        self.main_content_ui()
        self.init_ui()
        self.projects = []

    def main_content_ui(self):
        print("test" + self.lang_settings.language)
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
        user_pref_container = QHBoxLayout()
        settings = QPushButton()
        settings.setIcon(qta.icon('mdi.cog'))
        settings.setProperty('class', 'settings')
        settings.clicked.connect(lambda: self.dialog_window.language_window(self))
        user_pref_container.addWidget(settings)
        help_widget = QPushButton()
        help_widget.setIcon(qta.icon('mdi.help-circle'))
        help_widget.setProperty('class', 'settings')
        user_pref_container.addWidget(help_widget)
        header.addLayout(user_pref_container)
        header.setAlignment(user_pref_container, Qt.AlignmentFlag.AlignRight)
        self.layouts.append(header)
        head_wrapper.setLayout(header)

        # Search bar
        search_container = QVBoxLayout()
        self.search_wrapper = QWidget()
        self.draw_search_bar()
        search_container.addWidget(self.search_wrapper)
        self.layouts.append(search_container)
        search_container.setContentsMargins(16, 0, 16, 0)

        # Create the table
        self.draw_table()
        table_container = QVBoxLayout()
        table_container.addWidget(self.table)
        self.layouts.append(table_container)
        table_container.setContentsMargins(16, 0, 16, 0)

        # Add functionality to new project button
        # Can only happen here because the table needs to be drawn first
        new_project_button.clicked.connect(
            lambda: self.dialog_window.update_project(home_screen=self, table=self.table))

        # add header to the vertical layout
        self.layouts.append(self.container_home_screen)
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

    def draw_search_bar(self):
        self.search_wrapper = QWidget()
        self.search_wrapper.setProperty('class', 'search')
        search = QHBoxLayout()
        input_field = QLineEdit()
        input_field.setPlaceholderText(self._('search_text'))
        search.addWidget(input_field)
        search_button = QPushButton(self._('search_button'))
        search_button.clicked.connect(lambda: self.draw_table(input_field.text()))
        search.addWidget(search_button)
        search.addStretch()
        self.search_wrapper.setLayout(search)

    def draw_table(self, input: str = None):
        self.filter_projects(input)
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

        # add data to the table
        self.projects = self.home_func.get_all_projects()
        if input is not None:
            print(self.table.findItems(input, Qt.MatchFlag.MatchContains))
            self.projects = [k for k in self.projects if input in k]
        for count, element in enumerate(self.projects):
            for i in range(4):
                self.add_cell_to_table(self.table, count, i, element[i + 1])
            self.add_update_and_delete_button(count, element[0], self.table)

    def add_update_and_delete_button(self, count, id_, table):
        edit = QPushButton()
        edit.setIcon(qta.icon('mdi.pencil'))
        edit.setProperty('class', 'alter-button')
        edit.clicked.connect(lambda _, row_id=id_: self.dialog_window.update_project(id_=row_id,
                                                                                     table=table, home_screen=self
                                                                                     ))
        table.setCellWidget(count, 4, edit)
        button = QPushButton()
        button.setIcon(qta.icon('mdi.trash-can'))
        button.setProperty('class', 'alter-button')
        button.clicked.connect(lambda _, i=id_:
                               self.home_func.remove_project(id_=i, table=table))
        table.setCellWidget(count, 5, button)

    def add_cell_to_table(self, table, row, column, item):
        if isinstance(item, datetime.date):
            table.setItem(row, column, QTableWidgetItem(item.strftime("%d-%m-%Y")))
        else:
            table.setItem(row, column, QTableWidgetItem(item))

    def reset_ui(self, lang_settings=None):
        if lang_settings is not None:
            self.lang_settings = lang_settings
            self._ = self.lang_settings.return_language()
            self.home_func = HomeDomain.HomeDomain(self.database, self.lang_settings)
            self.dialog_window = DialogWindow.DialogWindow(self.database, self.lang_settings)
        print("Home screen has been reset with language " + self.lang_settings.language)
        self.draw_search_bar()
        self.draw_table()

    def filter_projects(self, input: str):
        print(input)
        print(type(input))
        if type(input) is str:
            input.strip()
            try:
                if len(input) == 0:
                    self.table.clear()
                    self.projects = [k for k in self.projects if input in k]
                    return
            except Exception as e:
                print(e)
        else:
            self.projects = self.home_func.get_all_projects()
