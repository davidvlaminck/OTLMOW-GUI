from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QStackedWidget

from Domain.language_settings import return_language
from GUI.header_bar import HeaderBar

ROOT_DIR = Path(__file__).parent
LANG_DIR = ROOT_DIR.parent / 'locale/'


class TemplateScreen(QWidget):
    def __init__(self, database):
        super().__init__()
        self.database = database
        self._ = self._ = return_language(LANG_DIR)
        self.header = HeaderBar(self._, self.database, self)
        self.container_template_screen = QVBoxLayout()
        self.stacked_widget = QStackedWidget()

        self.init_ui()

    def init_ui(self):
        button = self.header.header_bar_detail_screen()
        button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        self.container_template_screen.addWidget(self.header)
        self.container_template_screen.addSpacing(10)
        self.container_template_screen.addWidget(self.stepper_widget())
        self.container_template_screen.addStretch()
        self.container_template_screen.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.container_template_screen)

    def stepper_widget(self):
        stepper_widget = QWidget()
        horizontal_layout = QHBoxLayout()
        step1 = QPushButton()
        step1.setText(self._("step1"))
        step2 = QPushButton()
        step2.setText(self._("step2"))
        step3 = QPushButton()
        step3.setText(self._("step3"))
        step4 = QPushButton()
        step4.setText(self._("step4"))
        step5 = QPushButton()
        step5.setText(self._("step5"))

        horizontal_layout.addWidget(step1, alignment=Qt.AlignmentFlag.AlignLeft)
        horizontal_layout.addSpacing(50)
        horizontal_layout.addWidget(step2, alignment=Qt.AlignmentFlag.AlignLeft)
        horizontal_layout.addSpacing(50)
        horizontal_layout.addWidget(step3, alignment=Qt.AlignmentFlag.AlignLeft)
        horizontal_layout.addSpacing(50)
        horizontal_layout.addWidget(step4, alignment=Qt.AlignmentFlag.AlignLeft)
        horizontal_layout.addSpacing(50)
        horizontal_layout.addWidget(step5, alignment=Qt.AlignmentFlag.AlignLeft)
        stepper_widget.setLayout(horizontal_layout)
        return stepper_widget

