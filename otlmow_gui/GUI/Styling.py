import logging

from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from otlmow_gui.Domain import global_vars

from otlmow_gui.Domain.ProgramFileStructure import ProgramFileStructure


class Styling:
    #general styling
    light_stylesheet_filename = "custom_light.qss"
    dark_stylesheet_filename = "custom_dark.qss"

    #RelationScreen colors
    light_last_added_color = QColor("#d0ffcc")
    dark_last_added_color = QColor("#566b55")
    last_added_color = light_last_added_color

    #HeaderBar colors
    light_button_icon_color = QColor("#0E5A69")
    dark_button_icon_color = QColor("#FFFFFF")
    button_icon_color = light_button_icon_color

    @classmethod
    def applyStyling(cls,app:QApplication , meipass):
        """
        Apply the appropriate styling to the given application based on its color scheme. This method sets the application's stylesheet by loading the corresponding QSS file.

        :param app: The application instance to which the stylesheet will be applied.
        :type app: QApplication
        :param meipass: The path to the directory containing the executable, used to locate the stylesheet when running as a bundled application.
        :type meipass: str

        :return: None

        :raises FileNotFoundError: If the specified stylesheet file does not exist.

        :Examples:
            applyStyling(app, meipass)
        """

        style_library_name = "style"
        style_library_path = ProgramFileStructure.get_dynamic_library_path(style_library_name)

        if app.styleHints().colorScheme() == Qt.ColorScheme.Dark:
            style_filename = cls.dark_stylesheet_filename
            cls.last_added_color = cls.dark_last_added_color
            cls.button_icon_color = cls.dark_button_icon_color
        else:
            style_filename = cls.light_stylesheet_filename
            cls.last_added_color = cls.light_last_added_color
            cls.button_icon_color = cls.light_button_icon_color

        style_path = style_library_path / style_filename

        with open(style_path, 'r') as file:
            app.setStyleSheet(file.read())

        style_path_str = str(style_path.absolute())
        logging.debug(f"style sheet found in: {style_path_str}")

        #update a few hardcoded colors
        if global_vars.otl_wizard:
            global_vars.otl_wizard.main_window.update_color_scheme()


