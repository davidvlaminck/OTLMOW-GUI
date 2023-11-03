from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QFrame


class StepperWidget(QWidget):
    def __init__(self, _):
        super().__init__()
        self._ = _

    def stepper_widget(self):
        stepper_widget = QWidget()
        horizontal_layout = QHBoxLayout()
        step1 = QPushButton()
        aesthetic_line = QFrame()
        aesthetic_line.setFrameShape(QFrame.Shape.HLine)
        aesthetic_line.setFrameShadow(QFrame.Shadow.Plain)
        aesthetic_line.setLineWidth(2)
        line_2 = QFrame()
        line_2.setFrameShape(QFrame.Shape.HLine)
        line_2.setFrameShadow(QFrame.Shadow.Plain)
        line_2.setLineWidth(2)
        line_3 = QFrame()
        line_3.setFrameShape(QFrame.Shape.HLine)
        line_3.setFrameShadow(QFrame.Shadow.Plain)
        step1.setText(self._("step1"))
        step2 = QPushButton()
        step2.setText(self._("step2"))
        step3 = QPushButton()
        step3.setText(self._("step3"))
        step4 = QPushButton()
        step4.setText(self._("step4"))

        horizontal_layout.addWidget(step1, alignment=Qt.AlignmentFlag.AlignCenter)
        horizontal_layout.addWidget(aesthetic_line)
        horizontal_layout.addWidget(step2, alignment=Qt.AlignmentFlag.AlignLeft)
        horizontal_layout.addWidget(line_2)
        horizontal_layout.addWidget(step3, alignment=Qt.AlignmentFlag.AlignLeft)
        horizontal_layout.addWidget(line_3)
        horizontal_layout.addWidget(step4, alignment=Qt.AlignmentFlag.AlignLeft)
        horizontal_layout.addSpacing(50)
        stepper_widget.setLayout(horizontal_layout)
        return stepper_widget

    def reset_ui(self, _):
        pass
