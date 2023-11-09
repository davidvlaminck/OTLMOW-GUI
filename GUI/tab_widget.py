from pathlib import Path

from PyQt6.QtWidgets import QWidget, QTabWidget, QVBoxLayout, QFrame

from Domain.language_settings import return_language
from GUI.Screens.conversion_screen import ConversionScreen
from GUI.Screens.export_data_screen import ExportDataScreen
from GUI.Screens.screen import Screen
from GUI.header_bar import HeaderBar
from GUI.stepper import StepperWidget

ROOT_DIR = Path(__file__).parent

LANG_DIR = ROOT_DIR.parent / 'locale/'


class TableWidget(Screen):

    def __init__(self, database):
        super().__init__()
        self._ = return_language(LANG_DIR)
        self.tabs = QTabWidget()
        self.tab1 = ExportDataScreen()
        self.tab2 = ConversionScreen()
        self.stepper_widget = StepperWidget(self._)
        self.header = HeaderBar(database=database, language=self._)
        self.stacked_widget = None
        self.tabs.addTab(self.tab1, self._('export_data'))
        self.tabs.addTab(self.tab2, self._('conversion'))
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.header)
        self.layout.addSpacing(10)
        self.layout.addWidget(self.stepper_widget.stepper_widget())
        self.layout.addSpacing(10)
        self.layout.addWidget(self.tabs)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.init_ui()

    def init_ui(self):
        button = self.header.header_bar_detail_screen('step_4')
        button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))

    def reset_ui(self, _):
        self._ = _
        self.header.reset_ui(_, 'step_4')
        self.tabs.setTabText(0, self._('export_data'))
        self.tabs.setTabText(1, self._('conversion'))
        self.tab1.reset_ui(_)
        self.tab2.reset_ui(_)
