from PyQt6.QtWidgets import QMessageBox, QTableWidget, QPushButton


class MessageBox:

    def __init__(self, language_settings, home_domain):
        self._ = language_settings
        self.home_domain = home_domain

    def draw_remove_project_screen(self, id_: int, table: QTableWidget) -> None:
        dlg = QMessageBox()
        dlg.setWindowTitle(self._("delete"))
        dlg.setText(self._("project_deletion_question"))
        dlg.setIcon(QMessageBox.Icon.Warning)
        dlg.addButton(QPushButton(self._("yes")), QMessageBox.ButtonRole.YesRole)
        dlg.addButton(QPushButton(self._("no")), QMessageBox.ButtonRole.NoRole)
        dlg.exec()
        reply = dlg.buttonRole(dlg.clickedButton())
        if reply == QMessageBox.ButtonRole.YesRole:
            self.home_domain.remove_project(id_, table)