import qtawesome as qta

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QFrame

from Domain.ProjectFileManager import ProjectFileManager
from GUI.ButtonWidget import ButtonWidget


class StepperWidget(QWidget):
    def __init__(self, _, step: int):
        super().__init__()
        self._ = _
        self.stacked_widget = None
        self.step1 = ButtonWidget()
        self.step2 = ButtonWidget()
        self.step3 = ButtonWidget()
        self.step4 = ButtonWidget()
        self.step_nr = step

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

        # sets the text for the stepper buttons and applies classes which hold the style
        self.step1.setText(self._("step1"))
        self.step1.setProperty('class', 'stepper-button')
        self.step2.setText(self._("step2"))
        self.step2.setProperty('class', 'stepper-button')
        self.step3.setText(self._("step3"))
        self.step3.setProperty('class', 'stepper-button')
        self.step4.setText(self._("step4"))
        self.step4.setProperty('class', 'stepper-button')
        # sets the icons for the stepper buttons
        if self.step_nr == 1:
            self.step1.setIcon(qta.icon('mdi.numeric-1-circle', color="#B35F35"))
        else:
            self.step1.setIcon(qta.icon('mdi.numeric-1-circle', color="grey"))
        if self.step_nr == 2:
            self.step2.setIcon(qta.icon('mdi.numeric-2-circle', color="#B35F35"))
        else:
            self.step2.setIcon(qta.icon('mdi.numeric-2-circle', color="grey"))
        if self.step_nr == 3:
            self.step3.setIcon(qta.icon('mdi.numeric-3-circle', color="#B35F35"))
        else:
            self.step3.setIcon(qta.icon('mdi.numeric-3-circle', color="grey"))
        if self.step_nr == 4:
            self.step4.setIcon(qta.icon('mdi.numeric-4-circle', color="#B35F35"))
        else:
            self.step4.setIcon(qta.icon('mdi.numeric-4-circle', color="grey"))

        horizontal_layout.addWidget(self.step1, alignment=Qt.AlignmentFlag.AlignCenter)
        self.step1.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        horizontal_layout.addWidget(line_1)
        horizontal_layout.addWidget(self.step2, alignment=Qt.AlignmentFlag.AlignLeft)
        self.step2.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))
        horizontal_layout.addWidget(line_2)
        horizontal_layout.addWidget(self.step3, alignment=Qt.AlignmentFlag.AlignLeft)
        self.step3.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(3))
        self.enable_steps()
        horizontal_layout.addWidget(line_3)
        horizontal_layout.addWidget(self.step4, alignment=Qt.AlignmentFlag.AlignLeft)
        self.step4.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(4))
        horizontal_layout.addSpacing(50)
        stepper_widget.setLayout(horizontal_layout)
        return stepper_widget

    def enable_steps(self):
        if ProjectFileManager().otl_conform_map_exists():
            self.step3.setDisabled(False)
            self.step4.setDisabled(False)
        else:
            self.step3.setDisabled(True)
            self.step4.setDisabled(True)

    def reset_ui(self, _):
        print("reset stepper")
        self._ = _
        self.step1.setText(self._("step1"))
        self.step2.setText(self._("step2"))
        self.step3.setText(self._("step3"))
        self.step4.setText(self._("step4"))
        self.enable_steps()
