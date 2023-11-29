from PyQt6.QtWidgets import QStackedWidget


class Navigation(QStackedWidget):
    def __init__(self):
        super().__init__()

    def add_widget(self, widget, hasStepper=False):
        self.addWidget(widget)
        widget.stacked_widget = self
        widget.header.stacked_widget = self
        if hasStepper:
            widget.stepper_widget.stacked_widget = self
            widget.tab1.stacked_widget = self
            if hasattr(widget, 'tab2'):
                widget.tab2.stacked_widget = self

    def reset_ui(self, _):
        for i in range(self.count()):
            self.widget(i).reset_ui(_)
