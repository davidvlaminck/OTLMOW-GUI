import datetime
from pathlib import Path
from typing import Union

from PyQt6.QtGui import QPixmap

from Domain.language_settings import return_language
from PyQt6.QtWidgets import QWidget, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QTableWidget, \
    QTableWidgetItem, QLineEdit, QHeaderView, QFrame
from PyQt6.QtCore import Qt
import qtawesome as qta
import Domain.home_domain as HomeDomain
import GUI.dialog_window as DialogWindow
from GUI.message_box import MessageBox
from GUI.overviewtable import OverviewTable

ROOT_DIR = Path(__file__).parent

IMG_DIR = ROOT_DIR.parent / 'img/'
LANG_DIR = ROOT_DIR.parent / 'locale/'


class HomeScreen(QWidget):

    def __init__(self, database):
        super().__init__()
        self.database = database
        self._ = return_language(LANG_DIR)
        self.home_domain = HomeDomain.HomeDomain(database, self._)
        self.container_home_screen = QVBoxLayout()
        self.projects: list
        self.message_box = MessageBox(self._, self.home_domain)
        self.head_wrapper = QFrame()
        self.input_field = QLineEdit()
        self.new_project_button = QPushButton()
        self.search_message = QLabel()
        self.table = OverviewTable(self.search_message, self._, self.home_domain, self.message_box, self.database)

        self.main_content_ui()
        self.init_ui()

    def main_content_ui(self):
        # Header
        self.construct_header_bar()

        # Search bar
        search_container = QVBoxLayout()
        search_container.addWidget(self.draw_search_bar())
        search_container.setContentsMargins(16, 0, 16, 0)

        # Create the table
        self.table.draw_table()
        table_container = QVBoxLayout()
        table_container.addWidget(self.table)
        table_container.setContentsMargins(16, 0, 16, 0)

        # add header to the vertical layout
        self.container_home_screen.addWidget(self.head_wrapper)
        self.container_home_screen.addSpacing(39)
        # add searchbar to the vertical layout
        self.container_home_screen.addLayout(search_container)
        self.container_home_screen.addSpacing(43)
        # add table to the vertical layout with margins
        self.container_home_screen.addLayout(table_container)
        pixmap = QPixmap(str(IMG_DIR) + '/AWV_logo.png')
        pixmap = pixmap.scaledToWidth(200)
        self.container_home_screen.addStretch()
        self.container_home_screen.addWidget(QLabel(pixmap=pixmap), alignment=Qt.AlignmentFlag.AlignRight)
        self.container_home_screen.setContentsMargins(0, 0, 0, 0)

    def init_ui(self):
        self.setLayout(self.container_home_screen)
        self.show()

    def construct_header_bar(self):
        self.head_wrapper.setProperty('class', 'header')
        header = QHBoxLayout()
        title = QLabel('OTLWizard')
        title.setProperty('class', 'title')
        header.addWidget(title)
        self.create_new_project_button()
        header.addWidget(self.new_project_button)
        header.setAlignment(self.new_project_button, Qt.AlignmentFlag.AlignLeft)
        user_settings = self.construct_settings_bar()
        header.addLayout(user_settings)
        header.setAlignment(user_settings, Qt.AlignmentFlag.AlignRight)
        self.head_wrapper.setLayout(header)

    def create_new_project_button(self):
        self.new_project_button.setText(self._('new_project_button'))
        self.new_project_button.setProperty('class', 'new-project')
        self.new_project_button.clicked.connect(
            lambda: self.start_dialog_window(home_screen=self, is_project=True))

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

    def start_dialog_window(self, id_: int = None, overview_table=None, home_screen=None, is_project=False) -> None:
        dialog_window = DialogWindow.DialogWindow(self.database, self._)
        if is_project:
            dialog_window.draw_upsert_project(id_=id_, overview_table=overview_table)
        else:
            dialog_window.language_window(home_screen=home_screen)

    def reset_ui(self, lang_settings=None) -> None:
        if lang_settings is not None:
            self._ = lang_settings
            self.home_domain = HomeDomain.HomeDomain(self.database, self._)
        self.table.reset_language(self._)
        self.create_input_field()
        self.create_new_project_button()
