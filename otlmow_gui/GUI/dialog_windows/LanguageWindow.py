from pathlib import Path
from typing import Callable

from PyQt6.QtWidgets import QDialog, QHBoxLayout, QPushButton, QStackedWidget

from otlmow_gui.Domain.enums import Language
from otlmow_gui.Domain.Settings import Settings
from otlmow_gui.GUI.dialog_windows.NotificationWindow import NotificationWindow

ROOT_DIR = Path(__file__).parent.parent

LANG_DIR = ROOT_DIR.parent / 'locale/'


class LanguageWindow(QDialog):

    def __init__(self, language_settings: Callable, main_window: QStackedWidget):
        super().__init__()
        self._ = language_settings
        self.setModal(True)
        self.setWindowTitle(self._("change_language_title"))

        layout = QHBoxLayout()

        button_ned = QPushButton(self._("language_option_dutch"))
        button_eng = QPushButton(self._("language_option_english"))
        button_ned.clicked.connect(lambda: self.change_language(lang= Language.DUTCH, main_window= main_window))
        button_eng.clicked.connect(lambda: self.change_language(lang= Language.ENGLISH, main_window= main_window))
        layout.addWidget(button_ned)
        layout.addWidget(button_eng)
        self.setLayout(layout)

    def change_language(self, lang: Language, main_window: QStackedWidget) -> None:
        """
        Changes the application's language and updates the user interface accordingly.

        This method updates the language setting in the application's settings file, retrieves the
        corresponding translation Callable, and resets the main window's UI to reflect the new
        language. Finally, it closes the language selection window.

        :param lang: The new language to be set, represented as a Language enum.
        :type lang: Language
        :param main_window: The main window instance to be updated.
        :type main_window: QStackedWidget

        :return: None
        """
        Settings.change_language_on_settings_file(lang)
        restart_request_dialog = NotificationWindow(message=self._("Please restart the application to apply the changes"),
                                                    title=self._("Restart required"))
        restart_request_dialog.exec()
        # settings = Settings.get_or_create_settings_file()
        # self._ = GlobalTranslate(settings, LANG_DIR).get_all()
        # main_window.reset_ui(self._)
        self.close()
