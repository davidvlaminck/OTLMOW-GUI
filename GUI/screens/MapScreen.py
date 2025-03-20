import json
import os
import pathlib

from typing import List

import qtawesome as qta

from pathlib import Path

from PyQt6.QtCore import pyqtSlot, QObject, QUrl
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtWebEngineCore import QWebEngineSettings
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QVBoxLayout, QLabel, QWidget, QFrame, QHBoxLayout, QSizePolicy, \
    QPushButton

import folium.features

from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLObject
from otlmow_visuals.PyVisWrapper import PyVisWrapper

from Domain import global_vars
from Domain.logger.OTLLogger import OTLLogger
from Domain.step_domain.RelationChangeDomain import RelationChangeDomain
from GUI.screens.Map_elements.MapHelper import MapHelper
from GUI.screens.general_elements.ButtonWidget import ButtonWidget
from GUI.screens.Screen import Screen

ROOT_DIR = Path(__file__).parent

HTML_DIR = Path.home() / 'OTLWizardProjects' / 'img' / 'html'


class WebBridge(QObject):
    """Bridge between JavaScript and Python using QWebChannel."""

    def __init__(self,folium_map: folium.Map):
        super().__init__()
        self.folium_map = folium_map


    @pyqtSlot(str)
    def receive_coordinates(self, message):
        """Receives click event data from JavaScript."""
        data = json.loads(message)  # Convert string back to dict
        lat = float(data["lat"])
        lng =float(data["lng"])
        print(f"Python received click at: Latitude: {lat}, Longitude: {lng}")

        # bol_icon = folium.features.CustomIcon(str(ROOT_DIR.parent.parent / "img"/"bol.png"),
        #                                      icon_size=(30, 30))
        # folium.Marker([lat, lng],
        #               # icon=bol_icon,
        #               # popup='red',
        #               ).add_to(self.folium_map)


class MapScreen(Screen):

    object_count_limit = 300

    def __init__(self, _):
        super().__init__()

        if not HTML_DIR.exists():
            os.makedirs(HTML_DIR,exist_ok=True)
        self.map = None
        self.frame_layout_legend = None
        self.objects_in_memory: list[OTLObject] = []
        self.relation_change_screen_object_list_content_dict = {}
        self.refresh_needed_label = QLabel()
        self.container_insert_data_screen = QVBoxLayout()
        self._ = _
        self.webView = QWebEngineView()
        self.too_many_objects_message = QLabel()
        self.color_label_title = QLabel()
        self.init_ui()

        self.channel = QWebChannel()
        self.img_qurl = QUrl(pathlib.Path.home().drive + str(
            (ROOT_DIR.parent.parent / "img" / "bol.png").absolute()).replace("\\","/"))

        map_path, self.map , self.map_id = MapHelper.create_html_map(self.objects_in_memory, ROOT_DIR,HTML_DIR)

        self.web_bridge = WebBridge(self.map)
        self.channel.registerObject("webBridge", self.web_bridge)
        # resources = QUrl().fromLocalFile((os.path.dirname(os.path.realpath(__file__))))
        # OTLLogger.logger.debug(f"resources: {resources.path()}")
        self.webView.setHtml(open(map_path).read())
        self.webView.page().setWebChannel(self.channel)

        button = QPushButton("add marker")
        button.clicked.connect(
            lambda event: MapHelper.add_marker(37.847205896010706, -122.50185012817384,self.map_id,self.webView))
        self.container_insert_data_screen.addWidget(button)


        self.setLayout(self.container_insert_data_screen)



    def init_ui(self):
        self.container_insert_data_screen.addWidget(self.create_html_container())

    def create_html_container(self):
        window = QWidget()
        window.setProperty('class', 'background-box')
        
        window_layout = QVBoxLayout()
        window_layout.setContentsMargins(0,0,0,0)
        
        # html_loc = ROOT_DIR.parent.parent / 'img' / 'html' / "basic.html"
        # self.view.setHtml(open(html_loc).read())
        self.webView.settings().setAttribute(QWebEngineSettings.WebAttribute.ShowScrollBars, False)
        self.webView.setContentsMargins(0, 0, 0, 0)
        self.webView.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.too_many_objects_message.setVisible(False)

        self.color_label_title.setText(self._("relations legend") + ":")
        
        window_layout.addWidget(self.create_button_container())
        window_layout.addWidget(self.webView, 2)
        window_layout.addWidget(self.too_many_objects_message,2)
        # window_layout.addWidget(self.color_label_title)
        # window_layout.addWidget(self.create_color_legend())
        
        window.setLayout(window_layout)
        return window


    def create_color_legend(self):

        frame = QFrame()
        self.frame_layout_legend = QHBoxLayout()
        self.fill_frame_layout_legend()
        frame.setLayout(self.frame_layout_legend)
        frame.setHidden(True)
        return frame

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
            f"Executing MapScreen.reload_html() for project {global_vars.current_project.eigen_referentie}",
            extra={"timing_ref": f"reload_html_{global_vars.current_project.eigen_referentie}"})

        self.objects_in_memory = self.load_assets()

        self.relation_change_screen_object_list_content_dict:dict = RelationChangeDomain.get_current_relation_change_screen_object_list_content_dict()

        map_path, self.map , self.map_id = MapHelper.create_html_map(self.objects_in_memory,ROOT_DIR,HTML_DIR)
        self.web_bridge.folium_map = self.map
        self.webView.setHtml(open(map_path).read())
        # self.webView.page().setWebChannel(self.channel)

        first_coordinate = None




        object_count = len(self.objects_in_memory)
        OTLLogger.logger.debug(
            f"Executing MapScreen.reload_html() for project {global_vars.current_project.eigen_referentie} ({object_count} objects)",
            extra={"timing_ref": f"reload_html_{global_vars.current_project.eigen_referentie}"})


    def load_assets(self) -> List[OTLObject]:
        assets = RelationChangeDomain.get_visualisation_instances()
        self.check_if_refresh_message_is_needed()
        return  assets

    def create_html(self, objects_in_memory:List[OTLObject]):
        object_count = len(objects_in_memory)
        if object_count > MapScreen.object_count_limit:
            self.webView.setVisible(False)
            if not self.too_many_objects_message.isVisible():
                self.too_many_objects_message.setVisible(True)

            translation = self._("There are too many assets and relations to create a visualisation.\nmaximum: {0}\ncurrent: {1}")
            self.too_many_objects_message.setText(translation.format(
                MapScreen.object_count_limit,
                object_count))

        else:
            self.too_many_objects_message.setVisible(False)
            if not self.webView.isVisible():
                self.webView.setVisible(True)
            html_loc = HTML_DIR / "visuals.html"
            previous_cwd = os.getcwd()
            os.chdir(Path.home() / 'OTLWizardProjects')
            PyVisWrapper().show(list_of_objects=objects_in_memory,
                                html_path=Path(html_loc), launch_html=False)
            os.chdir(previous_cwd)
            resources =  QUrl().fromLocalFile((os.path.dirname(os.path.realpath(__file__))))
            OTLLogger.logger.debug(f"resources: {resources.path()}")
            self.webView.setHtml(open(html_loc).read(),resources)

    def opened(self):
        self.check_if_refresh_message_is_needed()

    def check_if_refresh_message_is_needed(self):
        self.refresh_needed_label.setHidden(RelationChangeDomain.is_visualisation_uptodate())


