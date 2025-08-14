from PyQt6.QtWidgets import QWidget, QMessageBox


class NotificationWindow(QMessageBox):

    def __init__(self, message:str, title:str = "notification"):
        self.message = message
        self.title = title
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(self.title)
        self.setText(self.message)