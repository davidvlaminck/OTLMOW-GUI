from enum import Enum
from pathlib import Path

from PyQt6.QtWidgets import QDialog, QHBoxLayout, QPushButton

from Domain.ProjectFileManager import ProjectFileManager
from Domain.enums import Language
from Domain.language_settings import return_language

ROOT_DIR = Path(__file__).parent.parent

LANG_DIR = ROOT_DIR.parent / 'locale/'


class LanguageWindow:

    def __init__(self, language_settings):
        self._ = language_settings

    def language_window(self, main_window) -> None:
        dialog = QDialog()
        dialog.setModal(True)
        dialog.setWindowTitle(self._("change_language_title"))
        layout = QHBoxLayout()
        button_ned = QPushButton(self._("language_option_dutch"))
        button_eng = QPushButton(self._("language_option_english"))
        button_ned.clicked.connect(lambda: self.change_language(Language.DUTCH, dialog, main_window))
        button_eng.clicked.connect(lambda: self.change_language(Language.ENGLISH, dialog, main_window))
        layout.addWidget(button_ned)
        layout.addWidget(button_eng)
        dialog.setLayout(layout)
        dialog.show()
        dialog.exec()

    def change_language(self, lang: Enum, dialog: QDialog, main_window) -> None:
        ProjectFileManager.change_language_on_settings_file(lang)
        self._ = return_language(LANG_DIR, lang)
        main_window.reset_ui(self._)
        dialog.close()
