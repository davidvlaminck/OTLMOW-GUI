import os
from typing import List

import qtawesome as qta

from pathlib import Path

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

    def __init__(self, _):
        super().__init__()

        if not HTML_DIR.exists():
            os.makedirs(HTML_DIR,exist_ok=True)

        self.frame_layout_legend = None
        self.objects_in_memory = []

        self.container_insert_data_screen = QVBoxLayout()
        self._ = _
        self.view = QWebEngineView()
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
       
        self.color_label_title.setText(self._("relations legend") + ":")
        
        window_layout.addWidget(self.create_button_container())
        window_layout.addWidget(self.view,2)
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
        
        frame_layout.addWidget(refresh_btn)
        frame_layout.addStretch()
        frame_layout.setContentsMargins(0,0,0,0)
        
        frame.setLayout(frame_layout)
        return frame

    def reset_ui(self, _):
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

    def load_assets(self) -> List[OTLObject]:
        return RelationChangeDomain.get_quicksave_instances()

    def create_html(self, objects_in_memory:List[OTLObject]):
        html_loc = HTML_DIR / "visuals.html"
        previous_cwd = os.getcwd()
        os.chdir(Path.home() / 'OTLWizardProjects')
        PyVisWrapper().show(list_of_objects=objects_in_memory,
                            html_path=Path(html_loc), launch_html=False)
        os.chdir(previous_cwd)
        self.view.setHtml(open(html_loc).read())
