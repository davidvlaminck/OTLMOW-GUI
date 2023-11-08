from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

import qtawesome as qta

from GUI.dialog_window import DialogWindow


class HeaderBar(QFrame):
    def __init__(self, language, database, stacked_widget=None, table=None):
        super().__init__()
        self.new_project_button = QPushButton()
        self._ = language
        self.database = database
        self.table = table
        self.stacked_widget = stacked_widget
        self.return_button = QPushButton()
        self.subtitel = QLabel()
        self.save_button = QPushButton()

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
        self.new_project_button.setProperty('class', 'primary-button')
        self.new_project_button.clicked.connect(
            lambda: self.start_dialog_window(is_project=True))

    def construct_settings_bar(self):
        user_pref_container = QHBoxLayout()
        settings = QPushButton()
        settings.setIcon(qta.icon('mdi.cog',
                                  color="white"))
        settings.setProperty('class', 'settings')
        settings.clicked.connect(lambda: self.start_dialog_window())
        user_pref_container.addWidget(settings)
        help_widget = QPushButton()
        help_icon = qta.icon('mdi.help-circle',
                             color='white')
        help_widget.setIcon(help_icon)
        help_widget.setProperty('class', 'settings')
        user_pref_container.addWidget(help_widget)
        return user_pref_container

    def start_dialog_window(self, id_: int = None, is_project=False) -> None:
        dialog_window = DialogWindow(self.database, self._)
        if is_project:
            dialog_window.draw_upsert_project(id_=id_, overview_table=self.table)
        else:
            dialog_window.language_window(stacked_widget=self.stacked_widget)

    def header_bar_detail_screen(self, page: str):
        full_header = QVBoxLayout()
        header = QHBoxLayout()
        head_top = QWidget()
        head_top.setProperty('class', 'header')
        title = QLabel('OTLWizard')
        title.setProperty('class', 'title')
        header.addWidget(title)
        self.return_button.setProperty('class', 'return-button')
        self.return_button.setIcon(qta.icon('mdi.arrow-left',
                                            color='white'))
        self.return_button.setText(self._('return_to_home_screen'))
        header.addWidget(self.return_button)
        header.setAlignment(self.return_button, Qt.AlignmentFlag.AlignLeft)
        settings = self.construct_settings_bar()
        header.addLayout(settings)
        header.setAlignment(settings, Qt.AlignmentFlag.AlignRight)

        header_sub = QFrame()
        header_sub_layout = QHBoxLayout()
        header_sub.setProperty('class', 'sub-header')

        self.subtitel.setText(self._(page))
        self.subtitel.setProperty('class', 'subtitle')

        self.save_button.setIcon(qta.icon('mdi.content-save',
                                          color='white'))
        self.save_button.setText(self._('save_button'))
        self.save_button.setProperty('class', 'primary-button')

        header_sub_layout.addWidget(self.subtitel)
        header_sub_layout.addWidget(self.save_button)
        header_sub_layout.setAlignment(self.save_button, Qt.AlignmentFlag.AlignRight)

        header_sub.setLayout(header_sub_layout)

        head_top.setLayout(header)

        full_header.setSpacing(0)
        full_header.addWidget(head_top)
        full_header.addWidget(header_sub)
        full_header.setContentsMargins(0, 0, 0, 0)
        self.setLayout(full_header)
        return self.return_button

    def reset_ui(self, _, page=None):
        self._ = _
        self.new_project_button.setText(self._('new_project_button'))
        self.return_button.setText(self._('return_to_home_screen'))
        self.save_button.setText(self._('save_button'))
        self.subtitel.setText(self._(page))
