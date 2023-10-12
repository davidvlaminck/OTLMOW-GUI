from PyQt6.QtWidgets import QWidget, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QTableWidget, \
    QTableWidgetItem, QLineEdit, QHeaderView
from PyQt6.QtCore import Qt
import qtawesome as qta


class HomeScreen(QWidget):
    def __init__(self):
        super().__init__()

        # Vertical layout
        containerHomeScreen = QVBoxLayout()

        # Create the header
        headWrapper = QWidget()
        headWrapper.setProperty('class', 'header')
        header = QHBoxLayout()
        title = QLabel('OTLWizard')
        header.addWidget(title)
        newProjectButton = QPushButton('New Project')
        newProjectButton.setProperty('class', 'new-project')
        header.addWidget(newProjectButton)
        header.setAlignment(newProjectButton, Qt.AlignmentFlag.AlignLeft)
        userPrefContainer = QHBoxLayout()
        settings = QPushButton()
        settings.setIcon(qta.icon('mdi.cog'))
        userPrefContainer.addWidget(settings)
        helpwidget = QPushButton()
        helpwidget.setIcon(qta.icon('mdi.help-circle'))
        userPrefContainer.addWidget(helpwidget)
        header.addLayout(userPrefContainer)
        header.setAlignment(userPrefContainer, Qt.AlignmentFlag.AlignRight)
        headWrapper.setLayout(header)

        # Search bar
        searchWrapper = QWidget()
        searchWrapper.setProperty('class', 'search')
        search = QHBoxLayout()
        inputField = QLineEdit()
        inputField.setPlaceholderText('Zoeken op projectnaam of bestek')
        search.addWidget(inputField)
        searchbutton = QPushButton('Search')
        search.addWidget(searchbutton)
        search.addStretch()
        searchWrapper.setLayout(search)

        # Create the table with QTableView
        table = QTableWidget()
        table.setRowCount(4)
        table.verticalHeader().setVisible(False)
        table.setColumnCount(6)
        for column in range(table.columnCount() - 2):
            table.horizontalHeader().setSectionResizeMode(column, QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        table.setShowGrid(False)
        # Zorgt ervoor dat selectie op row is niet op cell
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        # Zorgt ervoor dat de table niet editable is
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setHorizontalHeaderLabels(['Eigen referentie:', 'Bestek - (Dienstbevel)', 'Subset', 'Laatst bewerkt', '',''])
        # ALign titles of header to the left
        table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft)

        # add data to the table
        for j in range(4):
            for i in range(4):
                item = QTableWidgetItem()
                item.setText('test')
                table.setItem(j, i, item)
            item = QPushButton()
            item.setIcon(qta.icon('mdi.pencil'))
            table.setCellWidget(j, 4, item)
            item = QPushButton()
            item.setIcon(qta.icon('mdi.trash-can'))
            table.setCellWidget(j, 5, item)
        # add header to the vertical layout
        containerHomeScreen.addWidget(headWrapper)
        containerHomeScreen.addSpacing(39)
        # add searchbar to the vertical layout
        containerHomeScreen.addWidget(searchWrapper)
        containerHomeScreen.addSpacing(43)
        # add table to the vertical layout
        containerHomeScreen.addWidget(table)
        containerHomeScreen.addStretch()

        self.setLayout(containerHomeScreen)
        self.show()
