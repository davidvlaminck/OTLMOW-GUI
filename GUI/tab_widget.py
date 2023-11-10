from pathlib import Path

from PyQt6.QtWidgets import QTabWidget, QVBoxLayout

from Domain.language_settings import return_language
from GUI.Screens.screen import Screen
from GUI.header_bar import HeaderBar
from GUI.stepper import StepperWidget

ROOT_DIR = Path(__file__).parent

LANG_DIR = ROOT_DIR.parent / 'locale/'


class TableWidget(Screen):

    def __init__(self, database, widget1, description1: str, step_desc: str,widget2=None, description2: str = None):
        super().__init__()
        self._ = return_language(LANG_DIR)
        self.step_desc = step_desc
        self.tabs = QTabWidget()
        self.tab1 = widget1
        if widget2 is not None:
            self.tab2 = widget2
        self.stepper_widget = StepperWidget(self._)
        self.header = HeaderBar(database=database, language=self._)
        self.stacked_widget = None
        self.tabs.addTab(self.tab1, self._(description1))
        self.desc1 = description1
        if widget2 is not None:
            self.tabs.addTab(self.tab2, self._(description2))
            self.desc2 = description2
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.header)
        self.layout.addSpacing(10)
        self.layout.addWidget(self.stepper_widget.stepper_widget())
        self.layout.addSpacing(10)
        self.layout.addWidget(self.tabs)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.tabs.setProperty('class', 'tab-widget')

        self.init_ui()

    def init_ui(self):
        button = self.header.header_bar_detail_screen(self.step_desc)
        button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))

    def reset_ui(self, _):
        self._ = _
        self.header.reset_ui(_, self.step_desc)
        self.tabs.setTabText(0, self._(self.desc1))
        if hasattr(self, 'tab2'):
            self.tab2.reset_ui(_)
            self.tabs.setTabText(1, self._(self.desc2))
        self.tab1.reset_ui(_)
