import logging

from PyQt6.QtWidgets import QStackedWidget


class Navigation(QStackedWidget):
    def __init__(self):
        super().__init__()

    def add_widget(self, widget):
        logging.debug(f'Adding {widget} to stacked widget')
        self.addWidget(widget)
        widget.stacked_widget = self
        widget.header.stacked_widget = self

    def reset_ui(self, _):
        logging.debug(f'Resetting UI in {self}')
        logging.debug(f'{self.count()} ')
        for i in range(self.count()):
            self.widget(i).reset_ui(_)