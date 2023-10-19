import datetime
import gettext
from Domain.language_settings import returnLanguage
_ = returnLanguage()

from PyQt6.QtWidgets import QWidget, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QTableWidget, \
    QTableWidgetItem, QLineEdit, QHeaderView
from PyQt6.QtCore import Qt
import qtawesome as qta
import Domain.home_domain as HomeDomain
import GUI.dialog_window as DialogWindow


class HomeScreen(QWidget):
    projects = None
    home_func = None
    dialog_window = None

    def __init__(self, database):
        super().__init__()
        self.home_func = HomeDomain.HomeDomain(database)
        self.dialog_window = DialogWindow.DialogWindow(database)

        # Vertical layout
        container_home_screen = QVBoxLayout()

        # Create the header
        head_wrapper = QWidget()
        head_wrapper.setProperty('class', 'header')
        header = QHBoxLayout()
        title = QLabel('OTLWizard')
        title.setProperty('class', 'title')
        header.addWidget(title)
        new_project_button = QPushButton(_('New Project'))
        new_project_button.setProperty('class', 'new-project')
        header.addWidget(new_project_button)
        header.setAlignment(new_project_button, Qt.AlignmentFlag.AlignLeft)
        user_pref_container = QHBoxLayout()
        settings = QPushButton()
        settings.setIcon(qta.icon('mdi.cog'))
        settings.setProperty('class','settings')
        user_pref_container.addWidget(settings)
        help_widget = QPushButton()
        help_widget.setIcon(qta.icon('mdi.help-circle'))
        help_widget.setProperty('class', 'settings')
        user_pref_container.addWidget(help_widget)
        header.addLayout(user_pref_container)
        header.setAlignment(user_pref_container, Qt.AlignmentFlag.AlignRight)
        head_wrapper.setLayout(header)

        # Search bar
        search_container = QVBoxLayout()
        search_wrapper = QWidget()
        search_wrapper.setProperty('class', 'search')
        search = QHBoxLayout()
        input_field = QLineEdit()
        input_field.setPlaceholderText(_('Zoeken op projectnaam of bestek'))
        search.addWidget(input_field)
        search_button = QPushButton(_('Search'))
        search.addWidget(search_button)
        search.addStretch()
        search_wrapper.setLayout(search)
        search_container.addWidget(search_wrapper)
        search_container.setContentsMargins(16, 0, 16, 0)

        # Create the table
        table = self.draw_table()
        table_container = QVBoxLayout()
        table_container.addWidget(table)
        table_container.setContentsMargins(16, 0, 16, 0)

        # Add functionality to new project button
        # Can only happen here because the table needs to be drawn first
        new_project_button.clicked.connect(lambda: self.dialog_window.update_project(home_screen=self, table=table))

        # add header to the vertical layout
        container_home_screen.addWidget(head_wrapper)
        container_home_screen.addSpacing(39)
        # add searchbar to the vertical layout
        container_home_screen.addLayout(search_container)
        container_home_screen.addSpacing(43)
        # add table to the vertical layout with margins
        container_home_screen.addLayout(table_container)
        container_home_screen.addStretch()
        container_home_screen.setContentsMargins(0,0,0,0)
        self.setLayout(container_home_screen)
        self.show()

    def draw_table(self):
        table_container = QVBoxLayout()
        table = QTableWidget()
        table.setRowCount(self.home_func.get_amount_of_rows())
        table.verticalHeader().setVisible(False)
        table.setColumnCount(6)
        # Set the width of the columns to stretch except the last two columns for buttons
        for column in range(table.columnCount() - 2):
            table.horizontalHeader().setSectionResizeMode(column, QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        table.setShowGrid(False)
        # Zorgt ervoor dat selectie op row is niet op cell
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        # Zorgt ervoor dat de table niet editable is
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setHorizontalHeaderLabels(
            [_('Eigen referentie:'), _('Bestek - (Dienstbevel)'), _('Subset'), _('Laatst bewerkt'), '', ''])
        # ALign titles of header to the left
        table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft)

        # add data to the table
        self.projects = self.home_func.get_all_projects()
        for count, element in enumerate(self.projects):
            for i in range(4):
                self.add_cell_to_table(table, count, i, element[i + 1])
            self.add_update_and_delete_button(count, element[0], table)
        return table

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
            table.setItem(row,column, QTableWidgetItem(item.strftime("%d-%m-%Y")))
        else:
            table.setItem(row, column, QTableWidgetItem(item))
