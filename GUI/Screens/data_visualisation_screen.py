import logging

import qtawesome as qta


from pathlib import Path

from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QVBoxLayout, QLabel, QWidget, QFrame, QHBoxLayout
from otlmow_converter.OtlmowConverter import OtlmowConverter
from otlmow_visuals.PyVisWrapper import PyVisWrapper

from GUI.ButtonWidget import ButtonWidget
from Domain import global_vars
from GUI.Screens.screen import Screen

ROOT_DIR = Path(__file__).parent

HTML_DIR = ROOT_DIR.parent.parent / 'img' / 'html'


class DataVisualisationScreen(Screen):

    def __init__(self, _):
        super().__init__()
        self.container_insert_data_screen = QVBoxLayout()
        self._ = _
        self.view = QWebEngineView()
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
        title_label = QLabel()
        title_label.setText(self._("Data visualisation"))

        html_loc = HTML_DIR / "visuals.html"
        self.view.setHtml(open(html_loc).read())
        window_layout.addWidget(self.create_button_container())
        window_layout.addWidget(self.view)
        window_layout.addWidget(self.create_color_legend())
        window_layout.addSpacing(50)
        window.setLayout(window_layout)
        return window

    @classmethod
    def create_color_legend(cls):
        relatie_color_dict = PyVisWrapper().relatie_color_dict
        frame = QFrame()
        frame_layout = QHBoxLayout()
        for relatie, color in relatie_color_dict.items():
            color_label = QLabel()
            label = QLabel()
            relatie_name = relatie.split('#')[-1]
            label.setText(relatie_name)
            color_label.setStyleSheet(f"background-color: #{color}")
            frame_layout.addWidget(color_label)
            frame_layout.addWidget(label)
        frame.setLayout(frame_layout)
        return frame


    def create_button_container(self):
        frame = QFrame()
        frame_layout = QHBoxLayout()
        refresh_btn = ButtonWidget()
        refresh_btn.setIcon(qta.icon('mdi.refresh'))
        png_creator_button = ButtonWidget()
        png_creator_button.setText(self._("create_png"))
        png_creator_button.clicked.connect(lambda: self.create_png())
        refresh_btn.clicked.connect(lambda: self.reload_html())
        frame_layout.addWidget(refresh_btn)
        frame_layout.addSpacing(10)
        frame_layout.addWidget(png_creator_button)
        frame_layout.addStretch()
        frame.setLayout(frame_layout)
        return frame

    def reset_ui(self, _):
        pass

    def reload_html(self):
        self.load_assets_and_create_html()
        # self.view.reload()

    def load_assets_and_create_html(self):
        project = global_vars.single_project
        if project is None:
            return
        valid_file_paths = [file.file_path for file in project.templates_in_memory if file.state in ['OK', 'ok']]

        objects_in_memory = []
        for path in valid_file_paths:
            objects_in_memory.extend(OtlmowConverter().create_assets_from_file(
                filepath=Path(path), path_to_subset=project.subset_path))

        html_loc = HTML_DIR / "visuals.html"
        relatie_color_dict = PyVisWrapper().relatie_color_dict
        logging.debug(f"relatie_color_dict: {relatie_color_dict}")
        PyVisWrapper().show(list_of_objects=objects_in_memory, html_path=html_loc, launch_html=False)
        self.view.setHtml(open(html_loc).read())

    @classmethod
    def create_png(cls):
        pass
