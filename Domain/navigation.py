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
from GUI.Screens.TemplateScreen import TemplateScreen
from GUI.TabWidget import TabWidget


class Navigation(QStackedWidget):
    def __init__(self, language):
        super().__init__()
        self._ = language
        self.fill_stacked_widget()

    def add_widget(self, widget: QWidget, has_stepper: bool = False):
        self.addWidget(widget)
        widget.stacked_widget = self
        widget.header.stacked_widget = self
        if has_stepper:
            widget.stepper_widget.stacked_widget = self
            widget.tab1.stacked_widget = self
            if hasattr(widget, 'tab2'):
                widget.tab2.stacked_widget = self

    def reset_ui(self, _):
        for i in range(self.count()):
            self.widget(i).reset_ui(_)

    def fill_stacked_widget(self):
        home_screen = HomeScreen(self._)
        step1 = TemplateScreen(self._)
        step1_tabwidget = TabWidget(page_nr=1, widget1=step1, description1="template", has_save_btn=False)
        step2 = InsertDataScreen(self._)
        step2_tabwidget = TabWidget(page_nr=2, widget1=step2, description1="insert_data", has_save_btn=False)
        step3_visuals = DataVisualisationScreen(self._)
        step3_data = AssetDataChangeScreen(self._)
        step3_relations = RelationChangeScreen(self._)
        step_3_tabwidget = TabWidget(page_nr=3, widget1=step3_visuals, description1="data visuals", widget2=step3_data,
                                     description2="data_change", widget3=step3_relations,
                                     description3="relation_change", has_save_btn=False)
        step4_export = ExportDataScreen(self._)
        step4_tabwidget = TabWidget(page_nr=4, widget1=step4_export, description1="export_data",
                                    has_save_btn=False)
        self.add_widget(home_screen)
        stepper_widgets = [step1_tabwidget, step2_tabwidget, step_3_tabwidget,
                           step4_tabwidget]
        self.add_tabs_with_stepper_to_widget(stepper_widgets)
        home_screen.table.stacked_widget = self
        step1.stacked_widget = self

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
