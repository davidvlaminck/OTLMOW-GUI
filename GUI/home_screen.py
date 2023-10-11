from PyQt6.QtWidgets import QWidget, QGridLayout, QPushButton, QLabel, QHBoxLayout
from PyQt6.QtCore import Qt
class HomeScreen(QWidget):
    def __init__(self):
        super().__init__()

        #Create GridLayout
        grid = QGridLayout()
        Top = QHBoxLayout()

        #Create the header
        title = QLabel('OTLWizard')
        Top.addWidget(title)
        button = QPushButton('New Project')
        Top.addWidget(button)
        Top.setAlignment(button, Qt.AlignmentFlag.AlignLeft)
        User_pref = QHBoxLayout()
        settings = QPushButton('Settings')
        User_pref.addWidget(settings)
        help = QPushButton('Help')
        User_pref.addWidget(help)
        Top.addLayout(User_pref)
        Top.setAlignment(User_pref, Qt.AlignmentFlag.AlignRight)


        grid.addLayout(Top, 0, 0, 0, 0, Qt.AlignmentFlag.AlignCenter)
        grid.setAlignment(Top, Qt.AlignmentFlag.AlignTop)


        self.setLayout(grid)
        self.show()
