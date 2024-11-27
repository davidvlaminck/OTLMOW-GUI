import asyncio
import logging
from asyncio import sleep
from typing import List

from PyQt6.QtWidgets import QStackedWidget, QWidget

from GUI.Screens.AssetDataChangeScreen import AssetDataChangeScreen
from GUI.Screens.DataVisualisationScreen import DataVisualisationScreen
from GUI.Screens.ExportDataScreen import ExportDataScreen
from GUI.Screens.HomeScreen import HomeScreen
from GUI.Screens.InsertDataScreen import InsertDataScreen
from GUI.Screens.RelationChangeScreen import RelationChangeScreen
from GUI.Screens.Screen import Screen
from GUI.Screens.TemplateScreen import TemplateScreen
from GUI.TabWidget import TabWidget


class MainWindow(QStackedWidget):
    def __init__(self, language):
        super().__init__()
        self._ = language

        self.home_screen:Screen = HomeScreen(self._)
        self.step1:Screen = TemplateScreen(self._)
        self.step1_tabwidget:Screen = TabWidget(self._, page_nr=1, widget1=self.step1,
                                         description1="template",
                                         has_save_btn=False)
        self.step2:Screen = InsertDataScreen(self._)
        self.step2_tabwidget:Screen = TabWidget(self._, page_nr=2, widget1=self.step2,
                                         description1="insert_data",
                                         has_save_btn=False)
        self.step3_visuals:Screen = DataVisualisationScreen(self._)
        self.step3_data:Screen = AssetDataChangeScreen(self._)
        self.step3_relations:Screen = RelationChangeScreen(self._)
        self.step_3_tabwidget:Screen = TabWidget(self._, page_nr=3, widget1=self.step3_relations,
                                          description1="relation_change",
                                          widget2=self.step3_visuals,
                                          description2="data visuals",
                                          widget3=self.step3_data,
                                          description3="data_change",
                                          has_save_btn=False)
        self.step4_export:Screen = ExportDataScreen(self._)
        self.step4_tabwidget:Screen = TabWidget(self._, page_nr=4,
                                                widget1=self.step4_export,
                                                description1="export_data",
                                                has_save_btn=False)
        self.add_widget(self.home_screen)
        self.stepper_widgets:Screen = [self.step1_tabwidget, self.step2_tabwidget, self.step_3_tabwidget,
                           self.step4_tabwidget]
        self.add_tabs_with_stepper_to_widget(self.stepper_widgets)
        self.home_screen.table.main_window = self
        self.step1.main_window = self

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
        logging.debug("Window is closing...")

        # Stop the asyncio event loop
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Gather all pending tasks
            pending = asyncio.all_tasks(loop)
            for task in pending:
                task.cancel()  # Cancel all pending tasks

            loop.call_soon_threadsafe(loop.stop)
