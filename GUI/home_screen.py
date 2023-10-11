from PyQt6.QtWidgets import QWidget, QGridLayout, QPushButton, QLabel, QHBoxLayout, QVBoxLayout
from PyQt6.QtCore import Qt


class HomeScreen(QWidget):
    def __init__(self):
        super().__init__()


        # Create GridLayout
        grid = QGridLayout()
        Header = QHBoxLayout()
        Header.setProperty('class', 'Header')

        # Create the header
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

        # Create a table
        table = QVBoxLayout()
        top = QHBoxLayout()
        titel1 = QLabel('Eigen Referentie:')
        titel1.setProperty('class', 'titel')
        top.addWidget(titel1)
        titel2 = QLabel('Bestek - (dienstbevel):')
        titel2.setProperty('class', 'titel')
        top.addWidget(titel2)
        titel3 = QLabel('Subset:')
        titel3.setProperty('class', 'titel')
        top.addWidget(titel3)
        titel4 = QLabel('Laatst bewerkt:')
        titel4.setProperty('class', 'titel')
        top.addWidget(titel4)
        table.addLayout(top)
        table.setSpacing(0)

        # Create rows in that table
        for i in range(10):
            row = QHBoxLayout()
            row1 = QLabel('Test')
            row1.setProperty('class', 'row')
            row.addWidget(row1)
            row2 = QLabel('Test')
            row2.setProperty('class', 'row')
            row.addWidget(row2)
            row3 = QLabel('Test')
            row3.setProperty('class', 'row')
            row.addWidget(row3)
            row4 = QLabel('Test')
            row4.setProperty('class', 'row')
            row.addWidget(row4)
            table.addLayout(row)

        # Add the header to the grid
        grid.addLayout(Header, 0, 0, 0, 0)
        # Align the header to the top
        grid.setAlignment(Header, Qt.AlignmentFlag.AlignTop)
        # Add the table to the grid
        grid.addLayout(table, 1, 0, 2, 0, Qt.AlignmentFlag.AlignTop)

        self.setLayout(grid)
        with open('custom.css', 'r') as file:
            self.setStyleSheet(file.read())
        self.show()
