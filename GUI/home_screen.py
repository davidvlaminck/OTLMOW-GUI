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
        top.addWidget(QLabel('Eigen Referentie:'))
        top.addWidget(QLabel('Bestek - (dienstbevel):'))
        top.addWidget(QLabel('Subset:'))
        top.addWidget(QLabel("Laatst bewerkt:"))
        table.addLayout(top)

        # Create rows in that table
        for i in range(10):
            row = QHBoxLayout()
            row.addWidget(QLabel('Test'))
            row.addWidget(QLabel('Test'))
            row.addWidget(QLabel('Test'))
            row.addWidget(QLabel('Test'))
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
