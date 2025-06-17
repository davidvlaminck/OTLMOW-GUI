import json
import re
import sys
import time
from pathlib import Path
from typing import List

import qtawesome as qta

from PyQt6.QtWebEngineCore import QWebEngineSettings
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLabel, QComboBox, QSizePolicy, \
    QWidget, QFrame, QHBoxLayout
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtCore import QObject, pyqtSlot, QUrl
from html2image import Html2Image
from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLObject
from otlmow_visuals.PyVisWrapper import PyVisWrapper

from Domain import global_vars
from Domain.logger.OTLLogger import OTLLogger
from Domain.step_domain.RelationChangeDomain import RelationChangeDomain
from GUI.screens.DataVisualisation_elements.VisualisationHelper import VisualisationHelper
from GUI.screens.Screen import Screen
from GUI.screens.general_elements.ButtonWidget import ButtonWidget


class Backend(QObject):

    def __init__(self, parent_screen):
        super().__init__()
        self.parent_screen = parent_screen

    @pyqtSlot(str)
    def receive_new_node_data(self, message):
        """Receives receive_new_node_data from JavaScript."""
        data = json.loads(message)  # Convert string back to dict

        test_json_path = global_vars.current_project.get_current_visuals_folder_path() / "new_nodes.json"
        with open(test_json_path, 'w') as json_file:
            json.dump(data, json_file)

        new_node_data_str = json.dumps(data)

        # correcting the formatting of the title attribute of the node
        new_node_data_str = new_node_data_str.replace('"htmlTitle(\\', 'htmlTitle(')
        new_node_data_str = new_node_data_str.replace('</div>\\")"','</div>")')

        self.parent_screen.save_html(self.parent_screen.get_current_html_path(),new_node_data=new_node_data_str)

    @pyqtSlot(str)
    def receive_coordinates(self, message):
        """Receives click event data from JavaScript."""
        data = json.loads(message)  # Convert string back to dict
        lat = float(data["lat"])
        lng = float(data["lng"])

        OTLLogger.logger.debug(f"Received coordinates from javascript! ({lat},{lng})")


    @pyqtSlot(str)
    def receiveMessage(self, msg):
        print(f"Message from JS: {msg}")

class TestDataVisualisationScreen(Screen):

    def __init__(self, _):
        super().__init__()
        # self.setWindowTitle("PyQt6 QWebEngine QWebChannel Example")
        # self.resize(800, 600)

        # data variables
        self.objects_in_memory = []
        self.std_vis_wrap = None

        # translation model
        self._ = _

        #smaller support widgets
        self.refresh_needed_label = QLabel()
        self.visualisation_mode = QComboBox()
        self.too_many_objects_message = QLabel()
        self.relation_color_legend_title = QLabel()



        self.main_layout = QVBoxLayout()
        self.main_widget = self.create_main_widget()
        self.main_layout.addWidget(self.main_widget)
        self.setLayout(self.main_layout)

    def create_main_widget(self):
        main_widget = QWidget()
        main_widget.setProperty('class', 'background-box')

        window_layout = QVBoxLayout()
        window_layout.setContentsMargins(0, 0, 0, 0)

        # Set up the channel and backend for communication from js to python backend
        self.channel = QWebChannel()
        self.backend = Backend(parent_screen=self)
        self.channel.registerObject("backend", self.backend)

        # main QWebEngineView widget
        self.view = QWebEngineView(self)
        self.view.page().setWebChannel(self.channel)
        self.view.settings().setAttribute(QWebEngineSettings.WebAttribute.ShowScrollBars, False)
        self.view.setContentsMargins(0, 0, 0, 0)
        self.view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.too_many_objects_message.setVisible(False)

        self.relation_color_legend_title.setText(self._("relations legend") + ":")

        window_layout.addWidget(self.create_button_container())
        window_layout.addWidget(self.view, 2)
        window_layout.addWidget(self.too_many_objects_message, 2)
        window_layout.addWidget(self.relation_color_legend_title)
        window_layout.addWidget(self.create_color_legend())

        main_widget.setLayout(window_layout)
        return main_widget

    def create_button_container(self):
        frame = QFrame()
        frame_layout = QHBoxLayout()

        refresh_btn = ButtonWidget()
        refresh_btn.setIcon(qta.icon('mdi.refresh', color='white'))
        refresh_btn.setProperty('class', 'primary-button')
        refresh_btn.clicked.connect(lambda: self.recreate_html(self.get_current_html_path()))

        save_btn = ButtonWidget()
        # see all qta mdi icon options in: https://cdn.jsdelivr.net/npm/@mdi/font@5.9.55/preview.html
        save_btn.setIcon(qta.icon('mdi.content-save', color='white'))
        save_btn.setProperty('class', 'primary-button')
        save_btn.clicked.connect(lambda: self.save_as_png())
        self.refresh_needed_label.setText(
            self._("The visualisation is outdated, refresh to see new changes"))
        self.refresh_needed_label.setStyleSheet('color:#DD1111;')
        # self.refresh_needed_label.setHidden(True)

        self.visualisation_mode.addItems(["standaard visualisatie",
                                          "alternatief 0 visualisatie",
                                          "alternatief 1 visualisatie",
                                          "alternatief 2 visualisatie",
                                          "alternatief 3 visualisatie",
                                          "alternatief 4 visualisatie",
                                          "alternatief 5 visualisatie",
                                          "alternatief 6 visualisatie",
                                          "alternatief 7 visualisatie",
                                          "vorige"])

        frame_layout.addWidget(refresh_btn)
        frame_layout.addWidget(save_btn)
        frame_layout.addWidget(self.visualisation_mode)
        frame_layout.addWidget(self.refresh_needed_label)
        frame_layout.addStretch()
        frame_layout.setContentsMargins(0, 0, 0, 0)

        frame.setLayout(frame_layout)
        return frame

    def create_color_legend(self):

        frame = QFrame()
        self.frame_layout_legend = QHBoxLayout()
        self.fill_frame_layout_legend()
        frame.setLayout(self.frame_layout_legend)
        return frame

    def fill_frame_layout_legend(self):
        for i in reversed(range(self.frame_layout_legend.count())):
            self.frame_layout_legend.itemAt(i).widget().deleteLater()

        relatie_color_dict = PyVisWrapper().relatie_color_dict

        typeURIs_in_memory = [object_in_memory.typeURI for object_in_memory in
                              self.objects_in_memory]
        for relatie, color in relatie_color_dict.items():

            if relatie not in typeURIs_in_memory:
                continue

            color_label = QLabel()
            label = QLabel()
            relatie_name = relatie.split('#')[-1]
            label.setText(relatie_name)
            color_label.setStyleSheet(f"background-color: #{color}")
            self.frame_layout_legend.addWidget(color_label)
            self.frame_layout_legend.addWidget(label)

    def reset_ui(self, _):
        pass

    def load_html(self, html_loc):
        with open(html_loc) as html_file:
            self.view.setHtml( html_file.read(), QUrl("qrc:///"))

        global_vars.current_project.load_visualisation_uptodate_state()

        if not self.std_vis_wrap:
            self.std_vis_wrap = VisualisationHelper.get_std_vis_wrap_instance()

    def recreate_html(self,html_path:Path):
        OTLLogger.logger.debug(
            f"Executing DataVisualisationScreen.reload_html() for project {global_vars.current_project.eigen_referentie}",
            extra={"timing_ref": f"reload_html_{global_vars.current_project.eigen_referentie}"})

        self.objects_in_memory = self.load_assets()

        global_vars.current_project.visualisation_uptodate.reset_full_state()
        global_vars.current_project.save_visualisation_uptodate_state()

        self.refresh_needed_label.setHidden(True)

        self.fill_frame_layout_legend()

        object_count = len(self.objects_in_memory)

        if object_count > VisualisationHelper.object_count_limit:
            # do not draw the visualisation when there are too many assets
            self.view.setVisible(False)
            if not self.too_many_objects_message.isVisible():
                self.too_many_objects_message.setVisible(True)

            translation = self._(
                "There are too many assets and relations to create a visualisation.\nmaximum: {0}\ncurrent: {1}")
            self.too_many_objects_message.setText(translation.format(
                VisualisationHelper.object_count_limit,
                object_count))

        else:
            # do not draw the visualisation when there are too many assets
            self.too_many_objects_message.setVisible(False)
            if not self.view.isVisible():
                self.view.setVisible(True)

            self.std_vis_wrap = VisualisationHelper.create_html(html_loc= html_path,
                                                                objects_in_memory=self.objects_in_memory,
                                                                vis_mode=self.visualisation_mode.currentText())
            self.load_html(html_path)

        object_count = len(self.objects_in_memory)
        OTLLogger.logger.debug(
            f"Executing DataVisualisationScreen.reload_html() for project {global_vars.current_project.eigen_referentie} ({object_count} objects)",
            extra={"timing_ref": f"reload_html_{global_vars.current_project.eigen_referentie}"})



    def get_current_html_path(self):
        return global_vars.current_project.get_current_visuals_html_path()

    def opened(self):
        if self.changed_project_bool:
            self.changed_project()

        elif not RelationChangeDomain.is_visualisation_uptodate():
            if self.visualisation_mode.currentText() != "standaard visualisatie":
                self.refresh_needed_label.setHidden(False)
                return

            to_add_list = global_vars.current_project.visualisation_uptodate.get_to_be_inserted_relations()
            to_remove_list = global_vars.current_project.visualisation_uptodate.get_to_be_removed_relations()

            VisualisationHelper.add_new_relations(to_add_list=to_add_list,
                                   vis_wrap=self.std_vis_wrap, webview=self.view)
            VisualisationHelper.remove_relations(to_remove_list=to_remove_list,
                                  vis_wrap=self.std_vis_wrap, webview=self.view)

            global_vars.current_project.visualisation_uptodate.reset_relations_uptodate()

            if global_vars.current_project.visualisation_uptodate.get_clear_all():
                self.refresh_needed_label.setHidden(False)
                return

        self.refresh_needed_label.setHidden(True)

    def changed_project(self):
        html_path: Path = self.get_current_html_path()
        if html_path.exists():
            self.load_html(html_path)
            global_vars.current_project.visualisation_uptodate.reset_relations_uptodate()
        else:
            self.recreate_html(html_path)

        self.changed_project_bool = False

    def load_assets(self) -> List[OTLObject]:
        assets = RelationChangeDomain.get_visualisation_instances()
        return  assets

    def save_as_png(self):

        # TODO: fix the code to create the png form html (currently hangs the program)
        # hti = Html2Image(output_path=global_vars.current_project.get_project_local_path(),
        #                  size=(1920, 1080 ), )
        # hti.screenshot(
        #     html_file=str(self.get_current_html_path()),
        #     save_as="screenshot.png",
        #     size=(1920, 1080 )
        # )

        js_code = 'sendCurrentNodesDataToPython();\n'
        self.view.page().runJavaScript(js_code)



    def save_html(cls, file_path: Path, new_node_data:str) -> None:
        with open(file_path) as file:
            file_data = file.read()

        # pattern = re.compile(
        #     r'nodes\s*=\s*new\s+vis\.DataSet\(\[\{([\s\S]*?)\}\]\);',
        #     re.DOTALL
        # )

        pattern = re.compile(
            r'nodes\s*=\s*new\s+vis\.DataSet\(([\s\S]*?)\);',
            re.DOTALL
        )

        m = pattern.search(file_data)
        if m:
            old_node_data = m.group(1)
            # print(inner_blob)

            with open(file_path.parent / "match_results.txt", 'w') as file:
                file.write(old_node_data)


            file_data = file_data.replace(old_node_data, new_node_data)
            file_data = file_data.replace("\"hierarchical\": {\"enabled\": true",
                                          "\"hierarchical\": {\"enabled\": false")
            new_physics_setting = ", \"physics\": {\"enabled\": false, "
            if new_physics_setting not in file_data:
                file_data = file_data.replace(", \"physics\": {",new_physics_setting)


            with open(file_path,mode="w") as file:
                file.write(file_data)