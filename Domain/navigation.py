from typing import List

from PyQt6.QtWidgets import QStackedWidget, QWidget

from GUI.Screens.asset_data_change_screen import AssetDataChangeScreen
from GUI.Screens.data_visualisation_screen import DataVisualisationScreen
from GUI.Screens.export_data_screen import ExportDataScreen
from GUI.Screens.home_screen import HomeScreen
from GUI.Screens.insert_data_screen import InsertDataScreen
from GUI.Screens.relation_change_screen import RelationChangeScreen
from GUI.Screens.template_screen import TemplateScreen
from GUI.tab_widget import TabWidget


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
