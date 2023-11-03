from PyQt6.QtWidgets import QStackedWidget


class Navigation(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.stacked_widget = QStackedWidget()

    def add_widget(self, widget):
        self.addWidget(widget)

    def reset_ui(self, _):
        for i in range(self.stacked_widget.count()):
            self.stacked_widget.widget(i).reset_language(_)