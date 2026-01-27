import gc
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
from PyQt6.QtWidgets import QVBoxLayout, QLabel, QWidget, QFrame, QHBoxLayout, QSizePolicy

import folium.features

from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLObject
from otlmow_visuals.PyVisWrapper import PyVisWrapper

from otlmow_gui.Domain import global_vars
from otlmow_gui.Domain.ProgramFileStructure import ProgramFileStructure
from otlmow_gui.Domain.logger.OTLLogger import OTLLogger
from otlmow_gui.Domain.step_domain.RelationChangeDomain import RelationChangeDomain
from otlmow_gui.GUI.dialog_windows.LoadingImageWindow import add_loading_screen
from otlmow_gui.GUI.screens.Map_elements.MapHelper import MapHelper
from otlmow_gui.GUI.screens.general_elements.ButtonWidget import ButtonWidget
from otlmow_gui.GUI.screens.Screen import Screen
from otlmow_gui.exception_handler.ExceptionHandlers import create_task_reraise_exception

ROOT_DIR = Path(__file__).parent

IMG_DIR = ProgramFileStructure.get_dynamic_library_path('img')

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


        # bol_icon = folium.features.CustomIcon(str(ROOT_DIR.parent.parent / "img"/"bol.png"),
        #                                      icon_size=(30, 30))
        # folium.Marker([lat, lng],
        #               # icon=bol_icon,
        #               # popup='red',
        #               ).add_to(self.folium_map)

    @pyqtSlot(str)
    def  receive_selection_id(self, message):
        """Receives click event data from JavaScript."""
        data = json.loads(message)  # Convert string back to dict
        asset_id = str(data["id"])

        RelationChangeDomain.set_selected_object_from_map(asset_id)
        RelationChangeDomain.update_frontend()

class MapScreen(Screen):

    object_count_limit = 300

    def __init__(self, _, parent_screen):
        super().__init__()

        if not HTML_DIR.exists():
            os.makedirs(HTML_DIR,exist_ok=True)
        self.map = None
        self.prev_selected_asset_id = None
        self.parent_screen = parent_screen

        self.frame_layout_legend = None
        self.refresh_needed_label = QLabel()
        self.container_insert_data_screen = QVBoxLayout()
        self._ = _
        self.webView = QWebEngineView()
        self.too_many_objects_message = QLabel()
        self.color_label_title = QLabel()
        self.init_ui()

        self.channel = QWebChannel()
        self.img_qurl = QUrl(pathlib.Path.home().drive + str(
            (IMG_DIR / "bol.png").absolute()).replace("\\","/"))

        # self.relation_change_screen_object_list_content_dict = self.load_assets()

        # map_path, self.map , self.map_id = MapHelper.create_html_map(self.relation_change_screen_object_list_content_dict, ROOT_DIR, HTML_DIR,self.prev_selected_asset_id)

        self.map = MapHelper.create_folium_map()
        map_path = MapHelper.get_map_html_save_path(HTML_DIR,ROOT_DIR)
        self.map.save(map_path)
        self.map_id = self.map.get_name()

        self.web_bridge = WebBridge(self.map)
        self.channel.registerObject("webBridge", self.web_bridge)

        # with open(map_path, 'r', encoding='utf-8') as f:
        #     html_content = f.read()
        # self.webView.setHtml(html_content)
        map_QUrl = QUrl.fromLocalFile(map_path.replace("\\", "/"))
        self.webView.setUrl(map_QUrl)
        OTLLogger.logger.debug(map_QUrl.toString())

        self.webView.page().setWebChannel(self.channel)


        # MapHelper.zoom_to_assets(web_view=self.webView,map_id= self.map_id,prev_selected_asset_id=self.prev_selected_asset_id)

        self.setLayout(self.container_insert_data_screen)



    def init_ui(self):
        self.container_insert_data_screen.addWidget(self.create_html_container())

    def create_html_container(self):
        window = QWidget()
        window.setProperty('class', 'background-box')
        
        window_layout = QVBoxLayout()
        window_layout.setContentsMargins(0,0,0,0)

        self.webView.settings().setAttribute(QWebEngineSettings.WebAttribute.ShowScrollBars, False)
        self.webView.setContentsMargins(0, 0, 0, 0)
        self.webView.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.webView.settings().setAttribute(
            QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        self.webView.settings().setAttribute(
            QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        self.too_many_objects_message.setVisible(False)

        self.color_label_title.setText(self._("relations legend") + ":")
        
        window_layout.addWidget(self.create_button_container())
        window_layout.addWidget(self.webView, 2)
        window_layout.addWidget(self.too_many_objects_message,2)
        
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
        refresh_btn.clicked.connect(lambda: self.start_async_reload())

        self.refresh_needed_label.setText(self._("The visualisation is outdated, refresh to see new changes"))
        self.refresh_needed_label.setStyleSheet('color:#DD1111;')

        frame_layout.addWidget(refresh_btn)
        frame_layout.addWidget(self.refresh_needed_label)
        frame_layout.addStretch()
        frame_layout.setContentsMargins(0,0,0,0)
        
        frame.setLayout(frame_layout)
        return frame

    def reset_ui(self, _):
        super().reset_ui(_)

        self._ = _
        self.color_label_title.setText(self._("relations legend") + ":")

    def start_async_reload(self):
        create_task_reraise_exception(self.reload_html())

    @add_loading_screen
    async def reload_html(self):
        OTLLogger.logger.debug(
            f"Executing MapScreen.reload_html() for project {global_vars.current_project.eigen_referentie}",
            extra={"timing_ref": f"reload_html_{global_vars.current_project.eigen_referentie}"})

        # throw away old data before loading the new
        self.relation_change_screen_object_list_content_dict = {}
        gc.collect()

        self.relation_change_screen_object_list_content_dict = self.load_assets()

        map_path, self.map , self.map_id = await MapHelper.create_html_map(self.relation_change_screen_object_list_content_dict,
                                                                     IMG_DIR, HTML_DIR,self.prev_selected_asset_id)
        self.web_bridge.folium_map = self.map
        # self.webView.setHtml(open(map_path).read())
        map_QUrl = QUrl.fromLocalFile(map_path.replace("\\", "/"))
        self.webView.setUrl(map_QUrl)
        OTLLogger.logger.debug(map_QUrl.toString())

        # self.webView.page().setWebChannel(self.channel)

        first_coordinate = None


        object_count = len(self.relation_change_screen_object_list_content_dict)
        OTLLogger.logger.debug(
            f"Executing MapScreen.reload_html() for project {global_vars.current_project.eigen_referentie} ({object_count} objects)",
            extra={"timing_ref": f"reload_html_{global_vars.current_project.eigen_referentie}"})


    def load_assets(self) -> dict:
        assets = RelationChangeDomain.get_current_relation_change_screen_object_list_content_dict()
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
            map_QUrl = QUrl.fromLocalFile(str(html_loc).replace("\\", "/"))
            self.webView.setUrl(map_QUrl)
            OTLLogger.logger.debug(map_QUrl.toString())
            # self.webView.setHtml(open(html_loc).read(),resources)

    def opened(self):
        self.check_if_refresh_message_is_needed()

    def check_if_refresh_message_is_needed(self):
        self.refresh_needed_label.setHidden(RelationChangeDomain.is_visualisation_uptodate())

    def activate_highlight_layer_by_id(self, asset_id:str):
        self.prev_selected_asset_id = asset_id
        MapHelper.activate_highlight_layer_by_id(asset_id,self.webView,self.map_id)

    def closeEvent(self, a0):
        if self.parent_screen:
            self.parent_screen.map_window = None
        super().closeEvent(a0)

