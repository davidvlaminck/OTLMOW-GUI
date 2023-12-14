import qtawesome as qta
from pathlib import Path

from PyQt6.QtCore import QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QVBoxLayout, QLabel, QWidget
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
        self.init_ui()

    def init_ui(self):
        self.container_insert_data_screen.addSpacing(10)
        self.container_insert_data_screen.addWidget(self.create_html_container())
        self.setLayout(self.container_insert_data_screen)

    def create_html_container(self):
        window = QWidget()
        window.setProperty('class', 'background-box')
        window_layout = QVBoxLayout()
        title_label = QLabel()
        title_label.setText(self._("Data visualisation"))

        view = QWebEngineView()
        html_loc = HTML_DIR / "visuals.html"
        view.setHtml(open(html_loc).read())
        refresh_btn = ButtonWidget()
        refresh_btn.setIcon(qta.icon('mdi.refresh'))
        refresh_btn.clicked.connect(view.reload)
        window_layout.addWidget(view)
        window_layout.addWidget(refresh_btn)
        window.setLayout(window_layout)
        return window

    def reset_ui(self, _):
        pass

    @classmethod
    def load_assets_and_create_html(cls):
        project = global_vars.single_project
        if project is None:
            return
        valid_file_paths = [file.file_path for file in project.templates_in_memory if file.state in ['OK', 'ok']]

        objects_in_memory = []
        for path in valid_file_paths:
            objects_in_memory.extend(OtlmowConverter().create_assets_from_file(
                filepath=Path(path), path_to_subset=project.subset_path))

        html_loc = HTML_DIR / "visuals.html"
        PyVisWrapper().show(list_of_objects=objects_in_memory, html_path=html_loc, launch_html=False)
