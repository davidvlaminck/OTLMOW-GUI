from datetime import datetime
from PyQt6.QtWidgets import QMessageBox, QTableWidget, QWidget, QPushButton


class HomeDomain:

    def __init__(self, database, language_settings):
        self.db = database
        self._ = language_settings

    def get_amount_of_rows(self) -> int:
        return self.db.count_projects()

    def get_all_projects(self) -> list:
        return self.db.get_all_projects()

    # TODO: functie naar dialog_window.py
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
            self.remove_project(id_, table)

    def remove_project(self, id_: int, table: QTableWidget) -> None:
        self.db.remove_project(id_)
        table.removeRow(table.currentRow())

    def alter_table(self, properties: list, dlg, home_screen: QWidget, id_=None):
        time_of_alter = datetime.now()
        properties += [time_of_alter]
        project_exists = id_ is not None
        if project_exists:
            self.db.update_project(id_, properties[0], properties[1], properties[2], time_of_alter)
        else:
            id_ = self.db.add_project(properties[0], properties[1], properties[2], time_of_alter)
        home_screen.draw_table()
        dlg.close()
