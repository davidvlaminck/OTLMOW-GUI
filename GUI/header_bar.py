from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton

import qtawesome as qta

from GUI.dialog_window import DialogWindow


class HeaderBar(QFrame):
    def __init__(self, _, db, homescreen, table):
        super().__init__()
        self.setFrameShadow(QFrame.Shadow.Plain)
        self.new_project_button = QPushButton()
        self._ = _
        self.database = db
        self.home_screen = homescreen
        self.table = table

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

    def reset_language(self, _):
        self._ = _
        self.create_new_project_button()
