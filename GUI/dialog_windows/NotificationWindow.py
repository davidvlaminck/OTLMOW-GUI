from PyQt6.QtWidgets import QWidget, QMessageBox


class NotificationWindow(QWidget):

    def __init__(self, message:str, title:str = "notification"):
        self.message = message
        self.title = title
        super().__init__()
        self.init_ui()

    def init_ui(self):
        dlg = QMessageBox(self)
        dlg.setWindowTitle(self.title)
        dlg.setText(self.message)
        button = dlg.exec()