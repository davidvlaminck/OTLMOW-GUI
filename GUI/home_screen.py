from PyQt6.QtWidgets import QWidget, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QTableWidget, \
    QTableWidgetItem, QLineEdit, QHeaderView
from PyQt6.QtCore import Qt


class HomeScreen(QWidget):
    def __init__(self):
        super().__init__()

        # Vertical layout
        vert = QVBoxLayout()

        # Create the header
        headWrapper = QWidget()
        headWrapper.setProperty('class', 'header')
        Header = QHBoxLayout()
        title = QLabel('OTLWizard')
        Header.addWidget(title)
        button = QPushButton('New Project')
        Header.addWidget(button)
        Header.setAlignment(button, Qt.AlignmentFlag.AlignLeft)
        User_pref = QHBoxLayout()
        settings = QPushButton('Settings')
        User_pref.addWidget(settings)
        help = QPushButton('Help')
        User_pref.addWidget(help)
        Header.addLayout(User_pref)
        Header.setAlignment(User_pref, Qt.AlignmentFlag.AlignRight)
        headWrapper.setLayout(Header)

        # Search bar
        searchWrapper = QWidget()
        searchWrapper.setProperty('class', 'search')
        search = QHBoxLayout()
        inputField = QLineEdit()
        search.addWidget(inputField)
        searchbutton = QPushButton('Search')
        search.addWidget(searchbutton)
        searchWrapper.setLayout(search)

        # Create the table with QTableView
        table = QTableWidget()
        table.setRowCount(4)
        table.verticalHeader().setVisible(False)
        table.setColumnCount(4)

        for column in range(table.columnCount()):
            table.horizontalHeader().setSectionResizeMode(column, QHeaderView.ResizeMode.Stretch)
            #table.setColumnWidth(column, 474)
        table.setShowGrid(False)
        # Zorgt ervoor dat selectie op row is niet op cell
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        # Zorgt ervoor dat de table niet editable is
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.resizeRowsToContents()
        table.setHorizontalHeaderLabels(['Eigen referentie:', 'Bestek - (Dienstbevel)', 'Subset', 'Laatst bewerkt'])
        # ALign titles of header to the left
        table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft)

        # add data to the table
        for j in range(4):
            for i in range(4):
                item = QTableWidgetItem()
                item.setText('test')
                table.setItem(j, i, item)

        # add header to the vertical layout
        vert.addWidget(headWrapper)
        vert.addSpacing(39)
        # add searchbar to the vertical layout
        vert.addWidget(searchWrapper)
        vert.addSpacing(43)
        # add table to the vertical layout
        vert.addWidget(table)

        self.setLayout(vert)
        self.show()
