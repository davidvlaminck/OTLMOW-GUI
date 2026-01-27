from PyQt6.QtWidgets import QWidget, QMessageBox


class YesOrNoOrAbortNotificationWindow(QMessageBox):

    def __init__(self, message:str, title:str = "notification"):
        self.message = message
        self.title = title
        super().__init__()

        self.setWindowTitle(self.title)
        self.setText(self.message)
        self.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Abort)