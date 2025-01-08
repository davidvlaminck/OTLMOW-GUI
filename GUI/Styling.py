import logging
import os
from pathlib import Path

from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from Domain import global_vars
import qtawesome as qta

class Styling:
    #general styling
    light_stylesheet_filename = "custom_light.qss"
    dark_stylesheet_filename = "custom_dark.qss"

    #RelationScreen colors
    light_last_added_color = QColor("#d0ffcc")
    dark_last_added_color = QColor("#566b55")
    last_added_color = light_last_added_color

    #HeaderBar colors
    light_import_button_icon_color = QColor("#0E5A69")
    dark_import_button_icon_color = QColor("#FFFFFF")
    import_button_icon_color = light_import_button_icon_color

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


        if app.styleHints().colorScheme() == Qt.ColorScheme.Dark:
            style_filename = cls.dark_stylesheet_filename
            cls.last_added_color = cls.dark_last_added_color
            cls.import_button_icon_color = cls.dark_import_button_icon_color
        else:
            style_filename = cls.light_stylesheet_filename
            cls.last_added_color = cls.light_last_added_color
            cls.import_button_icon_color = cls.light_import_button_icon_color

        style_path = Path('style', style_filename)

        if meipass:  # when in .exe file
            style_path = Path(os.path.join(meipass, 'style', style_filename))
        elif not style_path.exists():
            style_path = Path('data', 'style', style_filename)

        with open(style_path, 'r') as file:
            app.setStyleSheet(file.read())

        style_path_str = str(style_path.absolute())
        logging.debug(f"style sheet found in: {style_path_str}")

        #update a few hardcoded colors
        if global_vars.otl_wizard:
            # res =global_vars.otl_wizard.main_window.home_screen.header.header.indexOf(global_vars.otl_wizard.main_window.home_screen.header.import_button)
            # logging.debug(f"import_button index : {res}")
            global_vars.otl_wizard.main_window.home_screen.header.import_button.setIcon(qta.icon("mdi.download",
                                            color=Styling.import_button_icon_color))
            # global_vars.otl_wizard.main_window.step1_tabwidget.header.import_button.setIcon(qta.icon("mdi.download",
            #                                 color=Styling.import_button_icon_color))
            # global_vars.otl_wizard.main_window.step2_tabwidget.header.import_button.setIcon(
            #     qta.icon("mdi.download",
            #              color=Styling.import_button_icon_color))
            # global_vars.otl_wizard.main_window.step_3_tabwidget.header.import_button.setIcon(
            #     qta.icon("mdi.download",
            #              color=Styling.import_button_icon_color))
            # global_vars.otl_wizard.main_window.step4_tabwidget.header.import_button.setIcon(
            #     qta.icon("mdi.download",
            #              color=Styling.import_button_icon_color))

