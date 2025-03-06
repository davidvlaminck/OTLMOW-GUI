import os
from dataclasses import replace
from typing import List

import qtawesome as qta

from pathlib import Path

from PyQt6.QtGui import QFont
from PyQt6.QtWebEngineCore import QWebEngineSettings
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QVBoxLayout, QLabel, QWidget, QFrame, QHBoxLayout, QSizePolicy
from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLObject
from otlmow_visuals.PyVisWrapper import PyVisWrapper

from Domain import global_vars
from Domain.logger.OTLLogger import OTLLogger
from Domain.step_domain.RelationChangeDomain import RelationChangeDomain
from GUI.screens.general_elements.ButtonWidget import ButtonWidget
from GUI.screens.Screen import Screen

ROOT_DIR = Path(__file__).parent

# HTML_DIR = ROOT_DIR.parent.parent / 'img' / 'html'
HTML_DIR = Path.home() / 'OTLWizardProjects' / 'img' / 'html'

class DataVisualisationScreen(Screen):

    object_count_limit = 300

    def __init__(self, _):
        super().__init__()

        if not HTML_DIR.exists():
            os.makedirs(HTML_DIR,exist_ok=True)

        self.frame_layout_legend = None
        self.objects_in_memory = []
        self.refresh_needed_label = QLabel()
        self.container_insert_data_screen = QVBoxLayout()
        self._ = _
        self.view = QWebEngineView()
        self.too_many_objects_message = QLabel()
        self.color_label_title = QLabel()
        self.init_ui()




    def init_ui(self):
        self.container_insert_data_screen.addWidget(self.create_html_container())

        self.setLayout(self.container_insert_data_screen)

    def create_html_container(self):
        window = QWidget()
        window.setProperty('class', 'background-box')
        
        window_layout = QVBoxLayout()
        window_layout.setContentsMargins(0,0,0,0)
        
        html_loc = ROOT_DIR.parent.parent / 'img' / 'html' / "basic.html"
        self.view.setHtml(open(html_loc).read())
        self.view.settings().setAttribute(QWebEngineSettings.WebAttribute.ShowScrollBars, False)
        self.view.setContentsMargins(0, 0, 0, 0)
        self.view.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Expanding )

        self.too_many_objects_message.setVisible(False)

        self.color_label_title.setText(self._("relations legend") + ":")
        
        window_layout.addWidget(self.create_button_container())
        window_layout.addWidget(self.view,2)
        window_layout.addWidget(self.too_many_objects_message,2)
        window_layout.addWidget(self.color_label_title)
        window_layout.addWidget(self.create_color_legend())
        
        window.setLayout(window_layout)
        return window


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

    def create_button_container(self):
        frame = QFrame()
        frame_layout = QHBoxLayout()
        
        refresh_btn = ButtonWidget()
        refresh_btn.setIcon(qta.icon('mdi.refresh', color='white'))
        refresh_btn.setProperty('class', 'primary-button')
        refresh_btn.clicked.connect(lambda: self.reload_html())

        self.refresh_needed_label.setText(self._("The visualisation is outdated, refresh to see new changes"))
        self.refresh_needed_label.setStyleSheet('color:#DD1111;')
        # self.refresh_needed_label.setHidden(True)

        frame_layout.addWidget(refresh_btn)
        frame_layout.addWidget(self.refresh_needed_label)
        frame_layout.addStretch()
        frame_layout.setContentsMargins(0,0,0,0)
        
        frame.setLayout(frame_layout)
        return frame

    def reset_ui(self, _):
        super().reset_ui(_)
        # self.refresh_needed_label.setHidden(True)
        self._ = _
        self.color_label_title.setText(self._("relations legend") + ":")

    def reload_html(self):
        OTLLogger.logger.debug(
            f"Executing DataVisualisationScreen.reload_html() for project {global_vars.current_project.eigen_referentie}",
            extra={"timing_ref": f"reload_html_{global_vars.current_project.eigen_referentie}"})

        self.objects_in_memory = self.load_assets()
        self.fill_frame_layout_legend()
        self.create_html(objects_in_memory=self.objects_in_memory)
        object_count = len(self.objects_in_memory)
        OTLLogger.logger.debug(
            f"Executing DataVisualisationScreen.reload_html() for project {global_vars.current_project.eigen_referentie} ({object_count} objects)",
            extra={"timing_ref": f"reload_html_{global_vars.current_project.eigen_referentie}"})
        js_code = 'newOptions = {"physics":{"enabled":false}};\nnetwork.setOptions(newOptions);\n'
        self.view.page().runJavaScript(js_code)

    def load_assets(self) -> List[OTLObject]:
        assets = RelationChangeDomain.get_visualisation_instances()
        self.check_if_refresh_message_is_needed()
        return  assets

    def create_html(self, objects_in_memory:List[OTLObject]):
        object_count = len(objects_in_memory)
        if object_count > DataVisualisationScreen.object_count_limit:
            self.view.setVisible(False)
            if not self.too_many_objects_message.isVisible():
                self.too_many_objects_message.setVisible(True)

            translation = self._("There are too many assets and relations to create a visualisation.\nmaximum: {0}\ncurrent: {1}")
            self.too_many_objects_message.setText(translation.format(
                DataVisualisationScreen.object_count_limit,
                object_count))

        else:
            self.too_many_objects_message.setVisible(False)
            if not self.view.isVisible():
                self.view.setVisible(True)
            html_loc = HTML_DIR / "visuals.html"
            previous_cwd = os.getcwd()
            os.chdir(Path.home() / 'OTLWizardProjects')
            PyVisWrapper().show(list_of_objects=objects_in_memory,
                                html_path=Path(html_loc), launch_html=False)
            os.chdir(previous_cwd)

            self.modify_html(html_loc)

            self.view.setHtml(open(html_loc).read())

    def modify_html(cls, file_path: Path) -> None:
        with open(file_path) as file:
            file_data = file.readlines()

        replace_index = -1
        for index, line in enumerate(file_data):
            if "drawGraph();" in line:
                replace_index = index

        if replace_index > 0:
            file_data[replace_index] = file_data[replace_index].replace("drawGraph();","var network = drawGraph();")
            file_data.insert(replace_index,"var container = document.getElementById('mynetwork');\n")
            file_data.insert(replace_index+1,
                             "var isPhysicsOn = true;\n")
            file_data.insert(replace_index+2,
                             "function disablePhysics(){\n")
            file_data.insert(replace_index+3,"if(isPhysicsOn){")
            file_data.insert(replace_index+4,'newOptions={"physics":{"enabled":false}};\n')
            file_data.insert(replace_index+5,"network.setOptions(newOptions)};\n;")
            file_data.insert(replace_index + 6, "isPhysicsOn = false;\n};\n")
            file_data.insert(replace_index+7,"container.addEventListener('mouseover', disablePhysics);\n")
        with open(file_path, 'w') as file:
            for line in file_data:
                file.write(line)

    def opened(self):
        self.check_if_refresh_message_is_needed()

    def check_if_refresh_message_is_needed(self):
        self.refresh_needed_label.setHidden(RelationChangeDomain.is_visualisation_uptodate())


