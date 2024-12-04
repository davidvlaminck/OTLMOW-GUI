import logging
from typing import List

import qtawesome as qta

from pathlib import Path

from PyQt6.QtWebEngineCore import QWebEngineSettings
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QVBoxLayout, QLabel, QWidget, QFrame, QHBoxLayout
from otlmow_converter.OtlmowConverter import OtlmowConverter
from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLObject
from otlmow_visuals.PyVisWrapper import PyVisWrapper

from Domain.Project import Project
from Domain.RelationChangeDomain import RelationChangeDomain
from Domain.enums import FileState
from GUI.ButtonWidget import ButtonWidget
from Domain import global_vars
from GUI.Screens.Screen import Screen

ROOT_DIR = Path(__file__).parent

HTML_DIR = ROOT_DIR.parent.parent / 'img' / 'html'


class DataVisualisationScreen(Screen):

    def __init__(self, _):
        super().__init__()

        self.frame_layout_legend = None
        self.objects_in_memory = []

        self.container_insert_data_screen = QVBoxLayout()
        self._ = _
        self.view = QWebEngineView()
        self.color_label_title = QLabel()
        self.init_ui()


    def init_ui(self):
        self.container_insert_data_screen.addSpacing(10)
        self.container_insert_data_screen.addWidget(self.create_html_container())
        self.container_insert_data_screen.addStretch()
        self.setLayout(self.container_insert_data_screen)

    def create_html_container(self):
        window = QWidget()
        window.setProperty('class', 'background-box')
        window_layout = QVBoxLayout()

        html_loc = HTML_DIR / "basic.html"
        self.view.setHtml(open(html_loc).read())
        window_layout.addWidget(self.create_button_container())
        self.view.settings().setAttribute(QWebEngineSettings.WebAttribute.ShowScrollBars, False)
        window_layout.addWidget(self.view)
        self.color_label_title.setText(self._("relations legend") + ":")
        window_layout.addWidget(self.color_label_title)
        window_layout.addWidget(self.create_color_legend())
        window_layout.addSpacing(50)
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
        frame_layout.addSpacing(10)
        frame_layout.addStretch()
        frame.setLayout(frame_layout)
        return frame

    def reset_ui(self, _):
        self._ = _
        self.color_label_title.setText(self._("relations legend") + ":")

    def reload_html(self):
        self.objects_in_memory = self.load_assets()
        self.fill_frame_layout_legend()
        self.create_html(self.objects_in_memory)

        # self.view.reload()

    def load_assets(self) -> List[OTLObject]:
        objects_in_memory = RelationChangeDomain.get_quicksave_instances()
        return objects_in_memory

    def create_html(self, objects_in_memory:List[OTLObject]):
        html_loc = HTML_DIR / "visuals.html"
        PyVisWrapper().show(list_of_objects=objects_in_memory,
                            html_path=Path(html_loc), launch_html=False)
        self.view.setHtml(open(html_loc).read())
