import asyncio

from PyQt6.QtWidgets import QApplication, QDialog, QLabel, QVBoxLayout, QPushButton, QHBoxLayout
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import Qt
import sys

class LoadingImageWindow(QDialog):

    image_path = "C:\\Users\\chris\\PycharmProjects\\OTLMOW-GUI\\img\\yoda_patience.jpg"
    message = "Loading"
    title = "Loading"
    def __init__(self, parent=None, delayed_opening = False):
        super().__init__(parent)


        self.setWindowTitle(LoadingImageWindow.title)
        self.setFixedSize(625, 468)

        # Main layout
        layout = QVBoxLayout()



        # Image label
        image_label = QLabel(self)
        pixmap = QPixmap(LoadingImageWindow.image_path)
        image_label.setPixmap(pixmap)
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Text label
        text_label = QLabel(LoadingImageWindow.message, self)
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text_label.setWordWrap(True)

        font = QFont()
        font.setPointSize(32)  # Adjust font size as needed
        text_label.setFont(font)

        # Buttons layout
        # buttons_layout = QHBoxLayout()
        # ok_button = QPushButton("OK", self)
        # ok_button.clicked.connect(self.accept)
        #
        # buttons_layout.addStretch()
        # buttons_layout.addWidget(ok_button)
        # buttons_layout.addStretch()

        # Add widgets to main layout
        layout.addWidget(image_label)
        layout.addWidget(text_label)
        # layout.addLayout(buttons_layout)

        self.setLayout(layout)
        self.opening = True
        if delayed_opening:
            event_loop = asyncio.get_event_loop()
            event_loop.create_task(self.delayed_open())
        else:
            self.open()

    async def delayed_open(self):
        # only open loading window after 1 second after initialisation
        # and only if the command to close it hasn't come yet by then
        await asyncio.sleep(1)
        if self.opening:
            self.open()

    def close(self):
        self.opening = False
        if not self.isHidden():
            return super().close()
