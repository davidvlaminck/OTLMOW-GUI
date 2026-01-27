import asyncio
import os
import subprocess
import webbrowser
from asyncio import sleep
from datetime import datetime
from pathlib import Path

import qtawesome as qta
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QTransform
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget, QMenu

from otlmow_gui.Domain import global_vars
from otlmow_gui.Domain.ProgramFileStructure import ProgramFileStructure
from otlmow_gui.Domain.logger.OTLLogger import OTLLogger
from otlmow_gui.Domain.project.Project import Project
from otlmow_gui.Domain.step_domain.HomeDomain import HomeDomain
from otlmow_gui.GUI.Styling import Styling
from otlmow_gui.GUI.dialog_windows.NotificationWindow import NotificationWindow
from otlmow_gui.GUI.dialog_windows.ProjectExistsError import ProjectExistsError
from otlmow_gui.GUI.dialog_windows.file_picker_dialog.ProjectImportFilePickerDialog import \
    ProjectImportFilePickerDialog
from otlmow_gui.GUI.screens.general_elements.ButtonWidget import ButtonWidget
from otlmow_gui.GUI.dialog_windows.LanguageWindow import LanguageWindow
from otlmow_gui.GUI.dialog_windows.MenuActionsWindow import MenuActionsWindow

from otlmow_gui.GUI.dialog_windows.UpsertProjectWindow import UpsertProjectWindow
from otlmow_gui.GUI.screens.Home_elements.OverviewTable import OverviewTable


IMG_DIR = ProgramFileStructure.get_dynamic_library_path('img')

class HeaderBar(QFrame):

    def __init__(self, language, main_window=None, table: OverviewTable = None, has_save_btn: bool = True):
        super().__init__()
        self.new_project_button = ButtonWidget()
        self._ = language
        self.table = table
        self.main_window = main_window
        self.return_button = ButtonWidget()
        self.subtitle = QLabel()
        self.save_button = ButtonWidget()
        self.import_button = ButtonWidget()
        self.reference_title = QLabel()
        self.has_save_btn = has_save_btn
        self.loading_icon = QLabel()
        self.saving_msg = QLabel()
        self.animation_event_loop = None
        self.pixmap_icon = None
        self.initialised = False
        self.quick_save_animation_task = None
        self.header = None
        self.import_project_dialog_window: ProjectImportFilePickerDialog = (
            ProjectImportFilePickerDialog(self._))

    def construct_header_bar(self):
        self.setProperty('class', 'header')
        self.header = QHBoxLayout()
        title = QLabel('OTLWizard')
        title.setProperty('class', 'title')
        self.header.addWidget(title)
        self.header.addSpacing(30)
        self.create_new_project_button()
        self.create_import_button()
        self.header.addWidget(self.new_project_button)
        self.header.addWidget(self.import_button)
        # self.header.addWidget(self.create_loading_icon())
        self.header.addStretch()
        self.header.setAlignment(self.new_project_button, Qt.AlignmentFlag.AlignLeft)
        user_settings = self.construct_settings_bar()
        self.header.addLayout(user_settings)
        self.header.setAlignment(user_settings, Qt.AlignmentFlag.AlignRight)
        self.setLayout(self.header)

    def start_event_loop(self):

        self.animation_event_loop = asyncio.get_event_loop()
        if self.quick_save_animation_task and self.animation_event_loop.is_running():
            self.quick_save_animation_task.cancel()

        self.quick_save_animation_task = self.animation_event_loop.create_task(self.rotate_icon())

    def create_new_project_button(self):
        self.new_project_button.setIcon(qta.icon("mdi.plus",
                                                 color='white'))
        self.new_project_button.setText(self._('new_project_button'))
        self.new_project_button.setProperty('class', 'new-project-btn')
        self.new_project_button.clicked.connect(
            lambda: self.start_dialog_window(is_project=True))

    def create_loading_icon(self):
        self.pixmap_icon = QPixmap(str(IMG_DIR / 'wizard.ico'))

        header_sub = QFrame()
        header_sub_layout = QHBoxLayout()

        self.loading_icon.setPixmap(self.pixmap_icon )
        self.loading_icon.setFixedHeight(30)
        self.loading_icon.setFixedWidth(30)
        self.loading_icon.setScaledContents(True)
        self.saving_msg.setText("Unsaved")
        self.saving_msg.setProperty("class","white_text")
        header_sub_layout.addWidget(self.loading_icon)
        header_sub_layout.addWidget(self.saving_msg)
        header_sub_layout.setContentsMargins(0, 0, 0, 0)
        header_sub.setLayout(header_sub_layout)

        return header_sub

    async def rotate_icon(self):
        angle = 0
        count = 0
        time_string = datetime.now().strftime("%H:%M")
        self.saving_msg.setText("Saving")
        while count < (360/10): # about 1.8 seconds
            transform = QTransform()
            angle += 10
            count +=1
            angle = angle % 360
            transform.rotate(angle)
            rotation_pixmap = self.pixmap_icon.transformed(transform)
            self.loading_icon.setPixmap(rotation_pixmap)
            if(count == 20):
                self.saving_msg.setText(f"Last Saved at {time_string}")
            # elif(count%5 == 3):
            #     self.saving_msg.setProperty("class", "black_text")

            await sleep(0.05)

        self.loading_icon.setPixmap(self.pixmap_icon)
        # self.saving_msg.setText(f"Last Saved at {time_string}")

    def construct_settings_bar(self):
        user_pref_container = QHBoxLayout()
        settings = ButtonWidget()
        settings.setIcon(qta.icon('mdi.cog',
                                  color="white"))
        settings.setProperty('class', 'settings')
        settings.clicked.connect(lambda: self.start_dialog_window())
        user_pref_container.addWidget(settings)
        help_widget = ButtonWidget()
        menu = self.construct_menu()
        help_widget.setMenu(menu)
        help_icon = qta.icon('mdi.help-circle',
                             color='white')
        help_widget.setIcon(help_icon)
        help_widget.setProperty('class', 'settings')
        user_pref_container.addWidget(help_widget)
        return user_pref_container

    def construct_menu(self):
        menu = QMenu()
        self.help_action = menu.addAction(self._('help'))
        self.help_action.triggered.connect(lambda: self.open_wiki())
        self.about_action = menu.addAction(self._('about'))
        self.about_action.triggered.connect(lambda: MenuActionsWindow(self._).create_about_window())
        self.report_action = menu.addAction(self._('report error'))
        self.report_action.triggered.connect(lambda: MenuActionsWindow(self._).create_error_report_window())
        self.logs_action = menu.addAction(self._('logs'))
        self.logs_action.triggered.connect(self.open_logs_folder)

        return menu

    @classmethod
    def open_logs_folder(cls):
        logs_folderpath = Path.home() / 'OTLWizardProjects' / 'logs'
        log_filename_list = os.listdir(logs_folderpath)
        if log_filename_list:
            log_filename_list.sort(reverse=True)
            last_log_filepath = logs_folderpath / log_filename_list[0]
            command = f'explorer /select,"{last_log_filepath}"'
            OTLLogger.logger.debug(f"open logs : {command}")
            subprocess.Popen(command)
        else:
            command = f'explorer /select,"{logs_folderpath}"'
            OTLLogger.logger.debug(f"open logs : {command}")
            subprocess.Popen(command)

    @staticmethod
    def open_wiki():
        webbrowser.open('https://github.com/davidvlaminck/OTLMOW-GUI/wiki')

    def start_dialog_window(self, id_: int = None, is_project=False) -> None:
        if is_project:
            dialog = UpsertProjectWindow(language_settings=self._,project=id_)
        else:
            dialog = LanguageWindow(language_settings=self._,main_window=self.main_window)
        dialog.exec()

    def header_bar_detail_screen(self):
        if self.initialised:
            return self.return_button

        self.return_button = ButtonWidget()
        full_header = QVBoxLayout()
        header = QHBoxLayout()
        head_top = QWidget()
        head_top.setProperty('class', 'header')
        title = QLabel('OTLWizard')
        title.setProperty('class', 'title')
        header.addWidget(title)
        header.addSpacing(20)
        self.return_button.setProperty('class', 'return-button')
        self.return_button.setIcon(qta.icon('mdi.arrow-left',
                                            color='#B35F35'))
        self.return_button.setText(self._('return_to_home_screen'))
        if global_vars.current_project is not None:
            self.reference_title.setText(global_vars.current_project.eigen_referentie)
        else:
            self.reference_title.setText("")
        self.reference_title.setProperty('class', 'project-title')
        header.addWidget(self.reference_title)
        header.addWidget(self.create_loading_icon())
        header.addStretch()
        header.setAlignment(self.return_button, Qt.AlignmentFlag.AlignLeft)
        settings = self.construct_settings_bar()
        header.addLayout(settings)
        header.setAlignment(settings, Qt.AlignmentFlag.AlignRight)

        header_sub = QFrame()
        header_sub_layout = QHBoxLayout()
        header_sub.setProperty('class', 'sub-header')
        if self.has_save_btn:
            self.save_button.setIcon(qta.icon('mdi.content-save',
                                              color='white'))
            self.save_button.setText(self._('save_button'))
            self.save_button.setProperty('class', 'primary-button')

        header_sub_layout.addWidget(self.return_button, alignment=Qt.AlignmentFlag.AlignLeft)
        if self.has_save_btn:
            header_sub_layout.addWidget(self.save_button)
            header_sub_layout.setAlignment(self.save_button, Qt.AlignmentFlag.AlignRight)

        header_sub.setLayout(header_sub_layout)

        head_top.setLayout(header)

        full_header.setSpacing(0)
        full_header.addWidget(head_top)
        full_header.addWidget(header_sub)
        full_header.setContentsMargins(0, 0, 0, 0)
        self.setLayout(full_header)
        self.initialised = True
        return self.return_button



    def create_import_button(self):
        self.set_import_icon(self.import_button)
        self.import_button.setText(self._("import"))
        self.import_button.setProperty('class', 'import-button')
        self.import_button.clicked.connect(
            lambda: self.import_project_window())

    def import_project_window(self):
        selected_file_path_list  = self.import_project_dialog_window.summon()

        if not selected_file_path_list or not selected_file_path_list[0]:
            return

        project = None
        try:
            project = Project.import_project(selected_file_path_list[0])
        except ProjectExistsError as e:
            notification = NotificationWindow(title=self._("Project bestaat al"),
                                              message=self._("Project naam: \"{project_naam}\" bestaat al.\nVerwijder het bestaande project en importeer opnieuw".format(project_naam=e.eigen_referentie)))
            notification.exec()
        except Exception as e:
            # TODO: proper error messag when project fails to import
            raise e


        if project is None:
            return
        HomeDomain.projects[project.eigen_referentie] = project
        global_vars.otl_wizard.main_window.home_screen.last_added_ref = project.eigen_referentie

        OTLLogger.logger.debug("Projects global")
        for eigen_ref in HomeDomain.projects.keys():
            OTLLogger.logger.debug(eigen_ref)

        HomeDomain.reload_projects()
        HomeDomain.update_frontend()
        # self.table.reset_ui(self._)

    def reset_ui(self, _):
        self._ = _
        self.new_project_button.setText(self._('new_project_button'))
        self.return_button.setText(self._('return_to_home_screen'))
        self.save_button.setText(self._('save_button'))
        self.import_button.setText(self._("import"))
        self.help_action.setText(self._('help'))
        self.about_action.setText(self._('about'))
        self.report_action.setText(self._('report error'))
        if global_vars.current_project is not None:
            self.reference_title.setText(global_vars.current_project.eigen_referentie)
        else:
            self.reference_title.setText("")

    def set_import_icon(self, button: ButtonWidget):
        button.setIcon(qta.icon("mdi.download",
                                            color=Styling.button_icon_color))
    def update_color_scheme(self):
        self.set_import_icon(self.import_button)