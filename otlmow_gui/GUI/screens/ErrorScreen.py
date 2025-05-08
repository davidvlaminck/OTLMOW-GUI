import logging

from PyQt6.QtWidgets import QWidget, QMessageBox, QDialog, QVBoxLayout, QScrollArea, QLabel, \
    QPushButton, QApplication
import pyperclip as pc


class ErrorScreen(QWidget):

    def __init__(self, error_message, operation_continued=None):
        self.error_message = error_message
        pc.copy(error_message)
        super().__init__()
        self.operation_continued = operation_continued
        self.init_ui()

    def init_ui(self):
        # Create a QDialog for the error screen
        dlg = QDialog(self)
        dlg.setWindowTitle("Unhandled Exception")

        # Set up a layout
        layout = QVBoxLayout(dlg)

        # Create a scroll area
        scroll_area = QScrollArea(dlg)
        scroll_area.setWidgetResizable(True)



        # Add a QLabel inside the scroll area to display the error message
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        error_label = QLabel(self.error_message + "\n\nError message copied to clipboard.",
                             content_widget)
        error_label.setWordWrap(True)
        # if self.operation_continued:
        #     extra_message = QLabel(self.operation_continued)
        #     extra_message.setWordWrap(True)
        #     extra_message.setStyleSheet("color: green;")
        #     content_layout.addWidget(extra_message)

        content_layout.addWidget(error_label)
        scroll_area.setWidget(content_widget)

        # Scroll down to the bottom by default
        scroll_area.verticalScrollBar().rangeChanged.connect(
            lambda: scroll_area.verticalScrollBar().setValue(
                scroll_area.verticalScrollBar().maximum())
        )

        # Add a button to close the dialog
        close_button = QPushButton("Close", dlg)
        close_button.clicked.connect(dlg.close)

        # Add scroll area and button to the layout
        layout.addWidget(scroll_area)
        layout.addWidget(close_button)

        # Set the dialog size to half the screen size
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        dlg.resize(int(screen_geometry.width()*(2/3)), int(screen_geometry.height()*(2/3)))

        # Show the dialog
        dlg.exec()