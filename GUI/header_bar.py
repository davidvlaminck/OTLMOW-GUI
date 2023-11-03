from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

import qtawesome as qta

from GUI.dialog_window import DialogWindow


class HeaderBar(QFrame):
    def __init__(self, _, db, homescreen, table=None):
        super().__init__()
        self.new_project_button = QPushButton()
        self._ = _
        self.database = db
        self.home_screen = homescreen
        self.table = table
        #self.navigation = navigation

    def construct_header_bar(self):
        self.setProperty('class', 'header')
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
        self.setLayout(header)

    def create_new_project_button(self):
        self.new_project_button.setText(self._('new_project_button'))
        self.new_project_button.setProperty('class', 'new-project')
        self.new_project_button.clicked.connect(
            lambda: self.start_dialog_window(is_project=True))

    def construct_settings_bar(self):
        user_pref_container = QHBoxLayout()
        settings = QPushButton()
        settings.setIcon(qta.icon('mdi.cog'))
        settings.setProperty('class', 'settings')
        settings.clicked.connect(lambda: self.start_dialog_window(home_screen=self.home_screen))
        user_pref_container.addWidget(settings)
        help_widget = QPushButton()
        help_widget.setIcon(qta.icon('mdi.help-circle'))
        help_widget.setProperty('class', 'settings')
        user_pref_container.addWidget(help_widget)
        return user_pref_container

    def start_dialog_window(self, id_: int = None, home_screen=None, is_project=False) -> None:
        dialog_window = DialogWindow(self.database, self._)
        if is_project:
            dialog_window.draw_upsert_project(id_=id_, overview_table=self.table)
        else:
            dialog_window.language_window(home_screen=home_screen)

    def header_bar_detail_screen(self):
        full_header = QVBoxLayout()
        header = QHBoxLayout()
        head_top = QWidget()
        head_top.setProperty('class', 'header')
        title = QLabel('OTLWizard')
        title.setProperty('class', 'title')
        header.addWidget(title)
        return_button = QPushButton()
        return_button.setProperty('class', 'return-button')
        return_button.setIcon(qta.icon('mdi.arrow-left'))
        return_button.setText(self._('return_to_home_screen'))
        header.addWidget(return_button)
        header.setAlignment(return_button, Qt.AlignmentFlag.AlignLeft)
        settings = self.construct_settings_bar()
        header.addLayout(settings)
        header.setAlignment(settings, Qt.AlignmentFlag.AlignRight)

        head_top.setLayout(header)
        # head_top.setContentsMargins(0, 0, 0, 0)

        label = QLabel(self._('subtitle_page_1'))
        label.setProperty('class', 'subtitle')

        full_header.setSpacing(0)
        full_header.addWidget(head_top)
        full_header.addWidget(label)
        full_header.setContentsMargins(0, 0, 0, 0)
        self.setLayout(full_header)
        return return_button

    def reset_language(self, _):
        self._ = _
        self.create_new_project_button()
