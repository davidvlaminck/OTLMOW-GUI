import logging

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel


class ErrorScreen(QWidget):

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        logging.debug("reached error screen")
        screen_layout = QVBoxLayout()
        title_label = QLabel()
        title_label.setText('error has caused program to crash')
        screen_layout.addWidget(title_label)
        self.setLayout(screen_layout)



