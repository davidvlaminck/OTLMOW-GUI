from PyQt6.QtWidgets import QWidget, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QTableWidget, \
    QTableWidgetItem, QLineEdit, QHeaderView
from PyQt6.QtCore import Qt
import qtawesome as qta
import Domain.home_domain as HomeDomain
import GUI.dialog_window as DialogWindow


class HomeScreen(QWidget):
    def __init__(self, database):
        super().__init__()
        home_func = HomeDomain.HomeDomain(database)
        dialog_window = DialogWindow.DialogWindow(database)

        # Vertical layout
        container_home_screen = QVBoxLayout()

        # Create the header
        head_wrapper = QWidget()
        head_wrapper.setProperty('class', 'header')
        header = QHBoxLayout()
        title = QLabel('OTLWizard')
        header.addWidget(title)
        new_project_button = QPushButton('New Project')
        new_project_button.setProperty('class', 'new-project')
        header.addWidget(new_project_button)
        header.setAlignment(new_project_button, Qt.AlignmentFlag.AlignLeft)
        user_pref_container = QHBoxLayout()
        settings = QPushButton()
        settings.setIcon(qta.icon('mdi.cog'))
        user_pref_container.addWidget(settings)
        help_widget = QPushButton()
        help_widget.setIcon(qta.icon('mdi.help-circle'))
        user_pref_container.addWidget(help_widget)
        header.addLayout(user_pref_container)
        header.setAlignment(user_pref_container, Qt.AlignmentFlag.AlignRight)
        head_wrapper.setLayout(header)

        # Search bar
        search_wrapper = QWidget()
        search_wrapper.setProperty('class', 'search')
        search = QHBoxLayout()
        input_field = QLineEdit()
        input_field.setPlaceholderText('Zoeken op projectnaam of bestek')
        search.addWidget(input_field)
        search_button = QPushButton('Search')
        search.addWidget(search_button)
        search.addStretch()
        search_wrapper.setLayout(search)

        # Create the table with QTableView
        table = QTableWidget()
        table.setRowCount(home_func.get_amount_of_rows())
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
            ['Eigen referentie:', 'Bestek - (Dienstbevel)', 'Subset', 'Laatst bewerkt', '', ''])
        # ALign titles of header to the left
        table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft)

        # add data to the table"
        projects = home_func.get_all_projects()
        for j in range(home_func.get_amount_of_rows()):
            for i in range(4):
                item = QTableWidgetItem()
                item.setText(projects[j][i + 1])
                table.setItem(j, i, item)
            edit = QPushButton()
            edit.setIcon(qta.icon('mdi.pencil'))
            edit.clicked.connect(lambda _, row_id = j: dialog_window.update_project(id_= projects[row_id][0],
                                                                                  eigen_ref=projects[row_id][1],
                                                                                  bestek=projects[row_id][2],
                                                                                  subset=projects[row_id][3],
                                                                                  table=table
                                                                                    ))
            table.setCellWidget(j, 4, edit)
            edit.show()
            button = QPushButton()
            button.setIcon(qta.icon('mdi.trash-can'))
            button.setProperty('class', f"""{projects[j][0]}""")
            button.clicked.connect(lambda _, i= projects[j][0]:
                                   home_func.remove_project(id_=i, table=table))
            table.setCellWidget(j, 5, button)
        # add header to the vertical layout
        container_home_screen.addWidget(head_wrapper)
        container_home_screen.addSpacing(39)
        # add searchbar to the vertical layout
        container_home_screen.addWidget(search_wrapper)
        container_home_screen.addSpacing(43)
        # add table to the vertical layout
        container_home_screen.addWidget(table)
        container_home_screen.addStretch()

        self.setLayout(container_home_screen)
        self.show()
