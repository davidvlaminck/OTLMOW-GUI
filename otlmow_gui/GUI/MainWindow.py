import asyncio

from typing import List, Callable

from PyQt6.QtWidgets import QStackedWidget, QWidget

from otlmow_gui.Domain import global_vars
from otlmow_gui.Domain.logger.OTLLogger import OTLLogger
from otlmow_gui.Domain.step_domain.ExportDataDomain import ExportDataDomain
from otlmow_gui.Domain.step_domain.ExportFilteredDataSubDomain import ExportFilteredDataSubDomain
from otlmow_gui.Domain.step_domain.HomeDomain import HomeDomain
from otlmow_gui.Domain.step_domain.InsertDataDomain import InsertDataDomain
from otlmow_gui.Domain.step_domain.RelationChangeDomain import RelationChangeDomain
from otlmow_gui.Domain.step_domain.TemplateDomain import TemplateDomain
from otlmow_gui.GUI.dialog_windows.NotificationWindow import NotificationWindow
from otlmow_gui.GUI.dialog_windows.YesOrNoNotificationWindow import YesOrNoNotificationWindow
from otlmow_gui.GUI.dialog_windows.file_picker_dialog.SubsetLoadFilePickerDialog import \
    SubsetLoadFilePickerDialog

from otlmow_gui.GUI.screens.ExportDataScreen import ExportDataScreen
from otlmow_gui.GUI.screens.HomeScreen import HomeScreen
from otlmow_gui.GUI.screens.InsertDataScreen import InsertDataScreen
from otlmow_gui.GUI.screens.RelationChangeScreen import RelationChangeScreen
from otlmow_gui.GUI.screens.Screen import Screen
from otlmow_gui.GUI.screens.TemplateScreen import TemplateScreen
from otlmow_gui.GUI.header.TabWidget import TabWidget
from otlmow_gui.GUI.screens.DynamicDataVisualisationScreen import DynamicDataVisualisationScreen


class MainWindow(QStackedWidget):
    def __init__(self, language: Callable):
        super().__init__()
        self._ = language

        self.home_screen:HomeScreen = HomeScreen(self._)
        self.step1:TemplateScreen = TemplateScreen(self._)
        self.step1_tabwidget:TabWidget = TabWidget(self._, page_nr=1, widget1=self.step1,
                                         description1="template",
                                         has_save_btn=False)
        self.step2:InsertDataScreen = InsertDataScreen(self._)
        self.step2_tabwidget:TabWidget = TabWidget(self._, page_nr=2, widget1=self.step2,
                                         description1="insert_data",
                                         has_save_btn=False)
        # self.step3_visuals:DataVisualisationScreen = DataVisualisationScreen(self._)
        self.step3_visuals: DynamicDataVisualisationScreen = DynamicDataVisualisationScreen(self._)
        # self.step3_map:MapScreen = MapScreen(self._)
        # self.step3_data:AssetDataChangeScreen = AssetDataChangeScreen(self._)
        self.step3_relations:RelationChangeScreen = RelationChangeScreen(self._)
        self.step_3_tabwidget:TabWidget = TabWidget(self._, page_nr=3, widget1=self.step3_relations,
                                          description1="relation_change",
                                          widget2=self.step3_visuals,
                                          description2="data visuals",
                                          # widget3=self.step3_map,
                                          # description3="map",
                                          has_save_btn=False)
        self.step4_export:ExportDataScreen = ExportDataScreen(self._)
        self.step4_tabwidget:TabWidget = TabWidget(self._, page_nr=4,
                                                widget1=self.step4_export,
                                                description1="export_data",
                                                has_save_btn=False)
        self.add_widget(self.home_screen)
        self.stepper_widgets:list[Screen] = [self.step1_tabwidget, self.step2_tabwidget, self.step_3_tabwidget,
                           self.step4_tabwidget]
        self.add_tabs_with_stepper_to_widget(self.stepper_widgets)
        self.home_screen.table.main_window = self
        self.step1.main_window = self

        HomeDomain.init_static(self.home_screen)
        self.subset_picker = SubsetLoadFilePickerDialog(self._)

        # dummy translation so the pybabel system doesn't remove them
        self._("template")
        self._("insert_data")
        self._("data visuals")
        self._("data_change")
        self._("relation_change")
        self._("export_data")

    def add_widget(self, widget: QWidget, has_stepper: bool = False):
        self.addWidget(widget)
        widget.main_window = self
        widget.header.main_window = self
        if has_stepper:
            widget.stepper_widget.main_window = self
            widget.tab1.main_window = self
            if hasattr(widget, 'tab2'):
                widget.tab2.main_window = self

    def reset_ui(self, _):
        for i in range(self.count()):
            self.widget(i).reset_ui(_)

    def add_tabs_with_stepper_to_widget(self, tabs: List[TabWidget]):
        for tab in tabs:
            self.add_widget(tab, True)

    def closeEvent(self, event):
        # Handle window close event
        OTLLogger.logger.debug("Checking if data visualisation is saved")
        if (global_vars.current_project and
            not global_vars.current_project.get_saved_graph_status()):

            title = self._("unsaved_graph_changes_warning_title")
            text = self._("unsaved_graph_changes_warning_text")
            alt_yes_text = self._("Continue")
            alt_no_text = self._("Back")

            warning_dialog = YesOrNoNotificationWindow(message=text,
                                                       title=title,
                                                       alt_yes_text=alt_yes_text,
                                                       alt_no_text=alt_no_text)
            answer = warning_dialog.exec()

            if answer == 16384:  # QMessageBox.ButtonRole.YesRole:
                # # save graph before closing application
                # global_vars.otl_wizard.main_window.step3_visuals.save_in_memory_changes_to_html()
                # asyncio.sleep(1)

                # close without doing anything else
                pass
            elif answer == 65536: # QMessageBox.ButtonRole.NoRole:
                # # close without doing anything else
                # pass

                # don't close return to application
                event.ignore()
                return
            elif answer == 262144: # QMessageBox.ButtonRole.AbortRole also X-button
                # don't close return to application
                event.ignore()
                return

        OTLLogger.logger.debug("Window is closing...")
        # Stop the asyncio event loop
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Gather all pending tasks
            pending = asyncio.all_tasks(loop)
            for task in pending:
                task.cancel()  # Cancel all pending tasks

            loop.call_soon_threadsafe(loop.stop)


    def notify_user_of_excel_file_unavailable_error(self,e):
        message = self._(e.error_window_message_key)
        self.setWindowTitle(e.error_window_title_key)
        NotificationWindow("{0}:\n{1}".format(message, e.file_path))

    def go_to_project(self) -> None:
        self.setCurrentIndex(1)

    def enable_steps(self) -> None:
        self.reset_ui(self._)

    def setCurrentIndex(self, index):
        # if you go to the RelationChangeScreen or ExportDataScreen
        # the information is updated if the project has changed
        # if (index in [3, 4] and (not RelationChangeDomain.project or
        #                          RelationChangeDomain.project != global_vars.current_project)):
        # if (index in [3, 4] ):
        #     if RelationChangeDomain.cleared_data:
        #         RelationChangeDomain.init_static(project=global_vars.current_project)

        #everytime you go to a specific page update the frontend to always show the last Domain state
        if index == 1:
            TemplateDomain.update_frontend()
        elif index == 2:
            InsertDataDomain.update_frontend()
        elif index == 3:
            RelationChangeDomain.update_frontend()
            self.step3_visuals.opened()
        elif index == 4:
            ExportDataDomain.update_frontend()
            ExportFilteredDataSubDomain.update_frontend()

        super().setCurrentIndex(index)

    def update_color_scheme(self):
        # Import button on the home_screen
        self.home_screen.header.update_color_scheme()
        self.step3_relations.update_color_scheme()

        # the color of disabled steps in the step bar in a project
        self.step1_tabwidget.stepper_widget.enable_steps()
        self.step2_tabwidget.stepper_widget.enable_steps()
        self.step_3_tabwidget.stepper_widget.enable_steps()
        self.step4_tabwidget.stepper_widget.enable_steps()


    def show_blocking_yes_no_notification_window(self,text,title):
        msgbox = YesOrNoNotificationWindow(message=text,title=title)
        return msgbox.exec()