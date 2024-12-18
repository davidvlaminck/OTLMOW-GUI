import logging
from pathlib import Path

from PyQt6.QtGui import QPixmap

from Domain.ProjectFileManager import ProjectFileManager
from PyQt6.QtWidgets import QWidget, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, \
    QLineEdit, QFrame
from PyQt6.QtCore import Qt
import Domain.HomeDomain as home_domain
from Domain.Updater import Updater
from GUI.DialogWindows.SuggestUpdateWindow import SuggestUpdateWindow
from GUI.Screens.Screen import Screen
from GUI.HeaderBar import HeaderBar
from GUI.MessageBox import MessageBox
from GUI.OverviewTable import OverviewTable

ROOT_DIR = Path(__file__).parent

IMG_DIR = ROOT_DIR.parent.parent / 'img/'


class HomeScreen(Screen):

    def __init__(self, language_settings=None):
        super().__init__()
        self._ = language_settings
        self.home_domain = home_domain.HomeDomain(self._)
        self.container_home_screen = QVBoxLayout()

        self.message_box = MessageBox(self._, self.home_domain)
        self.head_wrapper = QFrame()
        self.input_field = QLineEdit()
        self.new_project_button = QPushButton()
        self.search_message = QLabel()
        self.table = OverviewTable(self.search_message, self._, self.home_domain, self.message_box)
        self.header = HeaderBar(language=self._, table=self.table)
        self.main_window = None

        ProjectFileManager.load_projects_into_global()
        self.main_content_ui()
        self.init_ui()
        if Updater.needs_update:
            SuggestUpdateWindow( self._,Updater.local_version,Updater.master_version)

    def main_content_ui(self):
        # Search bar
        search_container = QVBoxLayout()
        search_container.addWidget(self.draw_search_bar())
        search_container.setContentsMargins(16, 0, 16, 0)

        # Create the table
        self.table.draw_table()
        table_container = QVBoxLayout()
        table_container.addWidget(self.table)
        table_container.setContentsMargins(16, 0, 16, 0)

        # Header
        self.header.construct_header_bar()

        # add header to the vertical layout
        self.container_home_screen.addWidget(self.header)
        self.container_home_screen.addSpacing(39)
        # add searchbar to the vertical layout
        self.container_home_screen.addLayout(search_container)
        self.container_home_screen.addSpacing(43)
        # add table to the vertical layout with margins
        self.container_home_screen.addLayout(table_container)
        pixmap = QPixmap(str(IMG_DIR) + '/AWV_200.png')
        self.container_home_screen.addStretch()
        self.container_home_screen.addWidget(QLabel(pixmap=pixmap), alignment=Qt.AlignmentFlag.AlignRight)
        self.container_home_screen.setContentsMargins(0, 0, 0, 0)

    def init_ui(self):
        self.setLayout(self.container_home_screen)

    def draw_search_bar(self) -> QWidget:
        search_wrapper = QWidget()
        search_wrapper.setProperty('class', 'search')
        search = QHBoxLayout()
        self.create_input_field()
        self.search_message.setText("")
        self.search_message.setStyleSheet("color: red")
        search.addWidget(self.input_field)
        search.addWidget(self.search_message)
        search.addStretch()
        search_wrapper.setLayout(search)
        return search_wrapper

    def create_input_field(self):
        self.input_field.returnPressed.connect(lambda: self.table.draw_table(self.input_field.text()))
        self.input_field.setPlaceholderText(self._('search_text'))

    def reset_ui(self, lang_settings=None) -> None:
        if lang_settings is not None:
            self._ = lang_settings
            self.home_domain = home_domain.HomeDomain(self._)
        self.table.reset_ui(self._)
        self.input_field.setPlaceholderText(self._('search_text'))
        self.header.reset_ui(self._)
