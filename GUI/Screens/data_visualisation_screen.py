import qtawesome as qta
from pathlib import Path

from PyQt6.QtCore import QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QVBoxLayout, QLabel, QWidget

from GUI.ButtonWidget import ButtonWidget
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
