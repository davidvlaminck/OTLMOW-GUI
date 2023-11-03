

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QFrame


class StepperWidget(QWidget):
    def __init__(self, _):
        super().__init__()
        self._ = _
        self.step1 = QPushButton()
        self.step2 = QPushButton()
        self.step3 = QPushButton()
        self.step4 = QPushButton()

    def stepper_widget(self):
        stepper_widget = QWidget()
        horizontal_layout = QHBoxLayout()
        line_1 = QFrame()
        line_1.setFrameShape(QFrame.Shape.HLine)
        line_1.setProperty('class', 'stepper-line')
        line_2 = QFrame()
        line_2.setFrameShape(QFrame.Shape.HLine)
        line_2.setProperty('class', 'stepper-line')
        line_3 = QFrame()
        line_3.setFrameShape(QFrame.Shape.HLine)
        line_3.setProperty('class', 'stepper-line')
        self.step1.setText(self._("step1"))
        self.step2.setText(self._("step2"))
        self.step3.setText(self._("step3"))
        self.step4.setText(self._("step4"))

        horizontal_layout.addWidget(self.step1, alignment=Qt.AlignmentFlag.AlignCenter)
        horizontal_layout.addWidget(line_1)
        horizontal_layout.addWidget(self.step2, alignment=Qt.AlignmentFlag.AlignLeft)
        horizontal_layout.addWidget(line_2)
        horizontal_layout.addWidget(self.step3, alignment=Qt.AlignmentFlag.AlignLeft)
        horizontal_layout.addWidget(line_3)
        horizontal_layout.addWidget(self.step4, alignment=Qt.AlignmentFlag.AlignLeft)
        horizontal_layout.addSpacing(50)
        stepper_widget.setLayout(horizontal_layout)
        return stepper_widget

    def reset_ui(self, _):
        self._ = _
        self.step1.setText(self._("step1"))
        self.step2.setText(self._("step2"))
        self.step3.setText(self._("step3"))
        self.step4.setText(self._("step4"))
