import qtawesome as qta

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QFrame

from otlmow_gui.Domain import global_vars
from otlmow_gui.GUI.screens.general_elements.ButtonWidget import ButtonWidget


class StepperWidget(QWidget):
    def __init__(self, _, step: int):
        super().__init__()
        self._ = _
        self.main_window = None
        self.step1 = ButtonWidget()
        self.step2 = ButtonWidget()
        self.step3 = ButtonWidget()
        self.step4 = ButtonWidget()
        self.step_nr = step

    def stepper_widget(self):
        stepper_widget = QWidget()
        lines = [QFrame() for _ in range(3)]
        for line in lines:
            line.setFrameShape(QFrame.Shape.HLine)
            line.setProperty('class', 'stepper-line')

        # sets the text for the stepper buttons and applies classes which hold the style
        steps = [self.step1, self.step2, self.step3, self.step4]
        self.populate_steps(steps)
        layout = self.fill_up_layout(lines)
        stepper_widget.setLayout(layout)
        return stepper_widget

    def populate_steps(self, steps):
        for i, step in enumerate(steps, start=1):
            step.setText(self._(f"step{i}"))
            step.setProperty('class', 'stepper-button')
            color = "#B35F35" if self.step_nr == i else "grey"
            step.setIcon(qta.icon(f'mdi.numeric-{i}-circle', color=color))
            step.clicked.connect(lambda _, index=i: self.main_window.setCurrentIndex(index))

    def fill_up_layout(self, lines):
        horizontal_layout = QHBoxLayout()
        self.enable_steps()
        horizontal_layout.addWidget(self.step1, alignment=Qt.AlignmentFlag.AlignCenter)
        horizontal_layout.addWidget(lines[0])
        horizontal_layout.addWidget(self.step2, alignment=Qt.AlignmentFlag.AlignLeft)
        horizontal_layout.addWidget(lines[1])
        horizontal_layout.addWidget(self.step3, alignment=Qt.AlignmentFlag.AlignLeft)
        horizontal_layout.addWidget(lines[2])
        horizontal_layout.addWidget(self.step4, alignment=Qt.AlignmentFlag.AlignLeft)
        horizontal_layout.addSpacing(50)
        horizontal_layout.setContentsMargins(10, 0, 0, 0)
        return horizontal_layout

    def enable_steps(self):
        if (global_vars.current_project and
                global_vars.current_project.are_all_project_files_in_memory_valid()):
            self.step3.setDisabled(False)
            self.step4.setDisabled(False)
        else:
            # OTLLogger.logger.debug('set disabled')
            self.step3.setDisabled(True)
            self.step4.setDisabled(True)

    def reset_ui(self, _):
        self._ = _
        self.step1.setText(self._("step1"))
        self.step2.setText(self._("step2"))
        self.step3.setText(self._("step3"))
        self.step4.setText(self._("step4"))
        self.enable_steps()
